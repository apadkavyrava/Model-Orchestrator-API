from parse_model_config import parse_model_config
from model_runner import run_model


def run_model_3(df):
    """
    Step 2 — Run Model 3
    Base model with no dependencies (uses raw variables only).
    """

    df = run_model(df, parse_model_config("data/model-3.csv"))

    return df


if __name__ == "__main__":
    from load_data import load_input_data

    df = load_input_data("data/input_data.csv")
    df = run_model_3(df)

    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output"]].head().to_string())
