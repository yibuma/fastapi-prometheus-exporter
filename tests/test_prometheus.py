import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_prometheus_exporter.prometheus import PrometheusExporterMiddleware

null_context = """# HELP http_requests_total Total HTTP Requests
# TYPE http_requests_total counter
# HELP http_request_duration_seconds HTTP Request Latency
# TYPE http_request_duration_seconds histogram
"""


class TestPrometheus(unittest.TestCase):
    def setUp(self) -> None:
        app = FastAPI()
        PrometheusExporterMiddleware.setup(
            app=app,
            ignore_paths=["/ignore"],
            metrics_path="/metrics",
        )
        app.get("/test")(lambda: {"status": "ok"})
        app.get("/ignore")(lambda: {"status": "ok"})
        client = TestClient(app)
        self.client = client

    def test_null_metrics(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, null_context)

    def test_ignore(self):
        response = self.client.get("/ignore")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, null_context)

    def test_test(self):
        response = self.client.get("/test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.text), len(null_context))
        self.assertGreater(
            response.text.find(
                'http_requests_total{endpoint="/test",http_status="200",method="GET"} 1.0'
            ),
            0,
        )
        self.assertGreater(
            response.text.find(
                'http_requests_created{endpoint="/test",http_status="200",method="GET"}'
            ),
            0,
        )
        self.assertGreater(
            response.text.find(
                'http_request_duration_seconds_bucket{endpoint="/test",http_status="200",le="+Inf",method="GET"} 1.0'
            ),
            0,
        )
        self.assertGreater(
            response.text.find(
                'http_request_duration_seconds_count{endpoint="/test",http_status="200",method="GET"} 1.0'
            ),
            0,
        )
        self.assertGreater(
            response.text.find(
                'http_request_duration_seconds_sum{endpoint="/test",http_status="200",method="GET"}'
            ),
            0,
        )
        self.assertGreater(
            response.text.find(
                'http_request_duration_seconds_created{endpoint="/test",http_status="200",method="GET"} '
            ),
            0,
        )
