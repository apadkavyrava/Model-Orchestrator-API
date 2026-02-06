import pandas as pd


def parse_model_config(filepath: str) -> dict:
    """
    Parses a model CSV file and extracts:
    - model_name: the independent variable (e.g. 'model_3_output')
    - coefficients: dict of {dep_var: factor} for all '~' relations
    - bau: the baseline constant from the 'bau' relation row

    Example return:
    {
        "model_name": "model_3_output",
        "coefficients": {
            "variable-1": 0.21,
            "variable-2": 0.59,
            ...
        },
        "bau": 0.21
    }
    """

    df = pd.read_csv(filepath, index_col=0)

    # Extract model name
    model_name = df["independent-variable"].iloc[0]

    # Extract coefficients from '~' rows
    mask_coeff = df["relation"] == "~"
    coefficients = dict(zip(df.loc[mask_coeff, "dep-var"], df.loc[mask_coeff, "factor"]))

    # Extract bau from 'bau' row
    mask_bau = df["relation"] == "bau"
    if mask_bau.any():
        bau = df.loc[mask_bau, "factor"].iloc[0]
    else:
        bau = 0.0

    config = {
        "model_name": model_name,
        "coefficients": coefficients,
        "bau": bau,
    }

    # Print summary
    print(f"\n  Parsed: {filepath}")
    print(f"  Model:  {model_name}")
    print(f"  Terms:  {len(coefficients)}")
    for var, coef in coefficients.items():
        print(f"          {coef} × {var}")
    print(f"  BAU:    {bau}")

    return config


if __name__ == "__main__":
    # Test with all model files
    for f in ["data/model-3.csv", "data/model-2.csv", "data/model-1.csv", "data/model-4.csv", "data/KPI.csv"]:
        parse_model_config(f)
