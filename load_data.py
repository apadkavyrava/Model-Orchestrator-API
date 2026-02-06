import pandas as pd


def load_input_data(filepath: str) -> pd.DataFrame:
    """
    Step 1 — Load Input Data
    Loads the raw input data, validates it, and returns a clean DataFrame.
    This is the shared read-only data layer for the entire orchestration pipeline.
    """

    # Load CSV
    df = pd.read_csv(filepath, index_col=0)
    df['dt'] = pd.to_datetime(df['dt'])

    # Define expected variables
    expected_variables = [f"variable-{i}" for i in range(1, 14)]

    # Validation checks
    errors = []

    # Check all expected columns exist
    missing_cols = [col for col in expected_variables if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing columns: {missing_cols}")

    # Check for missing values
    null_counts = df[expected_variables].isnull().sum()
    if null_counts.any():
        errors.append(f"Missing values found:\n{null_counts[null_counts > 0]}")

    # Check all variable columns are numeric
    non_numeric = [col for col in expected_variables if col in df.columns and not pd.api.types.is_numeric_dtype(df[col])]
    if non_numeric:
        errors.append(f"Non-numeric columns: {non_numeric}")

    # Check for duplicate dates
    if df['dt'].duplicated().any():
        errors.append(f"Duplicate dates found: {df['dt'][df['dt'].duplicated()].tolist()}")

    # If any validation failed, raise
    if errors:
        raise ValueError("Input data validation failed:\n" + "\n".join(errors))

    # Sort by date
    df = df.sort_values('dt').reset_index(drop=True)

    # Print summary
    print("STEP 1 — Input Data Loaded Successfully")

    return df


if __name__ == "__main__":
    filepath = "data/input_data.csv"
    df = load_input_data(filepath)
    print("\nFirst 5 rows:")
    print(df.head().to_string())
