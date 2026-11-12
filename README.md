# Smart Test Case Generator

**A REST API test case generator based on OpenAPI 3.x specifications.**

This project analyzes an API contract provided as JSON and automatically generates structured test scenarios: positive, negative, and boundary cases. Generation is rule-based, and the resulting scenarios are validated with Pydantic models.

This is an educational MVP demonstrating an approach to automating API test preparation. It helps create an initial set of test cases faster, but does not replace review by a QA engineer.

## Features

- **OpenAPI 3.0 and 3.1 parsing:** validates the specification structure and extracts declared HTTP operations.
- **Parameter analysis:** processes path, query, and other declared parameters, including required status and types.
- **Request body analysis:** extracts JSON request body schemas and uses declared constraints.
- **Positive scenarios:** generates valid request examples based on the schema.
- **Negative scenarios:** checks missing required parameters and fields, as well as values with incompatible types.
- **Boundary scenarios:** checks constraints such as `minimum`, `maximum`, `minLength`, and `maxLength`, when declared in the specification.
- **Result validation:** validates generated test case structures with Pydantic.
- **JSON output:** the API returns structured results that can be used by other testing tools.
- **API documentation:** interactive Swagger UI and ReDoc powered by FastAPI.
- **Automated tests:** the project uses pytest.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12+ | Main programming language |
| FastAPI | HTTP API and request handling |
| Pydantic | Data models and result validation |
| OpenAPI 3.x | Input specification format |
| pytest | Automated testing |
| httpx | HTTP client for tests |
| Docker / Docker Compose | Containerization and project startup |

## How It Works

1. The client submits an OpenAPI specification as a JSON document.
2. FastAPI receives the request and passes the document to the parser.
3. The parser checks the required document structure and extracts HTTP operations, parameters, request body schemas, and successful response codes.
4. The generator creates positive, negative, and boundary scenarios based on the extracted constraints.
5. Pydantic validates the generated test case structures.
6. The API returns the number of detected operations, the number of generated scenarios, the test cases, and parser warnings.

### Architecture

```text
                 OpenAPI JSON
                      |
                      v
                FastAPI endpoint
                      |
                      v
                OpenAPI parser
                      |
          +-----------+-----------+
          |                       |
          v                       v
   HTTP operations          Schema metadata
   and parameters           and constraints
          |                       |
          +-----------+-----------+
                      |
                      v
             Rule-based generator
                      |
                      v
              Pydantic validation
                      |
                      v
              JSON API response
          (test cases + warnings)
```

## Quick Start

### Requirements

- Python 3.12 or newer
- Git, to clone the repository
- Docker and Docker Compose, only if you want to run the project in a container

### Windows (PowerShell)

Clone the repository and navigate to the project directory:

```powershell
git clone https://github.com/sk8teJ/smart-test-case-generator.git
cd smart-test-case-generator
```

Create a virtual environment and install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the application:

```powershell
uvicorn app.main:app --reload
```

### Linux / macOS

```bash
git clone https://github.com/sk8teJ/smart-test-case-generator.git
cd smart-test-case-generator

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

uvicorn app.main:app --reload
```

After startup, the application is available at:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

### Run with Docker Compose

From the project root, run:

```bash
docker compose up --build
```

After the image is built, the API will be available on port `8000`.

## API

### Generate Test Cases

`POST /api/v1/test-cases/generate`

The request body must contain an OpenAPI 3.0.x or 3.1.x specification as a JSON object.

Header:

```http
Content-Type: application/json
```

Optional query parameters:

| Parameter | Default | Description |
|---|---:|---|
| `include_positive` | `true` | Include positive scenarios |
| `include_negative` | `true` | Include negative scenarios |
| `include_boundary` | `true` | Include boundary scenarios |

Example using curl:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/test-cases/generate?include_positive=true&include_negative=true&include_boundary=true" \
  -H "Content-Type: application/json" \
  --data-binary @examples/petstore.json
```

> The repository also contains an example specification at `examples/petstore.yaml`. The current endpoint accepts JSON request bodies; direct YAML file upload is not implemented yet.

### Application Health Check

`GET /health`

Returns the application status and can be used for a basic availability check.

## Testing

Run the automated tests from the project root:

```bash
pytest -q
```

## Project Structure

Main application components:

- `app/main.py` — creates the FastAPI application and registers routes.
- `app/api/routes/` — HTTP routes for test case generation and health checks.
- `app/core/config.py` — application configuration.
- `app/services/openapi_parser.py` — OpenAPI specification parser.
- `app/services/test_case_generator.py` — rule-based test scenario generation.
- `app/schemas/` — Pydantic response and test case models.
- `examples/` — API specification examples.
- `tests/` — automated tests.

## Current Limitations

Please keep the scope of this MVP in mind:

- The generator accepts OpenAPI 3.0.x and 3.1.x specifications as JSON.
- Direct YAML upload is not supported yet, despite the YAML example in the repository.
- Generation relies on parameters and constraints explicitly described in the contract. Undocumented business rules are not inferred.
- External `$ref` references are not fetched from the network; local reference resolution is limited to the current document.
- The service generates scenarios but does not send requests to the target API or execute tests.
- Expected HTTP status codes in generated scenarios are assumptions based on the contract and generation rules. They should be checked against the actual API behavior.
- Generated test cases should be reviewed and edited when necessary before use.

## Roadmap

- Add YAML specification upload.
- Improve support for complex schemas and reusable OpenAPI components.
- Add more scenario types and improve test coverage.
- Export test cases to formats supported by test management tools.
- Execute generated checks against a target API.
- Expand reporting and add a user interface.
- Experiment with LLM-assisted suggestions for additional scenarios, followed by mandatory validation.

## Project Purpose

This project is a practical exercise in automating API testing tasks. It combines structured data processing, REST API development, backend design, test scenario generation, and result validation.

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.
