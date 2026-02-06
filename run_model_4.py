from load_data import load_input_data
from parse_model_config import parse_model_config
from model_runner import run_model
from run_model_2 import run_model_2


def run_model_4(df):
    """
    Step 4b — Run Model 4
    Depends on Model 2 and Model 3.
    """

    # Dependency: ensure model_2_output exists (which also ensures model_3_output)
    if "model_2_output" not in df.columns:
        df = run_model_2(df)

    df = run_model(df, parse_model_config("data/model-4.csv"))

    return df


if __name__ == "__main__":
    df = load_input_data("data/input_data.csv")
    df = run_model_4(df)

    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output", "model_2_output", "model_4_output"]].head().to_string())
