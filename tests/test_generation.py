import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
SPEC_PATH = Path(__file__).parents[1] / "examples" / "petstore.json"
SPEC = json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_generate_cases_from_valid_spec():
    response = client.post("/api/v1/test-cases/generate", json=SPEC)
    assert response.status_code == 200
    payload = response.json()
    assert payload["operations_count"] == 3
    assert payload["generated_count"] == len(payload["test_cases"])
    assert payload["generated_count"] > 0
    assert {case["category"] for case in payload["test_cases"]} >= {"positive", "negative", "boundary"}


def test_rejects_unsupported_openapi_version():
    invalid = {**SPEC, "openapi": "2.0"}
    response = client.post("/api/v1/test-cases/generate", json=invalid)
    assert response.status_code == 422


def test_can_disable_negative_cases():
    response = client.post("/api/v1/test-cases/generate?include_negative=false", json=SPEC)
    assert response.status_code == 200
    assert all(case["category"] != "negative" for case in response.json()["test_cases"])


def test_rejects_missing_paths():
    invalid = {"openapi": "3.0.3", "info": {"title": "Broken", "version": "1"}}
    response = client.post("/api/v1/test-cases/generate", json=invalid)
    assert response.status_code == 422
