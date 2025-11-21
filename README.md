# Agentic AI Repository

## Overview

This repository contains the implementation of an **Agentic AI** system designed to perform complex tasks through a combination of perception, decision-making, and action execution. The system leverages Large Language Models (LLMs) to understand user queries, formulate plans, execute tools, and iteratively refine its approach based on feedback.

## Key Features

*   **Agentic Loop:** A robust feedback loop that cycles through Perception, Decision, and Action phases.
*   **Multi-MCP Support:** Integration with the Model Context Protocol (MCP) to allow the agent to use various external tools and servers.
*   **Perception Module:** Uses LLMs to analyze the current state, user queries, and tool outputs to form a structured understanding.
*   **Decision Module:** Generates and updates execution plans based on perception and strategy.
*   **Memory System:** Stores and retrieves past session logs to provide context and learn from previous interactions.
*   **Tool Execution:** A sandboxed executor for running code and calling external APIs safely.

## Project Structure

*   **`action/`**: Contains the `executor.py` which handles safe execution of code and tools.
*   **`agent/`**: Core agent logic, including the main loop (`agent_loop.py`), session management (`agentSession.py`), and context handling.
*   **`config/`**: Configuration files for models and profiles.
*   **`decision/`**: The decision-making engine that plans steps.
*   **`heuristics/`**: Heuristic rules for validation and safety checks.
*   **`mcp_servers/`**: Implementation of various MCP servers providing specific tools (e.g., math, search, file processing).
*   **`memory/`**: Logic for storing and searching session logs.
*   **`perception/`**: The module responsible for interpreting inputs and state.
*   **`prompts/`**: Text prompts used to guide the LLMs.
*   **`main.py`**: The entry point for running the interactive agent session.

## Setup

1.  **Prerequisites:**
    *   Python 3.11 or higher.
    *   Dependencies listed in `pyproject.toml`.

2.  **Installation:**
    ```bash
    pip install .
    # OR
    pip install -r requirements.txt # (if you generate one)
    ```

3.  **Configuration:**
    *   Create a `.env` file in the root directory and add your API keys (e.g., `GEMINI_API_KEY`).
    *   Review `config/profiles.yaml` and `config/mcp_server_config.yaml` to adjust agent settings and enabled tools.

## Usage

To start the interactive agent session, run:

```bash
python main.py
```

You will be prompted to enter a query. The agent will then proceed to analyze, plan, and execute tasks to fulfill your request, displaying its progress and reasoning along the way.

## Development

*   **Adding Tools:** Create a new MCP server script in `mcp_servers/` and register it in `config/mcp_server_config.yaml`.
*   **Modifying Prompts:** Edit the text files in `prompts/` to change the agent's behavior.
*   **Running Tests:** (Add instructions for running tests if available).

## License

[Add License Information Here]
