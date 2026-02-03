import asyncio
import threading
from datetime import date
from typing import Any, Dict

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import (
    SummarizationMiddleware,
    TodoListMiddleware,
    ToolCallLimitMiddleware,
)
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph.state import CompiledStateGraph

from src.commonlib.config import settings
from src.commonlib.logger import search_logger
from src.search.agents.prompts import RESEARCHER_INSTRUCTIONS
from src.search.agents.tools import internet_search, think_tool


class AgentManager:
    """Manages agent lifecycle and streaming."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once (singleton pattern)
        if hasattr(self, "_initialized") and self._initialized:
            return

        # Create async lock for async operations
        self._async_lock = asyncio.Lock()
        self._search_agent: CompiledStateGraph[AgentState, Any] = None
        self._checkpointer = InMemorySaver(
            serde=JsonPlusSerializer(pickle_fallback=True)
        )
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            base_url=settings.MODEL_URL,
            api_key=settings.API_KEY,
            temperature=settings.MODEL_TEMPERATURE,
            profile={
                "max_input_tokens": settings.MAX_INPUT_TOKENS,
                "tool_calling": True,
                "structured_output": False,
            },
        )
        self._initialized = True

    def _create_agent(self) -> CompiledStateGraph[AgentState, Any]:
        """
        Create agent for search queries (with full tool calling support).

        This agent has access to all legal search tools and must use them
        to answer legal questions.

        Return:
            agent (CompiledStateGraph)
        """
        tools = [think_tool, internet_search]
        system_prompt = RESEARCHER_INSTRUCTIONS.format(date=date.today())

        agent = create_agent(
            name=settings.AGENT_NAME,
            model=self.llm,
            tools=tools,
            system_prompt=system_prompt,
            debug=True,
            checkpointer=self._checkpointer,
            middleware=[
                TodoListMiddleware(),
                ToolCallLimitMiddleware(run_limit=settings.TOOL_CALLING_LIMIT),
                SummarizationMiddleware(
                    model=self.llm,
                    trigger=("fraction", settings.SUMMERIZATION_MIDDLEWARE_LIMIT),
                ),
            ],
        )

        return agent

    async def get_agent(self) -> CompiledStateGraph[AgentState, Any]:
        """
        Thread-safe lazy initialization of legal agent.

        Returns:
            agent (CompiledStateGraph[AgentState, Any])
        """
        if self._search_agent is None:
            async with self._async_lock:
                if self._search_agent is None:
                    self._search_agent = self._create_agent()
                    search_logger.info(f"Creating {settings.AGENT_NAME} agent")
                else:
                    search_logger.info(f"{settings.AGENT_NAME} agent already created")
        return self._search_agent
