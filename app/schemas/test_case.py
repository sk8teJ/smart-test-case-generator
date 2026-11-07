from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TestStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    expected_result: str


class TestCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    method: str
    path: str
    category: Literal["positive", "negative", "boundary"]
    priority: Literal["low", "medium", "high"] = "medium"
    source: Literal["rules", "ai"] = "rules"
    input_data: dict[str, Any] = Field(default_factory=dict)
    expected_status: int | None = None
    steps: list[TestStep] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class GenerationResponse(BaseModel):
    specification_title: str
    operations_count: int
    generated_count: int
    test_cases: list[TestCase]
    warnings: list[str] = Field(default_factory=list)

    @classmethod
    def model_validate_with_count(cls, **data: Any) -> "GenerationResponse":
        data["generated_count"] = len(data.get("test_cases", []))
        return cls.model_validate(data)
