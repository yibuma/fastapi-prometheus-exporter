# fastapi-prometheus-exporter
[![codecov](https://codecov.io/gh/yibuma/fastapi-prometheus-exporter/graph/badge.svg?token=QDbwB7a9kP)](https://codecov.io/gh/yibuma/fastapi-prometheus-exporter)  
FastAPI Prometheus Exporter is a simple Prometheus exporter for FastAPI applications. It provides a set of metrics by default and allows you to add your own metrics as well.

## Installation
```bash
pip install fastapi-prometheus-exporter
```
or
```bash
poetry add fastapi-prometheus-exporter
```

## Usage
```python
from fastapi import FastAPI
from fastapi_prometheus_exporter import PrometheusExporterMiddleware
app = FastAPI()

PrometheusExporterMiddleware.setup(
    app=app,
    metrics_path="/metrics",
    # ignore_paths=["/healthz", "/metrics"],
)
```
### Parameters
- `app`: FastAPI application instance
- `ignore_paths`: List of paths to ignore. Default: `[]`
- `metrics_path`: Path to expose metrics. Default: `/metrics`
- `metrics_registry`: Prometheus registry to use. Default: `prometheus_client.CollectorRegistry`
- `request_latency_name`: Name of the request latency metric. Default: `http_request_duration_seconds`
- `request_latency_doc`: Description of the request latency metric. Default: `HTTP Request Latency`
- `request_latency_buckets`: Buckets for the request latency metric. Default: `prometheus_client.Histogram.DEFAULT_BUCKETS`
- `request_latency_labels`: Labels for the request latency metric. Default: `["method", "endpoint", "http_status"]`
- `request_count_name`: Name of the request count metric. Default: `http_requests_total`
- `request_count_doc`: Description of the request count metric. Default: `Total HTTP Requests`
- `request_count_labels`: Labels for the request count metric. Default: `["method", "endpoint", "http_status"]`

## Metrics
### Default Metrics
- `http_request_duration_seconds`: HTTP request latency in seconds
- `http_requests_total`: Total HTTP requests
