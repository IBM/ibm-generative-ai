"""Wrapper around IBM GENAI APIs for use in langchain"""
import logging
import re

try:
    from langchain import PromptTemplate
except ImportError:
    raise ImportError("Could not import langchain: Please install ibm-generative-ai[langchain] extension.")

from genai.prompt_pattern import PromptPattern
from genai.utils.extensions import register_promptpattern_accessor

logger = logging.getLogger(__name__)

__all__ = ["PromptExtension"]


@register_promptpattern_accessor("langchain")
class PromptExtension:
    def __init__(self, prompt_pattern: PromptPattern):
        self._obj = prompt_pattern

    def as_template(self):
        """Convert genai PromptPattern to langchain PromptTemplate.
        Args:
            pattern (PromptPattern): An instance of genai prompt pattern.
        Returns:
            PromptTemplate: An instance of langchain PromptTemplate.
        """
        s = self._obj.dump
        vars = list(self._obj.find_vars())
        for var in vars:
            s = re.sub(r"{{\s*" + var + r"\s*}}", r"{" + var + r"}", s)
        return PromptTemplate(input_variables=vars, template=s)

    @staticmethod
    def from_template(template: PromptTemplate):
        """Convert langchain PromptTemplate to genai PromptPatterm.
        Args:
            template (PromptTemplate): An instance of langchain PromptTemplate.
        Returns:
            PromptPattern: An instance of genai prompt pattern.
        """
        s = template.template
        for var in template.input_variables:
            s = re.sub("{" + var + "}", "{{" + var + "}}", s)
        return PromptPattern.from_str(s)
