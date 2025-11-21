from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import os
import json
import faiss
import numpy as np
from pathlib import Path
import requests
import subprocess
import sqlite3
from io import StringIO
from tqdm import tqdm
import hashlib

# Models
from models import (
    AddInput, AddOutput,
    SubtractInput, SubtractOutput,
    CbrtInput, CbrtOutput,
    FactorialInput, FactorialOutput,
    RemainderInput, RemainderOutput,
    SinInput, SinOutput,
    CosInput, CosOutput,
    TanInput, TanOutput,
    MineInput, MineOutput,
    CreateThumbnailInput, ImageOutput,
    StringsToIntsInput, StringsToIntsOutput,
    ExpSumInput, ExpSumOutput
)

mcp = FastMCP("Mixed 4")

@mcp.tool()
def add(input: AddInput) -> AddOutput:
    """
    Adds two numbers.

    Args:
        input (AddInput): Object containing 'a' and 'b'.

    Returns:
        AddOutput: Object containing the 'result'.
    """
    print("CALLED: add(AddInput) -> AddOutput")
    return AddOutput(result=input.a + input.b)

@mcp.tool()
def subtract(input: SubtractInput) -> SubtractOutput:
    """
    Subtracts the second number from the first.

    Args:
        input (SubtractInput): Object containing 'a' and 'b'.

    Returns:
        SubtractOutput: Object containing the 'result'.
    """
    print("CALLED: subtract(SubtractInput) -> SubtractOutput")
    return SubtractOutput(result=input.a - input.b)

@mcp.tool()
def multiply(a, b):
    """
    Multiplies two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The product of a and b.
    """
    print("CALLED: multiply(a, b) -> result")
    return a * b

@mcp.tool()
def no_input():
    """
    A test function that takes no input.

    Returns:
        str: A greeting string.
    """
    print("CALLED: multiply(a, b) -> result")
    return "hello"

@mcp.tool()
def int_list_to_exponential_sum(input: ExpSumInput) -> ExpSumOutput:
    """
    Calculates the sum of exponentials of a list of integers.

    Args:
        input (ExpSumInput): Object containing 'numbers', a list of integers.

    Returns:
        ExpSumOutput: Object containing the 'result'.
    """
    print("CALLED: int_list_to_exponential_sum(ExpSumInput) -> ExpSumOutput")
    result = sum(math.exp(i) for i in input.numbers)  # ✅ FIXED
    return ExpSumOutput(result=result)


@mcp.tool()
def strings_to_chars_to_int(input: StringsToIntsInput) -> StringsToIntsOutput:
    """
    Converts a string to a list of ASCII values.

    Args:
        input (StringsToIntsInput): Object containing 'string'.

    Returns:
        StringsToIntsOutput: Object containing 'ascii_values'.
    """
    print("CALLED: strings_to_chars_to_int(StringsToIntsInput) -> StringsToIntsOutput")
    ascii_values = [ord(char) for char in input.string]
    return StringsToIntsOutput(ascii_values=ascii_values)

# ------------------- Main -------------------

if __name__ == "__main__":
    print("mcp_server_4.py starting")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
        print("\nShutting down...")
