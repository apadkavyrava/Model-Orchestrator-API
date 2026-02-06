import pandas as pd
from load_data import load_input_data
from read_csv_structure import parse_model_config
from model_body import evaluate_model, Variable
from run_model_3 import run_model
from run_model_1 import run_model_1
from run_model_4 import run_model_4


def run_kpi(df: pd.DataFrame) -> pd.DataFrame:
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

    config = parse_model_config("Data/KPI.csv")
    df = run_model(df, config)

    return df


if __name__ == "__main__":
    df = load_input_data("Data/input_data.csv")
    df = run_kpi(df)

    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output", "model_2_output", "model_1_output", "model_4_output", "KPI-1"]].head().to_string())
