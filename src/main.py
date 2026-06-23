import logging
import traceback  # 👈 Added to print the stack trace
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse  # 👈 Added for custom error responses
from fastapi.responses import PlainTextResponse # 👈 Added for debug endpoint
from src.api.middleware.correlation import CorrelationIDMiddleware
from src.api.routers import leads, health, costs
from src.utils.logger import configure_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Lead Analyser API starting up")
    yield       
    logger.info("Lead Analyser API shutting down")

# Declares that app is a FastAPI instance
app = FastAPI(
    title="Lead Analyser API",
    version="1.0.0",
    description="Async lead analysis pipeline with Claude",
    lifespan=lifespan,
)

# Global Exception Handler to expose hidden tracebacks
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("\n=== !!! FORCED TRACEBACK LOG !!! ===")
    traceback.print_exc()  # This prints the red error text directly to your terminal
    print("====================================\n")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "details": str(exc)}
    )

app.add_middleware(CorrelationIDMiddleware)

# Routers defining the endpoints
app.include_router(leads.router) 
app.include_router(health.router)
app.include_router(costs.router)


# main.py — add temporarily, remove after debugging
@app.get("/debug/errors", response_class=PlainTextResponse)
async def debug_errors():
    import os
    log_path = os.path.join(os.path.dirname(__file__), "src", "errors.log")
    if not os.path.exists(log_path):
        return "errors.log not found"
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines[-20:])  # last 20 lines
