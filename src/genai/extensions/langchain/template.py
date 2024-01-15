import re

__all__ = ["to_langchain_template", "from_langchain_template"]


def to_langchain_template(template: str) -> str:
    """Convert mustache template variables to langchain template variables"""
    return re.sub(r"{{([^}]+)}}", r"{\1}", template, count=0, flags=re.MULTILINE)


def from_langchain_template(template: str) -> str:
    """Convert langchain template variables to mustache template variables"""
    return re.sub(r"{([^}]+)}", r"{{\1}}", template, count=0, flags=re.MULTILINE)
