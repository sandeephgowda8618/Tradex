from __future__ import annotations

from fastapi import FastAPI, Request
import uvicorn

from app.api.routes.analysis import router as analysis_router
from app.utils.logger import setup_logger
from app.utils.logger import get_logger
from app.db.session import engine
from app.models import Base


setup_logger()
app = FastAPI()
app.include_router(analysis_router)
logger = get_logger("request")


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


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
