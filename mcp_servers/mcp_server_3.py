from mcp.server.fastmcp import FastMCP, Context
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import urllib.parse
import sys
import traceback
import asyncio
from datetime import datetime, timedelta
import time
import re
from pydantic import BaseModel, Field
from models import SearchInput, UrlInput
from models import PythonCodeOutput  # Import the models we need


@dataclass
class SearchResult:
    """
    Represents a single search result from DuckDuckGo.

    Attributes:
        title (str): The title of the search result.
        link (str): The URL of the search result.
        snippet (str): A brief summary or snippet from the result.
        position (int): The rank/position of the result in the list.
    """
    title: str
    link: str
    snippet: str
    position: int


class RateLimiter:
    """
    Implements a simple rate limiter to control request frequency.
    """
    def __init__(self, requests_per_minute: int = 30):
        """
        Initialize the RateLimiter.

        Args:
            requests_per_minute (int): Maximum allowed requests per minute.
        """
        self.requests_per_minute = requests_per_minute
        self.requests = []

    async def acquire(self):
        """
        Acquires permission to make a request, waiting if necessary to respect the rate limit.
        """
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [
            req for req in self.requests if now - req < timedelta(minutes=1)
        ]

        if len(self.requests) >= self.requests_per_minute:
            # Wait until we can make another request
            wait_time = 60 - (now - self.requests[0]).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        self.requests.append(now)


class DuckDuckGoSearcher:
    """
    Performs searches using DuckDuckGo (via HTML scraping).
    """
    BASE_URL = "https://html.duckduckgo.com/html"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self):
        """
        Initialize the DuckDuckGoSearcher with a rate limiter.
        """
        self.rate_limiter = RateLimiter()

    def format_results_for_llm(self, results: List[SearchResult]) -> str:
        """
        Formats search results into a natural language string suitable for LLM consumption.

        Args:
            results (List[SearchResult]): The list of search results.

        Returns:
            str: A formatted string containing the search results.
        """
        if not results:
            return "No results were found for your search query. This could be due to DuckDuckGo's bot detection or the query returned no matches. Please try rephrasing your search or try again in a few minutes."

        output = []
        output.append(f"Found {len(results)} search results:\n")

        for result in results:
            output.append(f"{result.position}. {result.title}")
            output.append(f"   URL: {result.link}")
            output.append(f"   Summary: {result.snippet}")
            output.append("")  # Empty line between results

        return "\n".join(output)

    async def search(
        self, query: str, ctx: Context, max_results: int = 10
    ) -> List[SearchResult]:
        """
        Performs a search on DuckDuckGo.

        Args:
            query (str): The search query.
            ctx (Context): The MCP context for logging.
            max_results (int): The maximum number of results to return.

        Returns:
            List[SearchResult]: A list of search results.
        """
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()

            # Create form data for POST request
            data = {
                "q": query,
                "b": "",
                "kl": "",
            }

            await ctx.info(f"Searching DuckDuckGo for: {query}")

            async with httpx.AsyncClient() as client:
                result = await client.post(
                    self.BASE_URL, data=data, headers=self.HEADERS, timeout=30.0
                )
                result.raise_for_status()

            # Parse HTML result
            soup = BeautifulSoup(result.text, "html.parser")
            if not soup:
                await ctx.error("Failed to parse HTML result")
                return []

            results = []
            for result in soup.select(".result"):
                title_elem = result.select_one(".result__title")
                if not title_elem:
                    continue

                link_elem = title_elem.find("a")
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                link = link_elem.get("href", "")

                # Skip ad results
                if "y.js" in link:
                    continue

                # Clean up DuckDuckGo redirect URLs
                if link.startswith("//duckduckgo.com/l/?uddg="):
                    link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])

                snippet_elem = result.select_one(".result__snippet")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                results.append(
                    SearchResult(
                        title=title,
                        link=link,
                        snippet=snippet,
                        position=len(results) + 1,
                    )
                )

                if len(results) >= max_results:
                    break

            await ctx.info(f"Successfully found {len(results)} results")
            return results

        except httpx.TimeoutException:
            await ctx.error("Search request timed out")
            return []
        except httpx.HTTPError as e:
            await ctx.error(f"HTTP error occurred: {str(e)}")
            return []
        except Exception as e:
            await ctx.error(f"Unexpected error during search: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return []


class WebContentFetcher:
    """
    Fetches and cleans textual content from webpages.
    """
    def __init__(self):
        """
        Initialize the WebContentFetcher with a rate limiter.
        """
        self.rate_limiter = RateLimiter(requests_per_minute=20)

    async def fetch_and_parse(self, url: str, ctx: Context) -> str:
        """
        Fetches content from a URL, parses the HTML, and extracts cleaned text.

        Args:
            url (str): The URL to fetch.
            ctx (Context): The MCP context for logging.

        Returns:
            str: The extracted text content or an error message.
        """
        try:
            await self.rate_limiter.acquire()

            await ctx.info(f"Fetching content from: {url}")

            async with httpx.AsyncClient() as client:
                result = await client.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    follow_redirects=True,
                    timeout=30.0,
                )
                result.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(result.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            # Get the text content
            text = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            # Remove extra whitespace
            text = re.sub(r"\s+", " ", text).strip()

            # Truncate if too long
            if len(text) > 8000:
                text = text[:8000] + "... [content truncated]"

            await ctx.info(
                f"Successfully fetched and parsed content ({len(text)} characters)"
            )
            return text

        except httpx.TimeoutException:
            await ctx.error(f"Request timed out for URL: {url}")
            return "Error: The request timed out while trying to fetch the webpage."
        except httpx.HTTPError as e:
            await ctx.error(f"HTTP error occurred while fetching {url}: {str(e)}")
            return f"Error: Could not access the webpage ({str(e)})"
        except Exception as e:
            await ctx.error(f"Error fetching content from {url}: {str(e)}")
            return f"Error: An unexpected error occurred while fetching the webpage ({str(e)})"


# Initialize FastMCP server
mcp = FastMCP("ddg-search")
searcher = DuckDuckGoSearcher()
fetcher = WebContentFetcher()


@mcp.tool()
async def duckduckgo_search_results(input: SearchInput, ctx: Context) -> PythonCodeOutput:
    """
    Performs a DuckDuckGo search and returns formatted results.

    Args:
        input (SearchInput): Object containing the 'query' and 'max_results'.
        ctx (Context): The MCP context.

    Returns:
        PythonCodeOutput: Object containing the formatted search results string.
    """
    try:
        results = await searcher.search(input.query, ctx, input.max_results)
        return PythonCodeOutput(result=searcher.format_results_for_llm(results))
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return f"An error occurred while searching: {str(e)}"


@mcp.tool()
async def download_raw_html_from_url(input: UrlInput, ctx: Context) -> PythonCodeOutput:
    """
    Downloads and parses the raw HTML content from a given URL.

    Args:
        input (UrlInput): Object containing the 'url' to fetch.
        ctx (Context): The MCP context.

    Returns:
        PythonCodeOutput: Object containing the parsed text content.
    """
    return PythonCodeOutput(result=await fetcher.fetch_and_parse(input.url, ctx))


if __name__ == "__main__":
    print("mcp_server_3.py starting")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
            mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
        print("\nShutting down...")
