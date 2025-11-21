import os
import sys
import asyncio
import json
from typing import Optional, Any, List, Dict
from inspect import signature
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ast

class MCP:
    """
    Represents a single MCP (Model Context Protocol) server connection.

    This class handles connecting to an MCP server, listing available tools,
    and calling tools on that server.
    """
    def __init__(
        self,
        server_script: str = "mcp_server_2.py",
        working_dir: Optional[str] = None,
        server_command: Optional[str] = None,
    ):
        """
        Initialize the MCP client.

        Args:
            server_script (str): The script to run the MCP server.
            working_dir (Optional[str]): The working directory for the server.
            server_command (Optional[str]): The command to run the server (defaults to sys.executable).
        """
        self.server_script = server_script
        self.working_dir = working_dir or os.getcwd()
        self.server_command = server_command or sys.executable

    async def list_tools(self):
        """
        Lists the tools available on the MCP server.

        Returns:
            list: A list of available tools.
        """
        server_params = StdioServerParameters(
            command=self.server_command,
            args=[self.server_script],
            cwd=self.working_dir
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                return tools_result.tools

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Calls a tool on the MCP server.

        Args:
            tool_name (str): The name of the tool to call.
            arguments (dict): The arguments to pass to the tool.

        Returns:
            Any: The result of the tool call.
        """
        server_params = StdioServerParameters(
            command=self.server_command,
            args=[self.server_script],
            cwd=self.working_dir
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments=arguments)

class MultiMCP:
    """
    Manages multiple MCP server connections and dispatches tool calls to the appropriate server.
    """
    def __init__(self, server_configs: List[dict]):
        """
        Initialize the MultiMCP manager.

        Args:
            server_configs (List[dict]): A list of configurations for each MCP server.
        """
        self.server_configs = server_configs
        self.tool_map: Dict[str, Dict[str, Any]] = {}
        self.server_tools: Dict[str, List[Any]] = {}

    async def initialize(self):
        """
        Initializes connections to all configured MCP servers and aggregates their tools.
        """
        print("in MultiMCP initialize")
        for config in self.server_configs:
            try:
                params = StdioServerParameters(
                    command=sys.executable,
                    args=[config["script"]],
                    cwd=config.get("cwd", os.getcwd())
                )
                print(f"→ Scanning tools from: {config['script']} in {params.cwd}")
                async with stdio_client(params) as (read, write):
                    print("Connection established, creating session...")
                    try:
                        async with ClientSession(read, write) as session:
                            print("[agent] Session created, initializing...")
                            await session.initialize()
                            print("[agent] MCP session initialized")
                            tools = await session.list_tools()
                            print(f"\n→ Tools received: {[tool.name for tool in tools.tools]}")
                            for tool in tools.tools:
                                self.tool_map[tool.name] = {
                                    "config": config,
                                    "tool": tool
                                }
                                server_key = config["id"]
                                if server_key not in self.server_tools:
                                    self.server_tools[server_key] = []
                                self.server_tools[server_key].append(tool)
                    except Exception as se:
                        print(f"❌ Session error: {se}")
            except Exception as e:
                print(f"❌ Error initializing MCP server {config['script']}: {e}")

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Calls a tool on the appropriate MCP server.

        Args:
            tool_name (str): The name of the tool to call.
            arguments (dict): The arguments for the tool.

        Returns:
            Any: The result from the tool call.

        Raises:
            ValueError: If the tool is not found on any server.
        """
        entry = self.tool_map.get(tool_name)
        if not entry:
            raise ValueError(f"Tool '{tool_name}' not found on any server.")

        config = entry["config"]
        params = StdioServerParameters(
            command=sys.executable,
            args=[config["script"]],
            cwd=config.get("cwd", os.getcwd())
        )

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments)



    async def function_wrapper(self, tool_name: str, *args):
        """
        Call a tool like a function with positional args OR a single string like 'add(45, 55)'.
        Returns the most relevant parsed result.

        Args:
            tool_name (str): The name of the tool (or function string).
            *args: Positional arguments for the tool.

        Returns:
            Any: The result of the tool execution.

        Raises:
            ValueError: If the function call format is invalid or tool not found.
        """
        # ── Handle LLM-style string input like: "add(45, 55) or ("send_email", ("a@b.com", "hello"))" ─────────────────
        # ── Handle string-form function call like "add(10, 20)" ──────────────
        if isinstance(tool_name, str) and len(args) == 0:
            stripped = tool_name.strip()
            if stripped.endswith(")") and "(" in stripped:
                try:
                    expr = ast.parse(stripped, mode='eval').body
                    if not isinstance(expr, ast.Call) or not isinstance(expr.func, ast.Name):
                        raise ValueError("Invalid function call format")
                    tool_name = expr.func.id
                    args = [ast.literal_eval(arg) for arg in expr.args]
                except Exception as e:
                    raise ValueError(f"Failed to parse function string '{tool_name}': {e}")


        # ── Look up tool ─────────────────────────────────────
        tool_entry = self.tool_map.get(tool_name)
        if not tool_entry:
            raise ValueError(f"Tool '{tool_name}' not found.")

        tool = tool_entry["tool"]
        schema = tool.inputSchema
        params = {}

        # ── Build input payload ──────────────────────────────
        if "input" in schema.get("properties", {}):
            inner_key = next(iter(schema.get("$defs", {})), None)
            inner_props = schema["$defs"][inner_key]["properties"]
            param_names = list(inner_props.keys())
            if len(param_names) != len(args):
                raise ValueError(f"{tool_name} expects {len(param_names)} args, got {len(args)}")
            params["input"] = dict(zip(param_names, args))
        else:
            param_names = list(schema["properties"].keys())
            if len(param_names) != len(args):
                raise ValueError(f"{tool_name} expects {len(param_names)} args, got {len(args)}")
            params = dict(zip(param_names, args))

        # ── Call and Normalize Output ────────────────────────
        result = await self.call_tool(tool_name, params)

        try:
            content_text = getattr(result, "content", [])[0].text.strip()
            parsed = json.loads(content_text)

            if isinstance(parsed, dict):
                if "result" in parsed:
                    return parsed["result"]
                if len(parsed) == 1:
                    return next(iter(parsed.values()))
                return parsed

            return parsed  # primitive type
        except Exception:
            return result  # fallback if parse fails



    def tool_description_wrapper(self) -> List[str]:
        """
        Formats tool usage examples for all available tools.

        Returns:
            List[str]: A list of formatted tool usage strings (e.g., "tool(type, type) # description").
        """
        examples = []
        for tool in self.get_all_tools():
            schema = tool.inputSchema
            if "input" in schema.get("properties", {}):
                inner_key = next(iter(schema.get("$defs", {})), None)
                props = schema["$defs"][inner_key]["properties"]
            else:
                props = schema["properties"]

            arg_types = []
            for k, v in props.items():
                t = v.get("type", "any")
                arg_types.append(t)

            signature_str = ", ".join(arg_types)
            examples.append(f"{tool.name}({signature_str})  # {tool.description}")
        return examples



    async def list_all_tools(self) -> List[str]:
        """
        Lists the names of all available tools across all servers.

        Returns:
            List[str]: A list of tool names.
        """
        return list(self.tool_map.keys())

    def get_all_tools(self) -> List[Any]:
        """
        Retrieves all tool objects from the map.

        Returns:
            List[Any]: A list of tool objects.
        """
        return [entry["tool"] for entry in self.tool_map.values()]

    def get_tools_from_servers(self, selected_servers: List[str]) -> List[Any]:
        """
        Retrieves tools belonging to specific servers.

        Args:
            selected_servers (List[str]): List of server IDs to retrieve tools from.

        Returns:
            List[Any]: A list of tool objects.
        """
        tools = []
        for server in selected_servers:
            if server in self.server_tools:
                tools.extend(self.server_tools[server])
        return tools

    async def shutdown(self):
        """
        Perform shutdown operations if needed.
        """
        pass
