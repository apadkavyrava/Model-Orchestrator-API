from flask import Flask, jsonify
from orchestrator import run_pipeline

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/run-pipeline")
def pipeline():
    try:
        df = run_pipeline()
        df["dt"] = df["dt"].astype(str)
        records = df.to_dict(orient="records")
        return jsonify({"status": "success", "rows": len(records), "data": records})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
