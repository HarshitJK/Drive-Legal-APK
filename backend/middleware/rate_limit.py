import time
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-process rate limiter (per IP, per minute).
    For production, use Redis-backed rate limiting.
    """

    def __init__(self, app, calls_per_minute: int = None):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self._windows: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and docs
        if request.url.path in {"/health", "/docs", "/redoc", "/openapi.json", "/"}:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        # Purge old timestamps outside 60s window
        self._windows[ip] = [t for t in self._windows[ip] if now - t < 60]

        if len(self._windows[ip]) >= self.calls_per_minute:
            return Response(
                content='{"detail":"Rate limit exceeded. Please wait before retrying."}',
                status_code=429,
                media_type="application/json",
            )

        self._windows[ip].append(now)
        return await call_next(request)
