from time import perf_counter

from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.requests import Request
from starlette.routing import Match

from app.monitoring.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
)


EXCLUDED_PATHS = {
    "/metrics",
    "/metrics/",
}


def get_route_template(
    request: Request,
) -> str:
    route = request.scope.get("route")

    if route is not None:
        route_path = getattr(
            route,
            "path",
            None,
        )

        if route_path:
            return route_path

    return "unmatched"


class PrometheusMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        if (
            request.url.path
            in EXCLUDED_PATHS
        ):
            return await call_next(
                request
            )

        started_at = perf_counter()

        status_code = 500

        try:
            response = await call_next(
                request
            )

            status_code = (
                response.status_code
            )

            return response

        finally:
            duration_seconds = (
                perf_counter()
                - started_at
            )

            route = get_route_template(
                request
            )

            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                route=route,
                status_code=str(
                    status_code
                ),
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                route=route,
            ).observe(
                duration_seconds
            )