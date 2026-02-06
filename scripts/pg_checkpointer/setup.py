"""
PostgreSQL checkpointer for LangGraph agent state persistence.
"""

import asyncio
import sys
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

print(settings.psycopg_dsn_checkpoint)


async def checkpointer_setup() -> AsyncGenerator[AsyncPostgresSaver, None]:
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

        saver = AsyncPostgresSaver(
            conn=conn,
            serde=serde,
        )
        print("Setting up checkpointer tables...")
        await saver.setup()
        print("Checkpointer tables created successfully!")


if __name__ == "__main__":
    asyncio.run(checkpointer_setup())

# python scripts/pg_checkpointer/setup.py
