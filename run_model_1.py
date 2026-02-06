import pandas as pd
from load_data import load_input_data
from read_csv_structure import parse_model_config
from model_body import evaluate_model, Variable
from run_model_3 import run_model
from run_model_2 import run_model_2


def run_model_1(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4a — Run Model 1
    Depends on Model 2 and Model 3.
    """

    # Dependency: ensure model_2_output exists (which also ensures model_3_output)
    if "model_2_output" not in df.columns:
        df = run_model_2(df)

    config = parse_model_config("Data/model-1.csv")
    df = run_model(df, config)

    return df


if __name__ == "__main__":
    df = load_input_data("Data/input_data.csv")
    df = run_model_1(df)

    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output", "model_2_output", "model_1_output"]].head().to_string())
