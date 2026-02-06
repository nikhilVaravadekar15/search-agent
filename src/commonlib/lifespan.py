# lifespan.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.commonlib.logger import search_logger
from src.commonlib.postgres_checkpointer import checkpointer_lifespan
from src.search.agents.stream_manager import StreamManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with checkpointer_lifespan() as checkpointer:

        from src.commonlib import infra_state as state

        state.checkpointer = checkpointer
        state.stream_manager = StreamManager()
        search_logger.info("Infrastructure initialized successfully")

        yield

        # Cleanup
        state.stream_manager = None
        state.checkpointer = None
        search_logger.info("Shutting down application successfully")
