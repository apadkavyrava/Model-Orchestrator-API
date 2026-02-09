The goal of the project is to orchestrates inference outputs from multiple ML models into a unified response.

The ML models flow is: 

<img width="1220" height="579" alt="Screenshot 2026-02-06 at 21 51 04" src="https://github.com/user-attachments/assets/062daa39-00e4-4b6a-84bc-5cf20dc24acc" />

Orchestration Strategy 
Step 1 — Load Input Data
Load imput_data.csv once. This is the shared data layer — read-only, never mutated.
Step 2 — Run Model 3 (no model dependencies)
Store model_3_output as a new column.
Step 3 — Run Model 2 (depends on Model 3)
Store model_2_output as a new column.
Step 4 — Run Model 1 and Model 4 in parallel
Both have all inputs available. No dependency between them. Store both as new columns.
Step 5 — Run KPI (depends on all four models)
Store KPI-1 as the final column.



Model-Orchestrator-API/
├── Data/
│   ├── model-1.csv
│   ├── model-2.csv
│   ├── model-3.csv
│   ├── model-4.csv
│   └── KPI.csv                # given data structure of model dependencies and connections
│
├── app.py                     # Flask entry point
├── model_body.py              # helper function - a dummy model for prediction
├── model_runner.py            # helper function - takes a DataFrame and a parsed model config
├── parse_model_config.py      # helper function - reload CSV file to dict
├── load_data.py               # step 1: load data
├── run_model_3.py             # step 2: first run with model-3 (no dependency)
├── run_model_2.py             # step 3: second run with model-2 (depends on model-3)
├── run_model_1.py             # step 4a: third run with model-1 (depends on model-3 and model-2)
├── run_model_4.py             # step 4b: third run with model-4 (depends on model-3 and model-2)
├── run_kpi.py                 # step 5: final model (depends on model-3, model-2, model-1, and model-4)
├── orchestrator.py            # clean entry point
├── requirements.txt           # dependencies list
└── README.md                  # Project description



