import re

from datamodel_code_generator.format import CustomCodeFormatter

from types_generator.config import ExtractorConfig


class CodeFormatter(CustomCodeFormatter):
    """
    Make modifications to generated model.
    1. Remove unused 'ConfigDict' import
    2. Remove source filename info
    3. Fix private class names starting with underscore _
    4. Make all Query and Request classes generated from operation ID private
    5. Add __all__ to export all local non-imported symbols for better documentation
    """

    def apply(self, code: str) -> str:
        code = (
            code.replace("from pydantic import ConfigDict\n", "")
            .replace(" ConfigDict,", "")
            .replace("ConfigDict,", "")
            .replace(", ConfigDict", "")
        )

        # datamodel-codegen cannot generate classname with underscore, because class name resolver contains this code:
        #
        #   # We should avoid having a field begin with an underscore, as it
        #   # causes pydantic to consider it as private
        #   while name.startswith('_'):

        code = code.replace(ExtractorConfig.private_field_name, "_")

        # We want to hide Query and Request classes generated from operation_id
        code = re.sub(rf"\nclass ({ExtractorConfig.operation_id_prefix}\S+(Query|Request)\()", "\nclass _\\1", code)
        code = code.replace(ExtractorConfig.operation_id_prefix, "")

        generated__all__ = "__all__=" + str(sorted(re.findall(r"class ([^_][A-Za-z0-9_]+)\(.*\):", code)))

        # Add __all__
        code = f"{code}\n{generated__all__}"
        return code
