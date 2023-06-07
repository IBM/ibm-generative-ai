from itertools import product

from genai.schemas import GenerateParams


def grid_search_generate_params(params_space: dict[str, list]) -> list[GenerateParams]:
    """
    Generate all combinations of parameters from a dictionary of lists

    Args:
        params_space (dict[str, list]): dictionary of params as lists

    Returns:
        list of GenerateParams
    """
    params_values = list(product(*params_space.values()))
    params_list = []
    for values in params_values:
        params = GenerateParams(**dict(zip(params_space.keys(), values)))
        params_list.append(params)
    return params_list
