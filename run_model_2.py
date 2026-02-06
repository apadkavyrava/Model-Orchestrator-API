import pandas as pd
from load_data import load_input_data
from read_csv_structure import parse_model_config
from model_body import evaluate_model, Variable
from run_model_3 import run_model


def run_model_2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3 — Run Model 2
    Depends on Model 3, so runs it first if model_3_output is missing.
    """

    # Dependency: ensure model_3_output exists
    if "model_3_output" not in df.columns:
        config_m3 = parse_model_config("Data/model-3.csv")
        df = run_model(df, config_m3)

    config = parse_model_config("Data/model-2.csv")
    df = run_model(df, config)

    return df


if __name__ == "__main__":
    df = load_input_data("Data/input_data.csv")
    df = run_model_2(df)

    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output", "model_2_output"]].head().to_string())
