from flask import Flask, request
from prometheus_client import (
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    disable_created_metrics,
)
from dotenv import load_dotenv
import os
import time
import random
import requests
from prometheus_summary import Summary

load_dotenv()

disable_created_metrics()

app = Flask(__name__)

# Create a custom registry
registry = CollectorRegistry()

# Create a counter metric
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests received",
    ["status", "path", "method"],
    registry=registry,
)

# Define a Gauge metric for tracking active HTTP requests
active_requests_gauge = Gauge(
    "http_active_requests",
    "Number of active connections to the service",
    registry=registry,
)

# Define a Histogram metric for request duration
latency_histogram = Histogram(
    "http_request_duration_seconds",
    "Duration of HTTP requests",
    ["status", "path", "method"],
    registry=registry,
)

posts_latency_summary = Summary(
    "post_request_duration_seconds",
    "Duration of requests to https://jsonplaceholder.typicode.com/posts",
    ["method"],
    registry=registry,
)


@app.before_request
def before_request():
    delay = random.uniform(0.5, 2)
    time.sleep(delay)
    """Track start of request processing"""
    active_requests_gauge.inc()
    request.start_time = time.time()


@app.after_request
def after_request(response):
    """Increment counter after each request"""
    http_requests_total.labels(
        status=str(response.status_code), path=request.path, method=request.method
    ).inc()
    active_requests_gauge.dec()
    duration = time.time() - request.start_time
    latency_histogram.labels(
        status=str(response.status_code), path=request.path, method=request.method
    ).observe(duration)
    return response


@app.route("/posts")
def get_posts():
    start_time = time.time()

    try:
        response = requests.get("https://jsonplaceholder.typicode.com/posts")
        response.raise_for_status()
    except requests.RequestException as e:
        return str(e), 500
    finally:
        # Record the request duration in the summary
        duration = time.time() - start_time
        posts_latency_summary.labels(method="GET").observe(duration)

    return response.json()


@app.route("/metrics")
def metrics():
    return generate_latest(registry), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/")
def hello():
    return "Hello world!"


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting HTTP server on port {port}")
    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        print(f"Server failed to start: {e}")
        exit(1)
