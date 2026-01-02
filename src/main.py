import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.commonlib.config import settings
from src.commonlib.logger import search_logger

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_logger.info("Application started")

