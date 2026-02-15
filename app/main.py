from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes.analysis import router as analysis_router
from app.utils.env import load_env_file
from app.utils.logger import setup_logger, get_logger
from app.db.session import engine
from app.models import Base


load_env_file()
setup_logger()
app = FastAPI()
app.include_router(analysis_router)
logger = get_logger("request")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    method = request.method
    url = str(request.url)
    logger.info("Request start | %s %s", method, url)
    try:
        response = await call_next(request)
        logger.info("Request end | %s %s | status=%s", method, url, response.status_code)
        return response
    except Exception:
        logger.exception("Request failed | %s %s", method, url)
        raise


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception | %s %s", request.method, request.url)
    raise exc


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
