import pandas as pd
from collections import namedtuple

Variable = namedtuple('Variable', 'name factor')


def evaluate_model(dependent_variables_list, input_data):
    """
    dependent_variables_list: list of 'Variable' named tuples
    input_data: pd DataFrame with the variables and dt column

    returns: predicted value by dt column with dummy model
    """
    assert type(dependent_variables_list) == list
    assert all([type(v) == Variable for v in dependent_variables_list])
    assert all([v.name in input_data.columns for v in dependent_variables_list])
    assert 'dt' in input_data.columns

    factor_map = {v.name: v.factor for v in dependent_variables_list}
    input_data['prediction'] = (
        input_data[list(factor_map.keys())]
        .apply(lambda x: x * factor_map[x.name])
        .sum(axis=1)
    )
    return input_data[['dt', 'prediction']]