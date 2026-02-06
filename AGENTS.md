# AGENTS.md — Model Orchestrator API

## Project Overview

This project orchestrates inference outputs from multiple ML models into a unified KPI response. Each model is a **linear combination** of input variables (and/or outputs of other models) plus a baseline constant (BAU). The goal is to productionize this pipeline as a Flask API.

**Current state:** Early development. Steps 1-3 (load data, Model 3, Model 2) were implemented and tested in a prior Claude thread but only partially committed to the repo. Steps 4-5 (Models 1 & 4, KPI) and the Flask API are not built yet.

## Prior Thread Context

A detailed design session occurred in [this Claude thread](https://claude.ai/share/7094ccea-1c5b-42f4-b5b8-30325e1185ee). Key outcomes:

### Agreed Design Decisions
1. **No normalization** — coefficients are applied as raw weighted sums (factors do NOT sum to 1, and that's intentional)
2. **Coefficients compound through the chain** — when KPI multiplies `model_1_output` by 0.41, that value already contains `model_2_output * 0.67`, which itself already contains `model_3_output * 0.80`, which carries the weighted raw variables
3. **BAU is added outside `evaluate_model()`** — the model body computes `sum(factor * variable)`, then `run_model()` adds BAU on top
4. **Pass `df.copy()` to `evaluate_model()`** — because it mutates the DataFrame by adding a `prediction` column
5. **Parse model configs one at a time** (not all upfront) — parse config right before running that model, for fail-early behavior
6. **Each model step is its own runner script** — `run_model_3.py`, `run_model_2.py`, etc.

### Agreed Restructuring Plan (partially implemented)
The thread agreed to restructure so that shared logic lives in a helpers module:
- **`model_helpers.py`** — should hold both `parse_model_config()` AND `run_model()` (currently `parse_model_config` lives in `read_csv_structure.py` and `run_model` lives in `run_model_3.py`)
- **`run_model_2.py`** — was created in the thread but NOT committed to repo
- **`model_body.py`** — was cleaned up (example code removed) in the thread but the committed version still has the old code

### What Was Completed in the Thread (but not all committed)
- Step 1: load_data.py — committed and working
- Step 2: run_model_3.py with generic `run_model()` — committed (but has line 55 bug)
- Step 3: run_model_2.py — created and tested, NOT committed
- Restructuring (move `run_model` to helpers) — discussed and tested, NOT committed

### What Remains To Be Built
- Step 4: Model 1 & Model 4 runner (can run in parallel)
- Step 5: KPI runner
- Full orchestration pipeline script
- Flask API
- Tests
- requirements.txt

## Architecture

### Model Dependency Graph (execution order matters)

```
Raw Input (13 variables)
        |
        v
   +---------+
   | Model 3  |  <-- depends on raw variables only (must run first)
   +----+-----+
        |
   +----+-----+
   v          v
+---------+ +---------+
| Model 2  | |         |
+----+-----+ |         |
     |       |         |
  +--+---+   |         |
  v      v   v         |
+------+ +---------+   |
|Mod 1 | | Model 4  |  |
+--+---+ +----+-----+  |
   |          |         |
   +----+-----+         |
        v               |
   +---------+          |
   |  KPI-1   | <-------+
   +---------+
```

### Exact Model Formulas (agreed in prior thread)

**Step 1 — Load Input Data:**
Load `data/input_data.csv` once. 60 rows, 13 variables, daily from 2020-01-01 to 2020-02-29.

**Step 2 — Model 3** (no model dependencies):
```
model_3_output = 0.21*var1 + 0.59*var2 + 0.41*var4 + 0.38*var6 + 0.49*var8 + 0.62*var9 + 0.21
```

**Step 3 — Model 2** (depends on Model 3):
```
model_2_output = 0.80*model_3_output + 0.46*var2 + 0.80*var3 + 0.58*var4 + 0.38*var5 + 0.61*var6 + 0.74
```

**Step 4a — Model 1** (depends on Models 2 & 3):
```
model_1_output = 0.67*model_2_output + 0.28*model_3_output + 0.53*var1 + 0.35
```

**Step 4b — Model 4** (depends on Models 2 & 3, parallel with Model 1):
```
model_4_output = 0.48*var1 + 0.33*var2 + 0.29*model_3_output + 0.73*var8 + 0.46*model_2_output + 0.22*var11 + 0.73
```

**Step 5 — KPI** (depends on all four models):
```
KPI-1 = 0.41*model_1 + 0.44*model_2 + 0.21*model_3 + 0.61*model_4 + 0.73*var7 + 0.71*var8 + 0.40*var9 + 0.41*var10 + 0.65*var11 + 0.53*var12 + 0.23
```

**Step 6 — Validate:**
After each step: no NaNs, outputs are numeric and finite. Halt on failure.

**Step 7 — Output:**
Final dataset = original input + 5 new columns: `model_3_output`, `model_2_output`, `model_1_output`, `model_4_output`, `KPI-1`.

## File Structure (current repo state)

```
.
├── AGENTS.md                  # This file
├── README.md                  # Brief project description with flow diagram
├── .gitignore                 # Ignores __pycache__/ and data/.ipynb_checkpoints/
├── load_data.py               # Step 1: load & validate input CSV
├── read_csv_structure.py      # Parse model config CSVs (to be renamed model_helpers.py)
├── model_body.py              # Core model evaluation (linear combination)
├── run_model_3.py             # Step 2 runner + generic run_model() (to be restructured)
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

### Target File Structure (agreed in prior thread)
```
.
├── model_helpers.py           # parse_model_config() + run_model() (shared logic)
├── model_body.py              # evaluate_model() + Variable namedtuple
├── load_data.py               # load_input_data()
├── run_model_3.py             # Step 2 runner
├── run_model_2.py             # Step 3 runner (NOT yet in repo)
├── run_model_1.py             # Step 4a runner (NOT yet built)
├── run_model_4.py             # Step 4b runner (NOT yet built)
├── run_kpi.py                 # Step 5 runner (NOT yet built)
└── data/                      # (unchanged)
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

### `read_csv_structure.py` — Model Config Parser (to become `model_helpers.py`)
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
- `run_model()` should also live here (per restructuring plan)

### `model_body.py` — Core Model Evaluation
- **Types:** `Variable = namedtuple('Variable', 'name factor')`
- **Function:** `evaluate_model(dependent_variables_list, input_data) -> DataFrame[dt, prediction]`
- Computes: `prediction = sum(variable_i * factor_i)` for each row
- Returns only `dt` and `prediction` columns
- **Caution:** mutates `input_data` by adding a `prediction` column — always pass `df.copy()`
- BAU is NOT added here — it's added in `run_model()`

### `run_model_3.py` — Orchestration Runner (Step 2)
- **Function:** `run_model(df, config) -> pd.DataFrame`
- Generic runner: converts config coefficients dict to `Variable` namedtuples, calls `evaluate_model`, adds BAU
- Adds result as a new column named `config["model_name"]` to the DataFrame
- Validates no NaN in output
- **Bug:** Line 55 calls `run_model(df, config_m3)` outside `if __name__` guard — runs on every import

### Integration Flow (how the pieces connect)
```
CSV file --> parse_model_config() --> config dict
                                        |
config["coefficients"] --> [Variable namedtuples] --> evaluate_model(variables, df.copy())
                                                           |
                                                    df[dt, prediction]
                                                           |
                                              prediction + config["bau"]
                                                           |
                                              stored as df[config["model_name"]]
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

## Known Issues

1. **Bug in `run_model_3.py:55`** — `run_model(df, config_m3)` is called outside the `if __name__` guard, executes on every import
2. **`model_body.py` mutates input** — `evaluate_model` adds a `prediction` column to `input_data` directly; always pass `.copy()`
3. **Path casing inconsistency** — some code uses `Data/` but filesystem directory is `data/`
4. **Restructuring incomplete** — `run_model()` should move to helpers module, `read_csv_structure.py` should become `model_helpers.py`
5. **No tests, no requirements.txt, no Flask API yet**

## Conventions

- Step-based logging with `print()` statements (e.g., "STEP 1 — Input Data Loaded Successfully")
- Model configs are CSV files, not hardcoded — all coefficients/BAU read from CSVs at runtime
- The shared DataFrame accumulates columns as models run (each model adds its output column)
- Model evaluation (`model_body.py`) is separated from orchestration (`run_model`)
- Each step gets its own runner script that chains all prior dependencies
- Parse model configs one at a time, right before running that model
