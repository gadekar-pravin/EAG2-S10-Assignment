from dataclasses import dataclass, asdict
from typing import Any, Literal, Optional
import uuid
import time
import json

@dataclass
class ToolCode:
    """
    Represents code execution involving a specific tool.

    Attributes:
        tool_name (str): The name of the tool to be executed.
        tool_arguments (dict[str, Any]): A dictionary of arguments for the tool.
    """
    tool_name: str
    tool_arguments: dict[str, Any]

    def to_dict(self):
        """
        Converts the ToolCode instance to a dictionary.

        Returns:
            dict: A dictionary representation of the ToolCode instance.
        """
        return {
            "tool_name": self.tool_name,
            "tool_arguments": self.tool_arguments
        }


@dataclass
class PerceptionSnapshot:
    """
    Snapshot of the agent's perception at a specific point in time.

    Attributes:
        entities (list[str]): List of entities identified in the context.
        result_requirement (str): The requirement for the result.
        original_goal_achieved (bool): Whether the original user goal has been achieved.
        reasoning (str): Reasoning behind the current perception.
        local_goal_achieved (bool): Whether the local/immediate goal has been achieved.
        local_reasoning (str): Reasoning specific to the local goal.
        last_tooluse_summary (str): Summary of the last tool usage.
        solution_summary (str): Summary of the proposed solution.
        confidence (str): Confidence level in the current perception.
    """
    entities: list[str]
    result_requirement: str
    original_goal_achieved: bool
    reasoning: str
    local_goal_achieved: bool
    local_reasoning: str
    last_tooluse_summary: str
    solution_summary: str
    confidence: str

@dataclass
class Step:
    """
    Represents a single step in the agent's plan.

    Attributes:
        index (int): The index of the step in the plan.
        description (str): A description of what the step involves.
        type (Literal["CODE", "CONCLUDE", "NOOP"]): The type of step (code execution, conclusion, or no-op).
        code (Optional[ToolCode]): The tool code to execute, if applicable.
        conclusion (Optional[str]): The conclusion reached, if applicable.
        execution_result (Optional[str]): The result of the execution.
        error (Optional[str]): Any error encountered during execution.
        perception (Optional[PerceptionSnapshot]): The perception snapshot after the step.
        status (Literal["pending", "completed", "failed", "skipped"]): The current status of the step.
        attempts (int): Number of attempts made for this step.
        was_replanned (bool): Whether this step was a result of replanning.
        parent_index (Optional[int]): The index of the parent step, if replanned.
    """
    index: int
    description: str
    type: Literal["CODE", "CONCLUDE", "NOOP"]
    code: Optional[ToolCode] = None
    conclusion: Optional[str] = None
    execution_result: Optional[str] = None
    error: Optional[str] = None
    perception: Optional[PerceptionSnapshot] = None
    status: Literal["pending", "completed", "failed", "skipped"] = "pending"
    attempts: int = 0
    was_replanned: bool = False
    parent_index: Optional[int] = None

    def to_dict(self):
        """
        Converts the Step instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Step instance.
        """
        return {
            "index": self.index,
            "description": self.description,
            "type": self.type,
            "code": self.code.to_dict() if self.code else None,
            "conclusion": self.conclusion,
            "execution_result": self.execution_result,
            "error": self.error,
            "perception": self.perception.__dict__ if self.perception else None,
            "status": self.status,
            "attempts": self.attempts,
            "was_replanned": self.was_replanned,
            "parent_index": self.parent_index
        }


