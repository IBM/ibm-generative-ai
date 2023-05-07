import json


def json_load(file):
    """
    Loads json or jsonl data from a file

    Args:
        file (IO) : The json or jsonl file

    Returns:
        data : Python dictionary
    """
    if file.name.endswith(".jsonl"):
        data = [json.loads(line) for line in file]
    else:
        data = json.load(file)
    return data


def json_extract(obj, key, join: bool = False):
    """
    Extract nested values from a JSON tree.

    Args:
        obj : JSON tree where we are looking for the key
        key (string): The kwy we are looking for

    Returns:
        string | list : Values for the given key. Can be returned as string or list of string
    """
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return "".join(values) if join else values


def json_get_all_keys(obj, join: bool = False):
    arr = []

    def extract_keys(obj, arr):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract_keys(v, arr)
                else:
                    arr.append(k)
        elif isinstance(obj, list):
            for item in obj:
                extract_keys(item, arr)
        return arr

    keys = extract_keys(obj, arr)
    return "".join(keys) if join else keys
