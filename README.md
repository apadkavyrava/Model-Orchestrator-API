The goal of the project is to orchestrates inference outputs from multiple ML models into a unified response.

The ML models flow is: 

<img width="1220" height="579" alt="Screenshot 2026-02-06 at 21 51 04" src="https://github.com/user-attachments/assets/062daa39-00e4-4b6a-84bc-5cf20dc24acc" />


Model-Orchestrator-API/
├── Data/
│   ├── model-1.csv, model-2.csv, model-3.csv, model-4.csv, KPI.csv   ← given data structure of model dependanies and connection
├── app.py                  ← Flask entry point
├── model_body.py           ← helper function - a dummy model for prediction
├── model_runner.py         ← helper function - takes a DataFrame and a parsed model config
├── parse_model_config.py   ← helper function - reload csv file to dict
├── load_data.py            ← 1 step: load data
├── run_model_3.py          ← 2 step: the first run with model-3 with no depencancy
├── run_model_2.py          ← 3 step: the second run with model-2 with dependacy from model-3
├── run_model_1.py          ← 4a step: the third run with model_1 with dependacy from model-3 and model-2
├── run_model_4.py          ← 4b step: the third run with model_4 with dependacy from model-3 and model-2
├── run_kpi.py              ← 5 step: run the last model with dependacy from model-3, model-2, model-1 and model-4
├── orhestrator.by          ← clean entry point
├── requirements.txt        ← dependencies list
└── README.md               ← how to run it
