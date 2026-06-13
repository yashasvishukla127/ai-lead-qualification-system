# src/api/middleware/correlation.py

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from src.utils.logger import correlation_id_var


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Use incoming header or generate a fresh UUID
        cid = request.headers.get("x-request-id", str(uuid.uuid4()))
        token = correlation_id_var.set(cid)  # bind to this async context

        try:
            response: Response = await call_next(request)
        finally:
            correlation_id_var.reset(token)  # always clean up

        response.headers["x-request-id"] = cid  # echo it back in response
        return response