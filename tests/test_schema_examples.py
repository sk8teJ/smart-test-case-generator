import pytest

from app.services.test_case_generator import _example_for_schema


def test_integer_example_respects_zero_maximum():
    assert _example_for_schema({"type": "integer", "maximum": 0}) == 0


def test_integer_example_rounds_fractional_minimum_up():
    assert _example_for_schema({"type": "integer", "minimum": 1.5}) == 2


def test_number_example_uses_maximum_when_default_would_be_invalid():
    assert _example_for_schema({"type": "number", "maximum": 0.25}) == 0.25


def test_number_example_supports_negative_maximum():
    assert _example_for_schema({"type": "number", "maximum": -2.5}) == -2.5
