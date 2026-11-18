from app.services.test_case_generator import generate_test_cases


def test_generates_negative_case_when_request_body_is_required():
    specification = {
        "openapi": "3.1.0",
        "info": {"title": "Example API", "version": "1.0.0"},
        "paths": {
            "/items": {
                "post": {
                    "operationId": "createItem",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"name": {"type": "string"}},
                                    "required": ["name"],
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "Created"}},
                }
            }
        },
    }

    cases, operation_count, warnings = generate_test_cases(
        specification,
        include_positive=True,
        include_negative=True,
        include_boundary=False,
    )

    missing_body_cases = [
        case for case in cases
        if case.category == "negative" and "missing required request body" in case.name
    ]

    assert operation_count == 1
    assert not warnings
    assert len(missing_body_cases) == 1
    assert missing_body_cases[0].input_data == {"omit_body": True}
    assert missing_body_cases[0].expected_status is None
