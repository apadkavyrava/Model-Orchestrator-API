# AGENTS.md — Model Orchestrator API

## Project Overview

This project orchestrates inference outputs from multiple ML models into a unified KPI response. Each model is a **linear combination** of input variables (and/or outputs of other models) plus a baseline constant (BAU). The goal is to productionize this pipeline as a Flask API.

**Current state:** Full pipeline working end-to-end. All 4 models + KPI run successfully with validation. Flask API available via `app.py`.

## Prior Thread Context

A detailed design session occurred in [this Claude thread](https://claude.ai/share/7094ccea-1c5b-42f4-b5b8-30325e1185ee). Key outcomes:

### Agreed Design Decisions
1. **No normalization** — coefficients are applied as raw weighted sums (factors do NOT sum to 1, and that's intentional)
2. **Coefficients compound through the chain** — when KPI multiplies `model_1_output` by 0.41, that value already contains `model_2_output * 0.67`, which itself already contains `model_3_output * 0.80`, which carries the weighted raw variables
3. **BAU is added outside `evaluate_model()`** — the model body computes `sum(factor * variable)`, then `run_model()` adds BAU on top
4. **Pass `df.copy()` to `evaluate_model()`** — because it mutates the DataFrame by adding a `prediction` column
5. **Parse model configs one at a time** (not all upfront) — parse config right before running that model, for fail-early behavior
6. **Each model step is its own runner script** — `run_model_3.py`, `run_model_2.py`, etc.

## Architecture

### Model Dependency Graph (execution order matters)

```
Raw Input (13 variables)
        |
        v
   +---------+
   | Model 3  |  <-- Level 0: depends on raw variables only (must run first)
   +----+-----+
        |
   +----+-----+
   v          v
+---------+ +---------+
| Model 2  | |         |  <-- Level 1: depends on Model 3
+----+-----+ |         |
     |       |         |
  +--+---+   |         |
  v      v   v         |
+------+ +---------+   |
|Mod 1 | | Model 4  |  |  <-- Level 2: both depend on Models 2 & 3 (can run in parallel)
+--+---+ +----+-----+  |
   |          |         |
   +----+-----+         |
        v               |
   +---------+          |
   |  KPI-1   | <-------+  <-- Level 3: depends on all four model outputs
   +---------+
```

### Exact Model Formulas

**Step 1 — Load Input Data:**
Load `data/input_data.csv` once. 60 rows, 13 variables, daily from 2020-01-01 to 2020-02-29.

**Step 2 — Model 3** (Level 0, no model dependencies):
```
model_3_output = 0.21*var1 + 0.59*var2 + 0.41*var4 + 0.38*var6 + 0.49*var8 + 0.62*var9 + 0.21
```

**Step 3 — Model 2** (Level 1, depends on Model 3):
```
model_2_output = 0.80*model_3_output + 0.46*var2 + 0.80*var3 + 0.58*var4 + 0.38*var5 + 0.61*var6 + 0.74
```

**Step 4a — Model 1** (Level 2, depends on Models 2 & 3):
```
model_1_output = 0.67*model_2_output + 0.28*model_3_output + 0.53*var1 + 0.35
```

**Step 4b — Model 4** (Level 2, depends on Models 2 & 3, parallel with Model 1):
```
model_4_output = 0.48*var1 + 0.33*var2 + 0.29*model_3_output + 0.73*var8 + 0.46*model_2_output + 0.22*var11 + 0.73
```

**Step 5 — KPI** (Level 3, depends on all four models):
```
KPI-1 = 0.41*model_1 + 0.44*model_2 + 0.21*model_3 + 0.61*model_4 + 0.73*var7 + 0.71*var8 + 0.40*var9 + 0.41*var10 + 0.65*var11 + 0.53*var12 + 0.23
```

**Step 6 — Validate:**
After full pipeline: check all 5 output columns exist, no NaNs, no infinities, numeric, 60 rows preserved.

**Step 7 — Output:**
Final dataset = original input + 5 new columns: `model_3_output`, `model_2_output`, `model_1_output`, `model_4_output`, `KPI-1`.

## Flask API

### Setup
```bash
pip install -r requirements.txt
python app.py
```
Server starts on `http://localhost:5001`.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Returns `{"status": "ok"}` — sanity check that the server is running |
| GET | `/run-pipeline` | Calls `run_pipeline()`, returns full DataFrame as JSON |

### `/run-pipeline` response shape
```json
{
  "status": "success",
  "rows": 60,
  "data": [
    {"dt": "2020-01-01", "variable-1": 42, ..., "model_3_output": 150.68, ..., "KPI-1": 639.82},
    ...
  ]
}
```

On error, returns HTTP 500 with `{"status": "error", "message": "..."}`.

## File Structure

```
.
├── AGENTS.md                  # This file
├── README.md                  # Brief project description with flow diagram
├── .gitignore                 # Ignores __pycache__/ and data/.ipynb_checkpoints/
├── requirements.txt           # Python dependencies (flask, pandas)
│
│   # Flask API
├── app.py                     # Flask app with /health and /run-pipeline endpoints
│
│   # Core modules (shared logic)
├── load_data.py               # Step 1: load & validate input CSV
├── parse_model_config.py      # Parse model config CSVs into dicts
├── model_body.py              # Core model evaluation (linear combination)
├── model_runner.py            # Generic run_model() function
│
│   # Step runners (one per model)
├── run_model_3.py             # Step 2: run Model 3
├── run_model_2.py             # Step 3: run Model 2 (depends on Model 3)
├── run_model_1.py             # Step 4a: run Model 1 (depends on Models 2 & 3)
├── run_model_4.py             # Step 4b: run Model 4 (depends on Models 2 & 3)
├── run_KPI.py                 # Step 5: run KPI (depends on all four models)
│
│   # Pipeline
├── orchestrator.py            # run_pipeline(): full orchestration in topological order
├── Pipeline_validation.py     # Steps 1-7: full pipeline + validation + save output
│
└── data/
    ├── input_data.csv         # Raw input: daily time series, 13 variables
    ├── input_data.xlsx        # Same data as Excel (original source)
    ├── model-1.csv            # Model 1 config (coefficients + BAU)
    ├── model-2.csv            # Model 2 config
    ├── model-3.csv            # Model 3 config
    ├── model-4.csv            # Model 4 config
    ├── KPI.csv                # KPI-1 config
    └── Untitled.ipynb         # Exploratory notebook (not part of pipeline)
```

## Key Modules

### `load_data.py` — Data Ingestion (Step 1)
- **Function:** `load_input_data(filepath) -> pd.DataFrame`
- Loads CSV, parses `dt` as datetime, validates:
  - All 13 expected columns (`variable-1` through `variable-13`) exist
  - No missing values in variable columns
  - All variable columns are numeric
  - No duplicate dates
- Sorts by date, returns clean DataFrame
- Note: `variable-13` exists in input but is not used by any model or KPI

### `parse_model_config.py` — Model Config Parser
- **Function:** `parse_model_config(filepath) -> dict`
- Parses model CSV files into:
  ```python
  {
      "model_name": "model_3_output",
      "coefficients": {"variable-1": 0.21, ...},
      "bau": 0.21
  }
  ```
- Rows with `relation == "~"` are coefficient terms
- Row with `relation == "bau"` is the baseline constant

### `model_body.py` — Core Model Evaluation
- **Function:** `evaluate_model(coefficients, input_data) -> DataFrame[dt, prediction]`
- `coefficients`: dict of `{variable_name: factor}` — passed directly from parsed config
- Computes: `prediction = sum(variable_i * factor_i)` for each row
- Returns only `dt` and `prediction` columns
- **Caution:** mutates `input_data` by adding a `prediction` column — always pass `df.copy()`
- BAU is NOT added here — it's added in `run_model()`

### `model_runner.py` — Generic Model Runner
- **Function:** `run_model(df, config) -> pd.DataFrame`
- Bridges `parse_model_config` output to `evaluate_model`:
  - Passes config coefficients dict directly to `evaluate_model(coefficients, df.copy())`
  - Adds BAU to prediction
  - Stores result as new column `df[config["model_name"]]`
- Validates: required input columns exist, no NaN in output
- No top-level dependency on `parse_model_config` — callers are responsible for parsing configs

### `Pipeline_validation.py` — Full Pipeline + Validation
- **Function:** `validate(df) -> bool`
- Checks: all 5 output columns present, no NaNs, no infinities, numeric types, 60 rows preserved
- Runs full pipeline via `run_kpi()` cascade, validates, saves to `Data/pipeline_output.csv`

### Integration Flow
```
CSV file --> parse_model_config() --> config dict
                                        |
config["coefficients"] --> evaluate_model(coefficients, df.copy())
                                        |
                                 df[dt, prediction]
                                        |
                           prediction + config["bau"]
                                        |
                           stored as df[config["model_name"]]
```

### Import Graph
```
model_body.py          <-- no dependencies
parse_model_config.py  <-- no dependencies
load_data.py           <-- no dependencies
model_runner.py        <-- imports from model_body
run_model_3.py         <-- imports from parse_model_config, model_runner
run_model_2.py         <-- imports from load_data, parse_model_config, model_runner, run_model_3
run_model_1.py         <-- imports from load_data, parse_model_config, model_runner, run_model_2
run_model_4.py         <-- imports from load_data, parse_model_config, model_runner, run_model_2
run_KPI.py             <-- imports from load_data, parse_model_config, model_runner, run_model_1, run_model_4
Pipeline_validation.py <-- imports from load_data, Run_KPI
```

## Data Formats

### Input Data (`data/input_data.csv`)
| Column | Type | Description |
|--------|------|-------------|
| `dt` | date (YYYY-MM-DD) | Daily timestamps, 2020-01-01 to 2020-02-29 (60 rows) |
| `variable-1` to `variable-13` | int | Input features (values range ~12-98) |

### Model Config CSVs (`data/model-*.csv`, `data/KPI.csv`)
| Column | Description |
|--------|-------------|
| `independent-variable` | Output name (e.g. `model_3_output`, `KPI-1`) |
| `relation` | `~` for coefficient term, `bau` for baseline |
| `dep-var` | Input variable name (empty for bau rows) |
| `factor` | Numeric coefficient or baseline value |

## Development Environment

- **Python 3.13** (Anaconda distribution)
- **Run with `python`** (not `python3` — system `python3` lacks pandas)
- **Anaconda path:** `/opt/anaconda3/bin/python`
- `pandas` and `numpy` are installed via Anaconda
- No `requirements.txt` or virtual environment config exists yet
- **macOS** (darwin)

## Changelog

### Refactoring — Consistency & Redundancy Cleanup

**1. `run_model_3.py` — Added reusable `run_model_3(df)` function**
- Was the only runner without a callable function (just a `__main__` script)
- Now consistent with `run_model_1`, `run_model_2`, `run_model_4` — all expose a `run_model_N(df)` function
- Model 3 is the base model (no dependencies)

**2. `run_model_2.py` — Uses `run_model_3(df)` for its dependency**
- Previously inlined `run_model(df, parse_model_config("data/model-3.csv"))` to run Model 3
- Now calls `run_model_3(df)`, matching how `run_model_1` and `run_model_4` call `run_model_2(df)`

**3. `model_body.py` / `model_runner.py` — Eliminated dict→namedtuple→dict round-trip**
- `evaluate_model` now accepts a `coefficients` dict directly instead of `Variable` namedtuples
- Removed the `Variable` namedtuple and `collections` import from `model_body.py`
- `model_runner.py` passes the coefficients dict straight through — no conversion step

**4. `model_runner.py` — Removed unused production import**
- `parse_model_config` moved from top-level import into `__main__` block (only used there for standalone testing)

## Known Issues

1. **`model_body.py` mutates input** — `evaluate_model` adds a `prediction` column to `input_data` directly; always pass `.copy()`
2. **Path casing** — code uses `Data/` which works on macOS (case-insensitive) but would break on Linux
3. **No tests yet**

## What Remains To Be Built

- Tests

## Conventions

- Step-based logging with `print()` statements (e.g., "STEP 1 — Input Data Loaded Successfully")
- Model configs are CSV files, not hardcoded — all coefficients/BAU read from CSVs at runtime
- The shared DataFrame accumulates columns as models run (each model adds its output column)
- Core logic split into 4 modules: `load_data`, `parse_model_config`, `model_body`, `model_runner`
- Each model step has its own runner with dependency checking (auto-runs upstream models if needed)
- Runner files have `if __name__ == "__main__"` blocks for standalone testing — never put code outside that guard
- Parse model configs one at a time, right before running that model
