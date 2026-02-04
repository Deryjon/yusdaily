from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self._hits: dict[str, deque[datetime]] = defaultdict(deque)
        self._lock = Lock()
        self._window = timedelta(minutes=1)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if request.method == "POST" and path in {
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        }:
            now = datetime.now(timezone.utc)
            client_ip = request.client.host if request.client else "unknown"
            key = f"{client_ip}:{path}"
            with self._lock:
                hits = self._hits[key]
                while hits and (now - hits[0]) > self._window:
                    hits.popleft()
                if len(hits) >= self.max_requests:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many auth requests"},
                    )
                hits.append(now)
        return await call_next(request)
