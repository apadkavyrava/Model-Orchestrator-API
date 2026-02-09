# Model Orchestrator API

Orchestrates inference outputs from multiple ML models into a unified KPI response, served as a Flask API.

Each model is a linear combination of input variables (and/or outputs of other models) plus a baseline constant. Models run in topological order — downstream models consume upstream outputs.

## Model flow

<img width="1220" height="579" alt="Screenshot 2026-02-06 at 21 51 04" src="https://github.com/user-attachments/assets/062daa39-00e4-4b6a-84bc-5cf20dc24acc" />

## Quick start

```bash
git clone https://github.com/apadkavyrava/Model-Orchestrator-API.git
cd Model-Orchestrator-API
pip install -r requirements.txt
python app.py
```

Server starts on http://localhost:5001.

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Returns `{"status": "ok"}` |
| GET | `/run-pipeline` | Runs the full model pipeline, returns results as JSON |

### Example usage

```bash
# Health check
curl http://localhost:5001/health

# Run pipeline
curl http://localhost:5001/run-pipeline
```

### `/run-pipeline` response

```json
{
  "status": "success",
  "rows": 60,
  "data": [
    {
      "dt": "2020-01-01",
      "variable-1": 60,
      "model_3_output": 150.68,
      "model_2_output": 267.65,
      "model_1_output": 253.67,
      "model_4_output": 293.0,
      "KPI-1": 639.82
    }
  ]
}
```

## Pipeline execution order

```
Input data (13 variables, 60 rows)
  → Step 1: load_data.py        — load and validate input CSV
  → Step 2: run_model_3.py      — Model 3 (no dependencies)
  → Step 3: run_model_2.py      — Model 2 (depends on Model 3)
  → Step 4a: run_model_1.py     — Model 1 (depends on Models 2 & 3)
  → Step 4b: run_model_4.py     — Model 4 (depends on Models 2 & 3)
  → Step 5: run_kpi.py          — KPI (depends on all four models)
```

## Project structure

```
Model-Orchestrator-API/
├── Data/
│   ├── input_data.csv         # raw input: daily time series, 13 variables
│   ├── model-1.csv
│   ├── model-2.csv
│   ├── model-3.csv
│   ├── model-4.csv
│   └── KPI.csv                # model configs: dependencies and coefficients
│
├── app.py                     # Flask entry point with /health and /run-pipeline endpoints
├── model_body.py              # helper: core prediction (linear combination)
├── model_runner.py            # helper: takes a DataFrame and a parsed model config
├── parse_model_config.py      # helper: parses model CSV config to dict
├── load_data.py               # step 1: load and validate input data
├── run_model_3.py             # step 2: run model-3 (no dependency)
├── run_model_2.py             # step 3: run model-2 (depends on model-3)
├── run_model_1.py             # step 4a: run model-1 (depends on model-3 and model-2)
├── run_model_4.py             # step 4b: run model-4 (depends on model-3 and model-2)
├── run_kpi.py                 # step 5: run KPI (depends on all four models)
├── orchestrator.py            # runs full pipeline in topological order
├── requirements.txt           # dependencies (flask, pandas)
└── README.md
```

## Running without the API

The pipeline can also be run directly as a Python script:

```bash
python orchestrator.py
```
