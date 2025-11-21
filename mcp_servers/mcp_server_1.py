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
    MultiplyInput, MultiplyOutput,
    DivideInput, DivideOutput,
    PowerInput, PowerOutput,
    CbrtInput, CbrtOutput,
    FactorialInput, FactorialOutput,
    RemainderInput, RemainderOutput,
    SinInput, SinOutput,
    CosInput, CosOutput,
    TanInput, TanOutput,
    MineInput, MineOutput,
    CreateThumbnailInput, ImageOutput,
    StringsToIntsInput, StringsToIntsOutput,
    ExpSumInput, ExpSumOutput,
    FibonacciInput, FibonacciOutput,
    PythonCodeInput, PythonCodeOutput,
    ShellCommandInput,
)

mcp = FastMCP("Calculator")

# ------------------- Tools -------------------

@mcp.tool()
def add(input: AddInput) -> AddOutput:
    """
    Adds two numbers.

    Args:
        input (AddInput): Object containing 'a' and 'b', the numbers to add.

    Returns:
        AddOutput: Object containing the 'result' of the addition.
    """
    print("CALLED: add(AddInput) -> AddOutput")
    return AddOutput(result=input.a + input.b)

@mcp.tool()
def subtract(input: SubtractInput) -> SubtractOutput:
    """
    Subtracts the second number from the first.

    Args:
        input (SubtractInput): Object containing 'a' (minuend) and 'b' (subtrahend).

    Returns:
        SubtractOutput: Object containing the 'result' of the subtraction.
    """
    print("CALLED: subtract(SubtractInput) -> SubtractOutput")
    return SubtractOutput(result=input.a - input.b)

@mcp.tool()
def multiply(input: MultiplyInput) -> MultiplyOutput:
    """
    Multiplies two integers.

    Args:
        input (MultiplyInput): Object containing 'a' and 'b', the numbers to multiply.

    Returns:
        MultiplyOutput: Object containing the 'result' of the multiplication.
    """
    print("CALLED: multiply(MultiplyInput) -> MultiplyOutput")
    return MultiplyOutput(result=input.a * input.b)

@mcp.tool()
def divide(input: DivideInput) -> DivideOutput:
    """
    Divides the first number by the second.

    Args:
        input (DivideInput): Object containing 'a' (numerator) and 'b' (denominator).

    Returns:
        DivideOutput: Object containing the 'result' of the division.
    """
    print("CALLED: divide(DivideInput) -> DivideOutput")
    return DivideOutput(result=input.a / input.b)

@mcp.tool()
def power(input: PowerInput) -> PowerOutput:
    """
    Computes the first number raised to the power of the second.

    Args:
        input (PowerInput): Object containing 'a' (base) and 'b' (exponent).

    Returns:
        PowerOutput: Object containing the 'result' of the exponentiation.
    """
    print("CALLED: power(PowerInput) -> PowerOutput")
    return PowerOutput(result=input.a ** input.b)

@mcp.tool()
def cbrt(input: CbrtInput) -> CbrtOutput:
    """
    Computes the cube root of a number.

    Args:
        input (CbrtInput): Object containing 'a', the number to compute the cube root of.

    Returns:
        CbrtOutput: Object containing the 'result' (cube root).
    """
    print("CALLED: cbrt(CbrtInput) -> CbrtOutput")
    return CbrtOutput(result=input.a ** (1/3))

@mcp.tool()
def factorial(input: FactorialInput) -> FactorialOutput:
    """
    Computes the factorial of a non-negative integer.

    Args:
        input (FactorialInput): Object containing 'a', the number to compute the factorial of.

    Returns:
        FactorialOutput: Object containing the 'result' (factorial).
    """
    print("CALLED: factorial(FactorialInput) -> FactorialOutput")
    return FactorialOutput(result=math.factorial(input.a))

@mcp.tool()
def remainder(input: RemainderInput) -> RemainderOutput:
    """
    Computes the remainder of the division of the first number by the second.

    Args:
        input (RemainderInput): Object containing 'a' (dividend) and 'b' (divisor).

    Returns:
        RemainderOutput: Object containing the 'result' (remainder).
    """
    print("CALLED: remainder(RemainderInput) -> RemainderOutput")
    return RemainderOutput(result=input.a % input.b)

@mcp.tool()
def sin(input: SinInput) -> SinOutput:
    """
    Computes the sine of an angle (in radians).

    Args:
        input (SinInput): Object containing 'a', the angle in radians.

    Returns:
        SinOutput: Object containing the 'result' (sine value).
    """
    print("CALLED: sin(SinInput) -> SinOutput")
    return SinOutput(result=math.sin(input.a))

@mcp.tool()
def cos(input: CosInput) -> CosOutput:
    """
    Computes the cosine of an angle (in radians).

    Args:
        input (CosInput): Object containing 'a', the angle in radians.

    Returns:
        CosOutput: Object containing the 'result' (cosine value).
    """
    print("CALLED: cos(CosInput) -> CosOutput")
    return CosOutput(result=math.cos(input.a))

@mcp.tool()
def tan(input: TanInput) -> TanOutput:
    """
    Computes the tangent of an angle (in radians).

    Args:
        input (TanInput): Object containing 'a', the angle in radians.

    Returns:
        TanOutput: Object containing the 'result' (tangent value).
    """
    print("CALLED: tan(TanInput) -> TanOutput")
    return TanOutput(result=math.tan(input.a))

