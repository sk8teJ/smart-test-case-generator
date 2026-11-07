from typing import Any


class OpenAPIParseError(ValueError):
    """Raised when an OpenAPI document is missing required structure."""


SUPPORTED_VERSIONS = ("3.0.", "3.1.")


def _resolve_local_ref(document: dict[str, Any], schema: Any) -> Any:
    if not isinstance(schema, dict):
        return schema
    ref = schema.get("$ref")
    if not ref:
        return schema
    if not ref.startswith("#/"):
        return {"type": "object", "description": f"External reference not resolved: {ref}"}
    current: Any = document
    try:
        for part in ref[2:].split("/"):
            current = current[part.replace("~1", "/").replace("~0", "~")]
    except (KeyError, TypeError):
        return {"type": "object", "description": f"Unresolved reference: {ref}"}
    return current if isinstance(current, dict) else schema


def _merge_parameters(document: dict[str, Any], path_parameters: list, operation_parameters: list) -> list:
    merged: dict[tuple[str, str], dict] = {}
    for parameter in [*(path_parameters or []), *(operation_parameters or [])]:
        resolved = _resolve_local_ref(document, parameter)
        if not isinstance(resolved, dict):
            continue
        key = (str(resolved.get("name", "")), str(resolved.get("in", "")))
        if key != ("", ""):
            merged[key] = resolved
    return list(merged.values())


def parse_openapi(document: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(document, dict):
        raise OpenAPIParseError("The request body must be a JSON object.")
    version = document.get("openapi")
    if not isinstance(version, str) or not version.startswith(SUPPORTED_VERSIONS):
        raise OpenAPIParseError("Only OpenAPI 3.0.x and 3.1.x specifications are supported.")
    if not isinstance(document.get("paths"), dict):
        raise OpenAPIParseError("The specification must contain a 'paths' object.")
    if not isinstance(document.get("info"), dict):
        raise OpenAPIParseError("The specification must contain an 'info' object.")

    operations: list[dict[str, Any]] = []
    warnings: list[str] = []
    methods = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}

    for path, path_item in document["paths"].items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in methods or not isinstance(operation, dict):
                continue
            parameters = _merge_parameters(
                document,
                path_item.get("parameters", []),
                operation.get("parameters", []),
            )
            request_schema = None
            request_body = operation.get("requestBody", {})
            request_body = _resolve_local_ref(document, request_body)
            if isinstance(request_body, dict):
                content = request_body.get("content", {})
                for media_type in ("application/json", "application/*+json", "*/*"):
                    media = content.get(media_type)
                    if isinstance(media, dict):
                        request_schema = _resolve_local_ref(document, media.get("schema"))
                        break
                if request_schema is None and content:
                    first_media = next(iter(content.values()))
                    if isinstance(first_media, dict):
                        request_schema = _resolve_local_ref(document, first_media.get("schema"))

            responses = operation.get("responses", {})
            success_status = next(
                (int(code) for code in responses if str(code).isdigit() and 200 <= int(code) < 300),
                200,
            )
            operations.append({
                "operation_id": operation.get("operationId", f"{method.lower()}_{path.strip('/').replace('/', '_') or 'root'}"),
                "method": method.upper(),
                "path": path,
                "summary": operation.get("summary") or operation.get("description") or f"{method.upper()} {path}",
                "parameters": parameters,
                "request_schema": request_schema,
                "responses": responses,
                "success_status": success_status,
            })

    if not operations:
        warnings.append("No supported HTTP operations were found in the specification.")
    return operations, warnings
