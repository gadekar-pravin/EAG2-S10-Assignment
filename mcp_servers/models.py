from pydantic import BaseModel, Field
from typing import List

# --- Math Tools ---

class AddInput(BaseModel):
    """Input model for addition operation."""
    a: int
    b: int

class AddOutput(BaseModel):
    """Output model for addition operation."""
    result: int

class SubtractInput(BaseModel):
    """Input model for subtraction operation."""
    a: int
    b: int

class SubtractOutput(BaseModel):
    """Output model for subtraction operation."""
    result: int

class MultiplyInput(BaseModel):
    """Input model for multiplication operation."""
    a: int
    b: int

class MultiplyOutput(BaseModel):
    """Output model for multiplication operation."""
    result: int

class SqrtInput(BaseModel):
    """Input model for square root operation."""
    a: int
    b: int

class SqrtOutput(BaseModel):
    """Output model for square root operation."""
    result: int

class DivideInput(BaseModel):
    """Input model for division operation."""
    a: int
    b: int

class DivideOutput(BaseModel):
    """Output model for division operation."""
    result: float

class PowerInput(BaseModel):
    """Input model for power operation."""
    a: int
    b: int

class PowerOutput(BaseModel):
    """Output model for power operation."""
    result: int

class CbrtInput(BaseModel):
    """Input model for cube root operation."""
    a: int

class CbrtOutput(BaseModel):
    """Output model for cube root operation."""
    result: float

class FactorialInput(BaseModel):
    """Input model for factorial operation."""
    a: int

class FactorialOutput(BaseModel):
    """Output model for factorial operation."""
    result: int

class RemainderInput(BaseModel):
    """Input model for remainder operation."""
    a: int
    b: int

class RemainderOutput(BaseModel):
    """Output model for remainder operation."""
    result: int

class SinInput(BaseModel):
    """Input model for sine operation."""
    a: int

class SinOutput(BaseModel):
    """Output model for sine operation."""
    result: float

class CosInput(BaseModel):
    """Input model for cosine operation."""
    a: int

class CosOutput(BaseModel):
    """Output model for cosine operation."""
    result: float

class TanInput(BaseModel):
    """Input model for tangent operation."""
    a: int

class TanOutput(BaseModel):
    """Output model for tangent operation."""
    result: float

class MineInput(BaseModel):
    """Input model for 'mine' operation."""
    a: int
    b: int

class MineOutput(BaseModel):
    """Output model for 'mine' operation."""
    result: int

# --- String & List Tools ---

class StringsToIntsInput(BaseModel):
    """Input model for converting string to integer list."""
    string: str

class StringsToIntsOutput(BaseModel):
    """Output model for converting string to integer list."""
    ascii_values: List[int]


class ExpSumInput(BaseModel):
    """Input model for exponential sum operation."""
    numbers: List[int]

class ExpSumOutput(BaseModel):
    """Output model for exponential sum operation."""
    result: float

class FibonacciInput(BaseModel):
    """Input model for generating Fibonacci numbers."""
    n: int

class FibonacciOutput(BaseModel):
    """Output model for generating Fibonacci numbers."""
    result: List[int]

# --- Image Tools ---

class CreateThumbnailInput(BaseModel):
    """Input model for creating an image thumbnail."""
    image_path: str

class ImageOutput(BaseModel):
    """Output model for image operations."""
    data: bytes
    format: str

# --- Shell, Python, SQL Tools ---

class PythonCodeInput(BaseModel):
    """Input model for executing Python code."""
    code: str

class PythonCodeOutput(BaseModel):
    """Output model for executing Python code."""
    result: str

class ShellCommandInput(BaseModel):
    """Input model for executing shell commands."""
    command: str

# --- RAG and Extraction Tools ---

class UrlInput(BaseModel):
    """Input model for URL-based operations."""
    url: str

class FilePathInput(BaseModel):
    """Input model for file path operations."""
    file_path: str

class MarkdownInput(BaseModel):
    """Input model for Markdown processing."""
    text: str

class MarkdownOutput(BaseModel):
    """Output model for Markdown processing."""
    markdown: str

class ChunkListOutput(BaseModel):
    """Output model for text chunking."""
    chunks: List[str]

# --- Memory Search ---

class SearchMemoryInput(BaseModel):
    """Input model for searching memory."""
    query: str

class EmptyInput(BaseModel):
    """Model for empty input."""
    pass

# --- Search Tools ---

class SearchInput(BaseModel):
    """Input model for search operations."""
    query: str
    max_results: int = Field(default=10, description="Maximum number of results to return")

class SearchDocumentsInput(BaseModel):
    """Input model for searching stored documents."""
    query: str
