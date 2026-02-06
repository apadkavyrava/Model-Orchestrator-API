from load_data import load_input_data
from parse_model_config import parse_model_config
from model_runner import run_model


def run_pipeline(input_path="data/input_data.csv"):
    """
    Runs the full orchestration pipeline in topological order.

    Level 0: Model 3  (raw variables only)
    Level 1: Model 2  (depends on Model 3)
    Level 2: Model 1 & Model 4  (depend on Models 2 & 3)
    Level 3: KPI  (depends on all four models)
    """

    # Step 1 — Load input data
    df = load_input_data(input_path)

    # Step 2 — Model 3
    df = run_model(df, parse_model_config("data/model-3.csv"))

    # Step 3 — Model 2
    df = run_model(df, parse_model_config("data/model-2.csv"))

    # Step 4 — Model 1 & Model 4
    df = run_model(df, parse_model_config("data/model-1.csv"))
    df = run_model(df, parse_model_config("data/model-4.csv"))

    # Step 5 — KPI
    df = run_model(df, parse_model_config("data/KPI.csv"))

    return df


if __name__ == "__main__":
    df = run_pipeline()

    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output", "model_2_output", "model_1_output", "model_4_output", "KPI-1"]].head().to_string())
