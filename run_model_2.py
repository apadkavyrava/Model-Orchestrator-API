from load_data import load_input_data
from parse_model_config import parse_model_config
from model_runner import run_model
from run_model_3 import run_model_3


def run_model_2(df):
    """
    Step 3 — Run Model 2
    Depends on Model 3, so runs it first if model_3_output is missing.
    """

    # Dependency: ensure model_3_output exists
    if "model_3_output" not in df.columns:
        df = run_model_3(df)

    df = run_model(df, parse_model_config("data/model-2.csv"))

    return df


if __name__ == "__main__":
    df = load_input_data("data/input_data.csv")
    df = run_model_2(df)

    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output", "model_2_output"]].head().to_string())
