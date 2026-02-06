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
from langgraph.graph.state import CompiledStateGraph

from src.commonlib import infra_state
from src.commonlib.config import settings
from src.commonlib.logger import search_logger
from src.search import types as search_types
from src.search.agents.prompts import (
    QUESTION_ANSWERING_INSTRUCTIONS,
    RESEARCHER_INSTRUCTIONS,
)
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
        self._agent_map: Dict[
            search_types.AGENT_TYPES, CompiledStateGraph[AgentState, Any]
        ] = {}
        self._checkpointer = infra_state.checkpointer
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

    def _create_agent(
        self, name: search_types.AGENT_TYPES
    ) -> CompiledStateGraph[AgentState, Any]:
        """
        Create agent for search queries (with full tool calling support).

        This agent has access to all legal search tools and must use them
        to answer legal questions.

        Args:
            name (AGENT_TYPES): name of the agent
        Return:
            agent (CompiledStateGraph)
        """
        tools = [think_tool]
        system_prompt = QUESTION_ANSWERING_INSTRUCTIONS.format(date=date.today())
        if name == "search":
            tools.append(internet_search)
            system_prompt = RESEARCHER_INSTRUCTIONS.format(date=date.today())

        agent = create_agent(
            name=f"{name}_agent",
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

    async def get_agent(
        self, name: search_types.AGENT_TYPES
    ) -> CompiledStateGraph[AgentState, Any]:
        """
        Thread-safe lazy initialization of legal agent.

        Args:
            name (AGENT_TYPES): name of the agent
        Returns:
            agent (CompiledStateGraph[AgentState, Any])
        """
        if name not in self._agent_map or self._agent_map[name] is None:
            async with self._async_lock:
                if name not in self._agent_map or self._agent_map[name] is None:
                    self._agent_map[name] = self._create_agent(name)
                    search_logger.info(f"Creating {name} agent")
                else:
                    search_logger.info(f"{name} agent already created")
        return self._agent_map[name]