class AgentSession:
    """
    Manages the session state for an agent execution.

    Attributes:
        session_id (str): Unique identifier for the session.
        original_query (str): The initial user query.
        perception (Optional[PerceptionSnapshot]): The most recent perception snapshot.
        plan_versions (list[dict[str, Any]]): History of plan versions generated during the session.
        state (dict): Current state summary including goal achievement and final answer.
    """

    def __init__(self, session_id: str, original_query: str):
        """
        Initialize a new AgentSession.

        Args:
            session_id (str): The unique ID for this session.
            original_query (str): The user's original query.
        """
        self.session_id = session_id
        self.original_query = original_query
        self.perception: Optional[PerceptionSnapshot] = None
        self.plan_versions: list[dict[str, Any]] = []
        self.state = {
            "original_goal_achieved": False,
            "final_answer": None,
            "confidence": 0.0,
            "reasoning_note": "",
            "solution_summary": ""

        }

    def add_perception(self, snapshot: PerceptionSnapshot):
        """
        Updates the current perception snapshot of the session.

        Args:
            snapshot (PerceptionSnapshot): The new perception snapshot.
        """
        self.perception = snapshot

    def add_plan_version(self, plan_texts: list[str], steps: list[Step]):
        """
        Adds a new version of the plan to the session history.

        Args:
            plan_texts (list[str]): Textual descriptions of the plan steps.
            steps (list[Step]): List of Step objects corresponding to the plan.

        Returns:
            Step: The first step of the new plan, or None if empty.
        """
        plan = {
            "plan_text": plan_texts,
            "steps": steps.copy()
        }
        self.plan_versions.append(plan)
        return steps[0] if steps else None  # ✅ fix: return first Step

    def get_next_step_index(self) -> int:
        """
        Calculates the next global step index based on all previous plan versions.

        Returns:
            int: The cumulative count of steps across all plan versions.
        """
        return sum(len(v["steps"]) for v in self.plan_versions)


    def to_json(self):
        """
        Serializes the entire session state to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representing the full session state.
        """
        return {
            "session_id": self.session_id,
            "original_query": self.original_query,
            "perception": asdict(self.perception) if self.perception else None,
            "plan_versions": [
                {
                    "plan_text": p["plan_text"],
                    "steps": [asdict(s) for s in p["steps"]]
                } for p in self.plan_versions
            ],
            "state_snapshot": self.get_snapshot_summary()
        }

    def get_snapshot_summary(self):
        """
        Generates a summary of the current session state.

        Returns:
            dict: A dictionary containing key session metrics and the final plan.
        """
        return {
            "session_id": self.session_id,
            "query": self.original_query,
            "final_plan": self.plan_versions[-1]["plan_text"] if self.plan_versions else [],
           "final_steps": [
                    asdict(s)
                    for version in self.plan_versions
                    for s in version["steps"]
                    if s.status == "completed"
                ],
            "final_answer": self.state["final_answer"],
            "confidence": self.state["confidence"],
            "reasoning_note": self.state["reasoning_note"]
        }

    def mark_complete(self, perception: PerceptionSnapshot, final_answer: Optional[str] = None, fallback_confidence: float = 0.95):
        """
        Marks the session as complete and updates the final state.

        Args:
            perception (PerceptionSnapshot): The final perception snapshot.
            final_answer (Optional[str]): The final answer string (overrides perception if provided).
            fallback_confidence (float): Default confidence if perception lacks one.
        """
        self.state.update({
            "original_goal_achieved": perception.original_goal_achieved,
            "final_answer": final_answer or perception.solution_summary,
            "confidence": perception.confidence or fallback_confidence,
            "reasoning_note": perception.reasoning,
            "solution_summary": perception.solution_summary
        })



    def simulate_live(self, delay: float = 1.2):
        """
        Simulates a live replay of the agent session trace to the console.

        Args:
            delay (float): The delay in seconds between printing steps.
        """
        print("\n=== LIVE AGENT SESSION TRACE ===")
        print(f"Session ID: {self.session_id}")
        print(f"Query: {self.original_query}")
        time.sleep(delay)

        if self.perception:
            print("\n[Perception 0] Initial ERORLL:")
            print(f"  {asdict(self.perception)}")
            time.sleep(delay)

        for i, version in enumerate(self.plan_versions):
            print(f"\n[Decision Plan Text: V{i+1}]:")
            for j, p in enumerate(version["plan_text"]):
                print(f"  Step {j}: {p}")
            time.sleep(delay)

            for step in version["steps"]:
                print(f"\n[Step {step.index}] {step.description}")
                time.sleep(delay / 1.5)

                print(f"  Type: {step.type}")
                if step.code:
                    print(f"  Tool → {step.code.tool_name} | Args → {step.code.tool_arguments}")
                if step.execution_result:
                    print(f"  Execution Result: {step.execution_result}")
                if step.conclusion:
                    print(f"  Conclusion: {step.conclusion}")
                if step.error:
                    print(f"  Error: {step.error}")
                if step.perception:
                    print("  Perception ERORLL:")
                    for k, v in asdict(step.perception).items():
                        print(f"    {k}: {v}")
                print(f"  Status: {step.status}")
                if step.was_replanned:
                    print(f"  (Replanned from Step {step.parent_index})")
                if step.attempts > 1:
                    print(f"  Attempts: {step.attempts}")
                time.sleep(delay)

        print("\n[Session Snapshot]:")
        print(json.dumps(self.get_snapshot_summary(), indent=2))
