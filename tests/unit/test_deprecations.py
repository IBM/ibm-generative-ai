import warnings

import pytest
from pydantic import BaseModel

from genai.schema import (
    ModerationHAP,
    ModerationImplicitHate,
    ModerationStigma,
)


class TestCase(BaseModel):
    input: dict
    output: dict
    warnings_count: int


@pytest.mark.unit
@pytest.mark.parametrize("cls", [ModerationHAP, ModerationStigma, ModerationImplicitHate])
@pytest.mark.parametrize(
    "case",
    [
        TestCase(
            input={"input": True},
            output={"input": {"enabled": True, "send_tokens": False, "threshold": 0.75}},
            warnings_count=1,
        ),
        TestCase(
            input={"input": True, "output": False},
            output={
                "input": {"enabled": True, "send_tokens": False, "threshold": 0.75},
                "output": {"enabled": False, "send_tokens": False, "threshold": 0.75},
            },
            warnings_count=2,
        ),
        TestCase(
            input={"input": True, "output": None},
            output={"input": {"enabled": True, "send_tokens": False, "threshold": 0.75}},
            warnings_count=1,
        ),
        TestCase(
            input={"input": True, "threshold": 0.5, "output": False},
            output={
                "input": {"enabled": True, "send_tokens": False, "threshold": 0.5},
                "output": {"enabled": False, "send_tokens": False, "threshold": 0.5},
            },
            warnings_count=3,
        ),
        TestCase(
            input={"input": False, "output": False},
            output={
                "input": {"enabled": False, "send_tokens": False, "threshold": 0.75},
                "output": {"enabled": False, "send_tokens": False, "threshold": 0.75},
            },
            warnings_count=2,
        ),
        TestCase(
            input={"threshold": 0.1},
            output={
                "input": {"enabled": True, "send_tokens": False, "threshold": 0.1},
                "output": {"enabled": True, "send_tokens": False, "threshold": 0.1},
            },
            warnings_count=1,
        ),
        TestCase(
            input={"threshold": 0.25, "send_tokens": True},
            output={
                "input": {"enabled": True, "send_tokens": True, "threshold": 0.25},
                "output": {"enabled": True, "send_tokens": True, "threshold": 0.25},
            },
            warnings_count=2,
        ),
        TestCase(
            input={"threshold": 0.25, "input": False, "send_tokens": True},
            output={
                "input": {"enabled": False, "send_tokens": True, "threshold": 0.25},
                "output": {"enabled": True, "send_tokens": True, "threshold": 0.25},
            },
            warnings_count=3,
        ),
        TestCase(input={"input": None, "output": None}, output={}, warnings_count=0),
        TestCase(input={}, output={}, warnings_count=0),
    ],
)
def test_deprecated_moderations(cls: type[BaseModel], case: TestCase) -> None:
    with warnings.catch_warnings(record=True) as warning_log:
        assert not warning_log
        expected = cls(**case.output)
        assert not warning_log

        current = cls(**case.input)
        assert len(warning_log) == case.warnings_count

        assert current == expected
