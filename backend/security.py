"""Security hardening middleware and helpers."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from collections import defaultdict

# Simple in-memory rate limiter (per IP)
_rate = defaultdict(list)
RATE_LIMIT = 100  # requests
RATE_WINDOW = 60  # seconds


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = [t for t in _rate[ip] if now - t < RATE_WINDOW]
        if len(window) >= RATE_LIMIT:
            return Response("Too Many Requests", status_code=429)
        window.append(now)
        _rate[ip] = window
        return await call_next(request)
