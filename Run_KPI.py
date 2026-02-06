from load_data import load_input_data
from parse_model_config import parse_model_config
from model_runner import run_model
from run_model_1 import run_model_1
from run_model_4 import run_model_4


def run_kpi(df):
    """
    Step 5 — Run KPI
    Depends on all four models.
    """

    # Dependency: ensure model_1_output exists (cascades to Model 2 and Model 3)
    if "model_1_output" not in df.columns:
        df = run_model_1(df)

    # Dependency: ensure model_4_output exists (Model 2 and 3 already done above)
    if "model_4_output" not in df.columns:
        df = run_model_4(df)

    df = run_model(df, parse_model_config("data/KPI.csv"))

    return df


if __name__ == "__main__":
    df = load_input_data("data/input_data.csv")
    df = run_kpi(df)

    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output", "model_2_output", "model_1_output", "model_4_output", "KPI-1"]].head().to_string())
