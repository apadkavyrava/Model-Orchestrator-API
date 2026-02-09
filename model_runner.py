import pandas as pd
from model_body import evaluate_model


def run_model(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Generic model runner.
    Takes a DataFrame and a parsed model config.
    Uses evaluate_model from model_body to compute predictions,
    then adds bau to get the final output.
    """

    model_name = config["model_name"]
    coefficients = config["coefficients"]
    bau = config["bau"]

    # Validate required columns exist in df
    missing = [col for col in coefficients if col not in df.columns]
    if missing:
        raise ValueError(f"{model_name} missing input columns: {missing}")

    # Run model body
    result = evaluate_model(coefficients, df.copy())

    # Add bau and store as new column
    df[model_name] = result["prediction"].values + bau

    # Validate output
    if df[model_name].isnull().any():
        raise ValueError(f"{model_name} produced NaN values")

    print(f"\n  Computed: {model_name}")
    print(f"  Range:   {df[model_name].min():.2f} -> {df[model_name].max():.2f}")
    print(f"  Mean:    {df[model_name].mean():.2f}")

    return df


if __name__ == "__main__":
    from load_data import load_input_data
    from parse_model_config import parse_model_config

    df = load_input_data("data/input_data.csv")
    config = parse_model_config("data/model-3.csv")
    df = run_model(df, config)
    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output"]].head().to_string())
