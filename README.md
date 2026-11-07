# Smart Test Case Generator

A backend tool that analyzes OpenAPI 3.x specifications and generates structured API test cases. Deterministic rules are the source of truth; an optional Gemini integration can be added as a separate enhancement.

## Current MVP

- Parse and validate OpenAPI 3.0/3.1 JSON specifications.
- Discover API operations, parameters, request-body schemas and response codes.
- Generate positive, negative and boundary-value test cases.
- Validate generated cases against a Pydantic model.
- Export generated scenarios as JSON.
- Expose an interactive Swagger UI through FastAPI.
- Run automated tests with pytest.

## Quick start (local)

Requirements: Python 3.12+.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

## Quick start (Docker)

```bash
docker compose up --build
```

## API

### Generate test cases

```http
POST /api/v1/test-cases/generate
Content-Type: application/json
```

Send an OpenAPI document as the JSON request body. Optional query parameters:

- `include_positive` (default: true)
- `include_negative` (default: true)
- `include_boundary` (default: true)

### Health

```http
GET /health
```

### Example

A sample specification is available at `examples/petstore.yaml`. The API currently accepts JSON; YAML upload support is planned for the next milestone.

## Development

```bash
pytest -q
```

## Architecture

```text
OpenAPI JSON
    |
    v
FastAPI endpoint
    |
    v
OpenAPI parser -----> operation / schema metadata
    |
    v
Rule-based test generator
    |
    v
Pydantic validation
    |
    v
JSON test-case response
```

## Roadmap

1. [x] Initial FastAPI application and rule-based generator.
2. [ ] YAML file upload, richer schema resolution and reusable components.
3. [ ] Optional Gemini-generated scenarios with strict validation.
4. [ ] pytest export and execution against a target API.
5. [ ] UI, persistence, reports and CI improvements.

## Scope and limitations

The first version generates test scenarios from the contract. It does not yet execute requests against a live API, infer undocumented business rules, or guarantee that every generated expected response is correct. Scenarios are suggestions derived from declared OpenAPI constraints and should be reviewed before use.

## License

MIT