@mcp.tool()
def mine(input: MineInput) -> MineOutput:
    """
    Performs a special mining operation (a - b - b).

    Args:
        input (MineInput): Object containing 'a' and 'b'.

    Returns:
        MineOutput: Object containing the 'result'.
    """
    print("CALLED: mine(MineInput) -> MineOutput")
    return MineOutput(result=input.a - input.b - input.b)

@mcp.tool()
def create_thumbnail(input: CreateThumbnailInput) -> ImageOutput:
    """
    Creates a 100x100 thumbnail from an image file.

    Args:
        input (CreateThumbnailInput): Object containing 'image_path', the path to the image.

    Returns:
        ImageOutput: Object containing the thumbnail 'data' (bytes) and 'format' ("png").
    """
    print("CALLED: create_thumbnail(CreateThumbnailInput) -> ImageOutput")
    img = PILImage.open(input.image_path)
    img.thumbnail((100, 100))
    return ImageOutput(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(input: StringsToIntsInput) -> StringsToIntsOutput:
    """
    Converts a string into a list of ASCII integer values.

    Args:
        input (StringsToIntsInput): Object containing 'string', the input string.

    Returns:
        StringsToIntsOutput: Object containing 'ascii_values', a list of integers.
    """
    print("CALLED: strings_to_chars_to_int(StringsToIntsInput) -> StringsToIntsOutput")
    ascii_values = [ord(char) for char in input.string]
    return StringsToIntsOutput(ascii_values=ascii_values)



@mcp.tool()
def int_list_to_exponential_sum(input: ExpSumInput) -> ExpSumOutput:
    """
    Calculates the sum of the exponentials of a list of integers.

    Args:
        input (ExpSumInput): Object containing 'numbers', a list of integers.

    Returns:
        ExpSumOutput: Object containing 'result', the sum of exponentials.
    """
    print("CALLED: int_list_to_exponential_sum(ExpSumInput) -> ExpSumOutput")
    result = sum(math.exp(i) for i in input.numbers)
    return ExpSumOutput(result=result)

@mcp.tool()
def fibonacci_numbers(input: FibonacciInput) -> FibonacciOutput:
    """
    Generates the first n Fibonacci numbers.

    Args:
        input (FibonacciInput): Object containing 'n', the count of Fibonacci numbers to generate.

    Returns:
        FibonacciOutput: Object containing 'result', a list of Fibonacci numbers.
    """
    print("CALLED: fibonacci_numbers(FibonacciInput) -> FibonacciOutput")
    n = input.n
    if n <= 0:
        return FibonacciOutput(result=[])
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return FibonacciOutput(result=fib_sequence[:n])



# @mcp.tool()
# def run_python_sandbox(input: PythonCodeInput) -> PythonCodeOutput:
#     """Run math code in Python sandbox. """
#     allowed_globals = {"__builtins__": __builtins__}
#     local_vars = {}

#     stdout_backup = sys.stdout
#     output_buffer = StringIO()
#     sys.stdout = output_buffer

#     try:
#         exec(input.code, allowed_globals, local_vars)
#         sys.stdout = stdout_backup
#         result = local_vars.get("result", output_buffer.getvalue().strip() or "Executed.")
#         return PythonCodeOutput(result=str(result))
#     except Exception as e:
#         sys.stdout = stdout_backup
#         return PythonCodeOutput(result=f"ERROR: {e}")

# @mcp.tool()
# def run_shell_command(input: ShellCommandInput) -> PythonCodeOutput:
#     """Run a safe shell command. """
#     allowed_commands = ["ls", "cat", "pwd", "df", "whoami"]

#     tokens = input.command.strip().split()
#     if tokens[0] not in allowed_commands:
#         return PythonCodeOutput(result="Command not allowed.")

#     try:
#         result = subprocess.run(
#             input.command, shell=True,
#             capture_output=True, timeout=3
#         )
#         output = result.stdout.decode() or result.stderr.decode()
#         return PythonCodeOutput(result=output.strip())
#     except Exception as e:
#         return PythonCodeOutput(result=f"ERROR: {e}")

# @mcp.tool()
# def run_sql_query(input: PythonCodeInput) -> PythonCodeOutput:
#     """Run safe SELECT-only SQL query. """
#     if not input.code.strip().lower().startswith("select"):
#         return PythonCodeOutput(result="Only SELECT queries allowed.")

#     try:
#         conn = sqlite3.connect("example.db")
#         cursor = conn.cursor()
#         cursor.execute(input.code)
#         rows = cursor.fetchall()
#         result = "\n".join(str(row) for row in rows)
#         return PythonCodeOutput(result=result or "No results.")
#     except Exception as e:
#         return PythonCodeOutput(result=f"ERROR: {e}")

# ------------------- Resources -------------------

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    Generates a personalized greeting resource.

    Args:
        name (str): The name to include in the greeting.

    Returns:
        str: A greeting string.
    """
    print("CALLED: get_greeting(name: str) -> str")
    return f"Hello, {name}!"

# ------------------- Prompts -------------------

@mcp.prompt()
def review_code(code: str) -> str:
    """
    Creates a prompt to ask the assistant to review code.

    Args:
        code (str): The code snippet to review.

    Returns:
        str: The prompt string.
    """
    return f"Please review this code:\n\n{code}"

@mcp.prompt()
def debug_error(error: str) -> list:
    """
    Creates a prompt to help debug an error.

    Args:
        error (str): The error message to debug.

    Returns:
        list: A list of message objects representing the conversation starter.
    """
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

# ------------------- Main -------------------

if __name__ == "__main__":
    print("mcp_server_1.py starting")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
        print("\nShutting down...")
