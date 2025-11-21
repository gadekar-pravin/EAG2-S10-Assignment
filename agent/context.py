from mcp_servers.multiMCP import MultiMCP
from typing import Optional
from pydantic import BaseModel
import time
import uuid
from datetime import datetime

class StrategyProfile(BaseModel):
    """
    Defines the strategy profile for the agent.

    Attributes:
        planning_mode (str): The mode of planning (e.g., "exploratory").
        exploration_mode (Optional[str]): The mode of exploration, if applicable.
        memory_fallback_enabled (bool): Whether to fall back to memory if planning fails.
        max_steps (int): The maximum number of steps allowed for the agent.
        max_lifelines_per_step (int): The maximum number of retries allowed per step.
    """
    planning_mode: str
    exploration_mode: Optional[str] = None
    memory_fallback_enabled: bool
    max_steps: int
    max_lifelines_per_step: int

class AgentContext:
    """
    Maintains the context for an agent, including access to MCP tools.

    Attributes:
        mcp_context (Optional[MultiMCP]): The MultiMCP instance providing tool access.
    """
    def __init__(
        self,
        mcp_context: Optional[MultiMCP] = None,

    ):
        """
        Initialize the AgentContext.

        Args:
            mcp_context (Optional[MultiMCP]): The MultiMCP instance.
        """
        self.mcp_context = mcp_context
