from typing import Any

from app.schemas.test_case import TestCase, TestStep
from app.services.openapi_parser import parse_openapi


def _example_for_schema(schema: Any) -> Any:
    if not isinstance(schema, dict):
        return "example"
    if "example" in schema:
        return schema["example"]
    if "default" in schema:
        return schema["default"]
    if "enum" in schema and schema["enum"]:
        return schema["enum"][0]
    kind = schema.get("type")
    if kind == "string":
        fmt = schema.get("format")
        return {"email": "qa@example.com", "date": "2026-01-01", "date-time": "2026-01-01T10:00:00Z"}.get(fmt, "sample")
    if kind in ("integer", "number"):
        return schema.get("minimum", 1)
    if kind == "boolean":
        return True
    if kind == "array":
        return [_example_for_schema(schema.get("items", {}))]
    if kind == "object" or "properties" in schema:
        return {
            name: _example_for_schema(prop)
            for name, prop in schema.get("properties", {}).items()
        }
    return "example"


def _invalid_value(schema: dict[str, Any]) -> Any:
    kind = schema.get("type")
    if kind in ("integer", "number"):
        return "not-a-number"
    if kind == "boolean":
        return "not-a-boolean"
    if kind == "array":
        return "not-an-array"
    if kind == "object":
        return "not-an-object"
    return 12345


def _case(
    operation: dict[str, Any],
    suffix: str,
    category: str,
    description: str,
    input_data: dict[str, Any],
    expected_status: int | None,
    priority: str = "medium",
) -> TestCase:
    case_id = f"TC-{len(suffix):02d}-{abs(hash((operation['operation_id'], suffix))) % 100000:05d}"
    return TestCase(
        id=case_id,
        name=f"{operation['method']} {operation['path']} — {suffix}",
        description=description,
        method=operation["method"],
        path=operation["path"],
        category=category,
        priority=priority,
        input_data=input_data,
        expected_status=expected_status,
        steps=[
            TestStep(action=f"Send {operation['method']} request to {operation['path']}", expected_result=f"Receive HTTP {expected_status}" if expected_status else "Receive a response matching the documented contract")
        ],
        tags=[operation["method"].lower(), category],
    )


def _parameter_cases(operation: dict[str, Any], include_negative: bool, include_boundary: bool) -> list[TestCase]:
    cases: list[TestCase] = []
    for parameter in operation["parameters"]:
        name = parameter.get("name", "parameter")
        location = parameter.get("in", "query")
        schema = parameter.get("schema", {})
        if not isinstance(schema, dict):
            schema = {}
        value = _example_for_schema(schema)
        if parameter.get("required") or location == "path":
            cases.append(_case(
                operation, f"valid {location} parameter '{name}'", "positive",
                f"Verify the operation accepts a valid {location} parameter.",
                {"parameters": {location: {name: value}}}, operation["success_status"], "high",
            ))
        if include_negative and parameter.get("required"):
            cases.append(_case(
                operation, f"missing required {location} parameter '{name}'", "negative",
                f"Verify the API rejects a request when required parameter '{name}' is omitted.",
                {"parameters": {location: {name: None}}, "omit_parameter": name},
                400, "high",
            ))
        if include_negative:
            cases.append(_case(
                operation, f"invalid type for parameter '{name}'", "negative",
                f"Verify validation rejects a value with an incompatible type for '{name}'.",
                {"parameters": {location: {name: _invalid_value(schema)}}}, 400,
            ))
        if include_boundary:
            if "minimum" in schema:
                boundary = schema["minimum"]
                cases.append(_case(operation, f"minimum boundary for '{name}'", "boundary",
                    f"Verify the inclusive minimum value for '{name}'.",
                    {"parameters": {location: {name: boundary}}}, operation["success_status"]))
            if "maximum" in schema:
                boundary = schema["maximum"]
                cases.append(_case(operation, f"maximum boundary for '{name}'", "boundary",
                    f"Verify the inclusive maximum value for '{name}'.",
                    {"parameters": {location: {name: boundary}}}, operation["success_status"]))
            if "minLength" in schema:
                cases.append(_case(operation, f"minimum length for '{name}'", "boundary",
                    f"Verify the minimum allowed string length for '{name}'.",
                    {"parameters": {location: {name: "x" * schema["minLength"]}},
                    operation["success_status"]))
            if "maxLength" in schema:
                cases.append(_case(operation, f"maximum length for '{name}'", "boundary",
                    f"Verify the maximum allowed string length for '{name}'.",
                    {"parameters": {location: {name: "x" * schema["maxLength"]}},
                    operation["success_status"]))
    return cases


def _body_cases(operation: dict[str, Any], include_negative: bool, include_boundary: bool) -> list[TestCase]:
    schema = operation.get("request_schema")
    if not isinstance(schema, dict):
        return []
    body = _example_for_schema(schema)
    cases = [_case(operation, "valid request body", "positive",
        "Verify the operation accepts a request body that follows the declared schema.",
        {"body": body}, operation["success_status"], "high")]
    if include_negative and schema.get("type") == "object":
        for required in schema.get("required", []):
            properties = schema.get("properties", {})
            partial = {name: _example_for_schema(prop) for name, prop in properties.items() if name != required}
            cases.append(_case(operation, f"missing required body field '{required}'", "negative",
                f"Verify the API rejects a body without required field '{required}'.",
                {"body": partial}, 422))
        for name, prop in schema.get("properties", {}).items():
            if isinstance(prop, dict):
                cases.append(_case(operation, f"invalid type for body field '{name}'", "negative",
                    f"Verify the API rejects an incompatible value for body field '{name}'.",
                    {"body": {**body, name: _invalid_value(prop)}}, 422))
    if include_boundary and schema.get("type") == "object":
        for name, prop in schema.get("properties", {}).items():
            if not isinstance(prop, dict):
                continue
            for constraint in ("minimum", "maximum", "minLength", "maxLength"):
                if constraint not in prop:
                    continue
                value = prop[constraint]
                if constraint.endswith("Length"):
                    value = "x" * value
                boundary_body = {**body, name: value}
                cases.append(_case(operation, f"{constraint} boundary for body field '{name}'", "boundary",
                    f"Verify the {constraint} constraint for body field '{name}'.",
                    {"body": boundary_body}, operation["success_status"]))
    return cases


def generate_test_cases(
    specification: dict[str, Any],
    include_positive: bool = True,
    include_negative: bool = True,
    include_boundary: bool = True,
) -> tuple[list[TestCase], int, list[str]]:
    operations, warnings = parse_openapi(specification)
    cases: list[TestCase] = []
    for operation in operations:
        generated = _parameter_cases(operation, include_negative, include_boundary)
        generated.extend(_body_cases(operation, include_negative, include_boundary))
        if include_positive:
            has_positive = any(case.category == "positive" for case in generated)
            if not has_positive:
                generated.append(_case(operation, "basic successful request", "positive",
                    "Verify the operation can be called with the documented path and no additional invalid input.",
                    {}, operation["success_status"], "high"))
        cases.extend(case for case in generated if (
            (include_positive or case.category != "positive")
            and (include_negative or case.category != "negative")
            and (include_boundary or case.category != "boundary")
        ))
    return cases, len(operations), warnings
