from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.commonlib.config import settings
from src.commonlib.logger import search_logger
from src.health_check.router import router as health_check_router_v1

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_check_router_v1, prefix="/api/v1")

search_logger.info("Application started")
