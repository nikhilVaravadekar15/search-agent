"""
PostgreSQL checkpointer for LangGraph agent state persistence.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from psycopg.rows import dict_row
from psycopg_pool.pool_async import AsyncConnectionPool

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

from src.commonlib.config import settings

# load environment variables from .env file
load_dotenv()


# Create encrypted serializer for secure state storage
serde = EncryptedSerializer.from_pycryptodome_aes()


@asynccontextmanager
async def checkpointer_lifespan() -> AsyncGenerator[AsyncPostgresSaver, None]:
    """
    Lifespan context that creates ONE AsyncPostgresSaver
    for the entire app lifetime.
    """
    async with AsyncConnectionPool(
        conninfo=settings.psycopg_dsn_checkpoint,
        kwargs={
            "autocommit": True,
            "prepare_threshold": 0,
            "row_factory": dict_row,
        },
    ) as pool, pool.connection() as conn:

        checkpointer = AsyncPostgresSaver(
            conn=conn,
            serde=serde,
        )
        yield checkpointer
