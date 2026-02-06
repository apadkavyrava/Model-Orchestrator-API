import pandas as pd
from load_data import load_input_data
from Run_KPI import run_kpi


def validate(df: pd.DataFrame) -> bool:
    """
    Step 6 — Validate the full pipeline output.
    Checks all model outputs and KPI for integrity.
    """

    expected_outputs = [
        "model_3_output",
        "model_2_output",
        "model_1_output",
        "model_4_output",
        "KPI-1",
    ]

    errors = []

    # Check all output columns exist
    missing = [col for col in expected_outputs if col not in df.columns]
    if missing:
        errors.append(f"Missing output columns: {missing}")

    # Check for NaN values
    for col in expected_outputs:
        if col in df.columns and df[col].isnull().any():
            errors.append(f"{col} has {df[col].isnull().sum()} NaN values")

    # Check for infinite values
    for col in expected_outputs:
        if col in df.columns and df[col].isin([float("inf"), float("-inf")]).any():
            errors.append(f"{col} has infinite values")

    # Check all values are numeric and finite
    for col in expected_outputs:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"{col} is not numeric")

    # Check row count is preserved
    if len(df) != 60:
        errors.append(f"Expected 60 rows, got {len(df)}")

    # Print validation report
    print("\n" + "=" * 60)
    print("STEP 6 — Validation")
    print("=" * 60)

    if errors:
        print("  FAILED:")
        for e in errors:
            print(f"    - {e}")
        return False

    print("  All checks passed:")
    print(f"    - {len(expected_outputs)} output columns present")
    print(f"    - 0 NaN values")
    print(f"    - 0 infinite values")
    print(f"    - {len(df)} rows preserved")
    print("\n  Output summary:")
    for col in expected_outputs:
        print(f"    {col:20s}  min={df[col].min():>10.2f}  mean={df[col].mean():>10.2f}  max={df[col].max():>10.2f}")
    print("=" * 60)

    return True


if __name__ == "__main__":
    # Step 1 — Load data
    df = load_input_data("Data/input_data.csv")

    # Steps 2-5 — Run full pipeline (cascades automatically)
    df = run_kpi(df)

    # Step 6 — Validate
    is_valid = validate(df)

    # Step 7 — Save output
    if is_valid:
        output_path = "Data/pipeline_output.csv"
        df.to_csv(output_path, index=False)
        print(f"\n  Output saved to: {output_path}")
        print(f"\n  Final columns: {list(df.columns)}")
        print(f"\nFirst 5 rows:")
        print(df.head().to_string())
    else:
        print("\n  Pipeline failed validation. Output not saved.")
