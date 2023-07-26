def sanitize_params(params):
    if params is not None:
        if type(params) is not dict:
            params = params.model_dump(by_alias=True, exclude_none=True)
    return params
