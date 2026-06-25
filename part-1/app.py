import os
import time
from flask import Flask, request, jsonify, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = Flask(__name__)

# ---------------------------
# ENV CONFIG
# ---------------------------
#INFER_DELAY = float(os.getenv("INFER_DELAY", "0.5"))  # seconds
#MEMORY_MB = int(os.getenv("MEMORY_MB", "0"))  # simulate memory load

try:
    INFER_DELAY = float(os.environ["INFER_DELAY"])
    MEMORY_MB = int(os.environ["MEMORY_MB"])
except KeyError as e:
    raise RuntimeError(f"Missing required environment variable: {e}")

# ---------------------------
# PROMETHEUS METRICS
# ---------------------------
REQUEST_COUNT = Counter("requests_total", "Total requests", ["endpoint", "status"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Latency histogram", ["endpoint"])
IN_FLIGHT = Gauge("inflight_requests", "In-flight requests")
ERROR_COUNT = Counter("error_total", "Total errors")

# ---------------------------
# HEALTH ENDPOINTS
# ---------------------------
@app.route("/healthz")
def healthz():
    return "ok", 200

@app.route("/readyz")
def readyz():
    # simple readiness check
    if MEMORY_MB < 0:
        return "not ready", 503
    return "ready", 200

# ---------------------------
# PREDICTION ENDPOINT
# ---------------------------
@app.route("/predict", methods=["POST"])
def predict():
    IN_FLIGHT.inc()
    start = time.time()

    try:
        data = request.get_json(silent=True) or {}

        # optional per-request override
        delay = float(data.get("delay", INFER_DELAY))

        # simulate failure condition
        if data.get("fail") == True:
            raise Exception("Forced failure triggered")

        time.sleep(delay)

        result = {
            "input": data,
            "prediction": "class_A",
            "confidence": 0.92
        }

        REQUEST_COUNT.labels("/predict", "200").inc()
        REQUEST_LATENCY.labels("/predict").observe(time.time() - start)

        return jsonify(result)

    except Exception as e:
        REQUEST_COUNT.labels("/predict", "500").inc()
        ERROR_COUNT.inc()
        return jsonify({"error": str(e)}), 500

    finally:
        IN_FLIGHT.dec()

# ---------------------------
# METRICS ENDPOINT
# ---------------------------
@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)