#src/main.py


# import logging
# from contextlib import asynccontextmanager

# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates

# from src.api.middleware.correlation import CorrelationIDMiddleware
# from src.api.routers import leads, health, costs
# from src.utils.logger import configure_logging

# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     configure_logging()
#     logger.info("Lead Analyser API starting up")
#     yield
#     logger.info("Lead Analyser API shutting down")


# app = FastAPI(
#     title="Lead Analyser API",
#     version="1.0.0",
#     description="Async lead analysis pipeline with Claude",
#     lifespan=lifespan,
# )

# # Frontend
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# @app.get("/", response_class=HTMLResponse)
# async def serve_ui(request: Request):
#     return templates.TemplateResponse(request=request, name="index.html")

# # Middleware
# app.add_middleware(CorrelationIDMiddleware)

# # Routers
# app.include_router(leads.router)
# app.include_router(health.router)
# app.include_router(costs.router)




# import logging
# from contextlib import asynccontextmanager

# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates

# from src.api.middleware.correlation import CorrelationIDMiddleware
# from src.api.routers import leads, health, costs
# from src.utils.logger import configure_logging

# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     configure_logging()
#     logger.info("Lead Analyser API starting up")
#     yield
#     logger.info("Lead Analyser API shutting down")


# app = FastAPI(
#     title="Lead Analyser API",
#     version="1.0.0",
#     description="Async lead analysis pipeline with Claude",
#     lifespan=lifespan,
# )

# # ---------------------------
# # Frontend
# # ---------------------------

# app.mount("/static", StaticFiles(directory="static"), name="static")

# templates = Jinja2Templates(directory="templates")


# @app.get("/", response_class=HTMLResponse)
# async def serve_ui(request: Request):
#     return templates.TemplateResponse(request=request, name="index.html")


# # ---------------------------
# # Middleware
# # ---------------------------

# app.add_middleware(CorrelationIDMiddleware)

# # ---------------------------
# # Routers
# # ---------------------------

# app.include_router(leads.router)
# app.include_router(health.router)
# app.include_router(costs.router)








import os

from anthropic import Anthropic
from dotenv import load_dotenv

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from src.api.middleware.correlation import CorrelationIDMiddleware #every every request gets corelation id

from src.api.routers import leads, health, costs
from src.utils.logger import configure_logging

# #================front end part============================================================
# # main.py
# from contextlib import asynccontextmanager
# import logging

# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates

# from src.api.middleware.correlation import CorrelationIDMiddleware
# from src.api.routers import leads, health, costs
# from src.utils.logger import configure_logging

# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     configure_logging()
#     logger.info("Lead Analyser API starting up")
#     yield
#     logger.info("Lead Analyser API shutting down")


# # ── 1. Create the app ──────────────────────────────
# app = FastAPI(
#     title="Lead Analyser API",
#     version="1.0.0",
#     description="Async lead analysis pipeline with Claude",
#     lifespan=lifespan,
# )

# # ── 2. Frontend (add these right after app = FastAPI) ──
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# @app.get("/", response_class=HTMLResponse)
# async def serve_ui(request: Request):
#     return templates.TemplateResponse(request=request, name="index.html")
   ##remeber to keep it this way only as it wont let frontend run then 
# # ── 3. Middleware ──────────────────────────────────
# app.add_middleware(CorrelationIDMiddleware)

# # ── 4. API routers ─────────────────────────────────
# app.include_router(leads.router)
# app.include_router(health.router)
# app.include_router(costs.router)





# #=================front end part end============================================================


logger = logging.getLogger(__name__)

def test_connection() -> None:
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found")

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence"
            }
        ],
    )

    text = "".join(
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    ).strip()

    print(text)

    usage = response.usage

    print("\n=== Token Usage ===")
    print(f"Input tokens  : {usage.input_tokens}")
    print(f"Output tokens : {usage.output_tokens}")

    # Optional fields
    if hasattr(usage, "cache_creation_input_tokens"):
        print(f"Cache write   : {usage.cache_creation_input_tokens}")

    if hasattr(usage, "cache_read_input_tokens"):
        print(f"Cache read    : {usage.cache_read_input_tokens}")


if __name__ == "__main__":
    test_connection()




client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
)
page = client.beta.models.list()
page = page.data[0]
print(page.id)









@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Lead Analyser API starting up")
    yield
    logger.info("Lead Analyser API shutting down")


app = FastAPI(
    title="Lead Analyser API",
    version="1.0.0",
    description="Async lead analysis pipeline with Claude",
    lifespan=lifespan,
)

# Middleware — must be added before routers
app.add_middleware(CorrelationIDMiddleware)

# Routers
app.include_router(leads.router)
app.include_router(health.router)
app.include_router(costs.router)