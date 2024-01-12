from pydantic import BaseModel

from types_generator.schema_transformer import http_method_mapper, path_to_schema_name, to_classname

Schema = dict


class ApiEndpoint(BaseModel):
    path: str
    method: str
    version: str
    class_name: str


def extract_endpoints(api: Schema):
    endpoints: list[ApiEndpoint] = []

    for path, http_methods in sorted(api.get("paths", {}).items()):
        path_formatted = path_to_schema_name(path, delimiter="_")

        for http_method_raw, properties in sorted(http_methods.items()):
            assert isinstance(properties, dict)

            http_method = http_method_mapper[http_method_raw]
            assert http_method

            for value in list(properties.get("parameters", [])):
                assert isinstance(value, dict)
                if value.get("in") == "query" and value.get("name") == "version":
                    endpoints.append(
                        ApiEndpoint(
                            class_name=to_classname(f"{path_formatted}_{http_method.title()}_endpoint"),
                            path=path,
                            method=str(http_method_raw).upper(),
                            version=value.get("schema", {}).get("enum")[0],
                        )
                    )
                    break
            else:
                raise Exception(f"No query parameter was found for {http_method_raw}: {path}")

    return endpoints
