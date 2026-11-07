from fastapi import APIRouter, HTTPException, Query

from app.schemas.test_case import GenerationResponse
from app.services.openapi_parser import OpenAPIParseError
from app.services.test_case_generator import generate_test_cases

router = APIRouter(tags=["test-cases"])


@router.post(
    "/test-cases/generate",
    response_model=GenerationResponse,
    summary="Generate test cases from an OpenAPI JSON document",
)
def generate(
    specification: dict,
    include_positive: bool = Query(default=True),
    include_negative: bool = Query(default=True),
    include_boundary: bool = Query(default=True),
) -> GenerationResponse:
    try:
        cases, operations_count, warnings = generate_test_cases(
            specification=specification,
            include_positive=include_positive,
            include_negative=include_negative,
            include_boundary=include_boundary,
        )
        return GenerationResponse(
            specification_title=specification.get("info", {}).get("title", "Untitled API"),
            operations_count=operations_count,
            generated_count=len(cases),
            test_cases=cases,
            warnings=warnings,
        )
    except OpenAPIParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
