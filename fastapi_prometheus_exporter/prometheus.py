import timeit
import typing

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse

from prometheus_client import (
    Counter,
    Histogram,
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
    generate_latest,
)


class PrometheusExporterMiddleware:
    @classmethod
    def setup(
        cls,
        app: FastAPI,
        ignore_paths: list[str] | None = None,
        metrics_path: str = "/metrics",
        metrics_registry: CollectorRegistry | None = None,
        request_latency_name: str = "http_request_duration_seconds",
        request_latency_doc: str = "HTTP Request Latency",
        request_latency_buckets: typing.Sequence[
            float | str
        ] = Histogram.DEFAULT_BUCKETS,
        request_latency_labels: list[str] = ["method", "endpoint", "http_status"],
        request_count_name: str = "http_requests_total",
        request_count_doc: str = "Total HTTP Requests",
        request_count_labels: list[str] = ["method", "endpoint", "http_status"],
    ):
        if metrics_registry is None:
            metrics_registry = CollectorRegistry()
        request_count = Counter(
            request_count_name,
            request_count_doc,
            request_count_labels,
            registry=metrics_registry,
        )
        request_latency = Histogram(
            request_latency_name,
            request_latency_doc,
            request_latency_labels,
            buckets=request_latency_buckets,
            registry=metrics_registry,
        )
        middleware = cls(
            app,
            request_latency,
            request_count,
            metrics_registry,
            ignore_paths,
            metrics_path,
        )
        middleware.register()

    def __init__(
        self,
        app: FastAPI,
        request_latency: Histogram,
        request_count: Counter,
        registry: CollectorRegistry,
        ignore_paths: list[str] | None,
        metrics_path: str,
    ):
        self.app = app
        self.request_latency = request_latency
        self.request_count = request_count
        self.registry = registry
        self.ignore_paths = ignore_paths
        self.metrics_path = metrics_path

    def register(self):
        self.app.get(self.metrics_path, response_class=PlainTextResponse)(
            self.prometheus_output
        )
        self.app.middleware("http")(self.prometheus_middleware)

    async def prometheus_output(self):
        return PlainTextResponse(
            content=generate_latest(self.registry),
            media_type=CONTENT_TYPE_LATEST,
        )

    async def prometheus_middleware(
        self,
        request: Request,
        call_next: typing.Callable[[Request], typing.Awaitable[Response]],
    ):
        endpoint = request.url.path
        if endpoint == self.metrics_path or (
            self.ignore_paths and endpoint in self.ignore_paths
        ):
            return await call_next(request)

        route = request.scope.get("route")
        if route is not None:
            if route.path in self.ignore_paths:
                return await call_next(request)
            endpoint = route.path

        status_code = 200
        start_time = timeit.default_timer()
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except HTTPException as e:
            status_code = e.status_code
            raise e
        except Exception as e:
            status_code = 500
            raise e
        finally:
            request_latency = timeit.default_timer() - start_time
            self.request_latency.labels(
                method=request.method,
                endpoint=endpoint,
                http_status=status_code,
            ).observe(request_latency)
            self.request_count.labels(
                method=request.method,
                endpoint=endpoint,
                http_status=status_code,
            ).inc()
