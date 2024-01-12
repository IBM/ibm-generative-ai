from datamodel_code_generator.format import CustomCodeFormatter


class CodeFormatter(CustomCodeFormatter):
    """
    Make modifications to generated model.
    1. Remove unused 'ConfigDict' import
    2. Remove source filename info
    """

    def apply(self, code: str) -> str:
        return (
            code.replace("from pydantic import ConfigDict\n", "")
            .replace(" ConfigDict,", "")
            .replace("ConfigDict,", "")
            .replace(", ConfigDict", "")
        )
