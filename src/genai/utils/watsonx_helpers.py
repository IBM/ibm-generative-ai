def watsonx_payload(template, data=None, files=None):
    _dict = {}
    _dict["data"] = {}

    try:
        _dict["id"] = template.watsonx.id

        if data:
            _dict["data"] = data

        if files:
            _dict["data"]["example_file_ids"] = files

        return _dict

    except Exception as e:
        print(e)
