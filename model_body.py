import pandas as pd


def evaluate_model(coefficients, input_data):
    """
    coefficients: dict of {variable_name: factor}
    input_data: pd DataFrame with the variables and dt column

    returns: predicted value by dt column with dummy model
    """
    assert isinstance(coefficients, dict)
    assert all(name in input_data.columns for name in coefficients)
    assert 'dt' in input_data.columns

    input_data['prediction'] = (
        input_data[list(coefficients.keys())]
        .apply(lambda x: x * coefficients[x.name])
        .sum(axis=1)
    )
    return input_data[['dt', 'prediction']]