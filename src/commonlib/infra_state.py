# src/commonlib/infra_state.py

from typing import Any, Optional

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

checkpointer: Optional[AsyncPostgresSaver] = None
stream_manager: Optional[Any] = None
