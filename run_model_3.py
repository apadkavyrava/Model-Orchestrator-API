from load_data import load_input_data
from parse_model_config import parse_model_config
from model_runner import run_model


if __name__ == "__main__":
    # Step 1 - Load data
    df = load_input_data("data/input_data.csv")

    # Step 2 - Run Model 3
    config_m3 = parse_model_config("data/model-3.csv")
    df = run_model(df, config_m3)

    print("\nFirst 5 rows:")
    print(df[["dt", "model_3_output"]].head().to_string())
