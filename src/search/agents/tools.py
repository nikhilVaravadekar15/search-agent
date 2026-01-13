import asyncio
from typing import Any, Dict, List, Optional

import httpx
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from pydantic import HttpUrl

from src.commonlib.async_crawl4AI_client import AsyncCrawl4AIClient
from src.commonlib.config import settings
from src.commonlib.logger import search_logger
from src.commonlib.types import Crawl4AIResponse
from src.search import types as search_types

crawl4ai_client = AsyncCrawl4AIClient()


async def scrape_webpage_content(url: HttpUrl) -> Optional[search_types.CompleteSource]:
    """Fetch and convert webpage content to markdown.

    Args:
        url (HttpUrl): URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Optional[search_types.Source]
    """
    try:
        try:
            c4ai_response: Crawl4AIResponse = await crawl4ai_client.scrape(url=url)

        except Exception as e:
            print(f"crawl4ai exception: {str(e)}")
            raise e

        if c4ai_response is not None and (
            c4ai_response.success is False or len(c4ai_response.results) == 0
        ):
            raise Exception("Failed to scrape the url")

        crawler_data = c4ai_response.results[0]

        if (
            crawler_data.markdown is not None
            and crawler_data.markdown.markdown_with_citations is not None
        ):
            metadata = crawler_data.metadata or {}

            title = (
                metadata.get("title")
                or metadata.get("og:title")
                or metadata.get("twitter:title")
                or "Untitled"
            )

            meta_description = (
                metadata.get("description")
                or metadata.get("og:description")
                or metadata.get("twitter:description")
            )

            return search_types.CompleteSource(
                title=title.strip(),
                url=url,
                description=meta_description,
                content=crawler_data.markdown.markdown_with_citations,
            )

        return None
    except httpx.TimeoutException as te:
        search_logger.error(
            f"Error fetching content, Search request timed out for {url}: {str(e)}"
        )
        raise te
    except httpx.HTTPError as he:
        search_logger.error(f"Error fetching content for {url}: {str(e)}")
        raise he
    except Exception as e:
        search_logger.error(f"Unexpected error during search for {url}: {str(e)}")
        raise e


@tool("internet_search", parse_docstring=True)
async def internet_search(query: str, runtime: ToolRuntime[Dict, Any]) -> ToolMessage:
    """
    Search the web for information on a given query.
    Uses brave search api to discover relevant URLs, then fetches and returns full webpage content as markdown.

    Args:
        query (str): Natural language question

    Returns:
        Toolmessage: message containing the semantic results with:
            - Comprehensive answer synthesized from multiple relevant websites
            - Source references
        Returns empty result if no relevant documents found or query cannot be processed.
    """

    params = {"api_key": settings.SCRAPER_API_KEY, "query": query}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(settings.SCRAPER_API_URL, params=params)
            search_logger.info(
                f"fetch web sources from internet with status_code: {response.status_code}"
            )
            response.raise_for_status()
            data = response.json()

            search_logger.info(data)

        urls: List[HttpUrl] = []
        tasks: List[asyncio.Task] = []
        results = []
        if isinstance(data, Dict):
            results = data.get("organic_results", [])
        for result in results:
            try:
                url = HttpUrl(result["link"])
                urls.append(url)
                search_logger.info(f"scraping webpage for url={url}")
                tasks.append(scrape_webpage_content(url=url))
            except Exception as e:
                search_logger.warning(f"Scaping error: {str(e)}")
                continue

        formatted_results: List[str] = []
        complete_sources: List[search_types.CompleteSource] = []
        webpages: List[Optional[search_types.Source] | BaseException] = (
            await asyncio.gather(*tasks, return_exceptions=True)
        )
        for webpage in webpages:
            if webpage is not None and not isinstance(webpage, Exception):
                complete_sources.append(webpage)
                tsource = ""
                for key, value in webpage:
                    if value:
                        tsource += f"{key}: {value}, \n"
                formatted_results.append(tsource)

        return ToolMessage(
            content=(
                "\n".join(formatted_results)
                if formatted_results
                else "No search results found for the query."
            ),
            name="internet_search",
            tool_call_id=runtime.tool_call_id,
            additional_kwargs={
                "sources": [
                    source.model_dump(
                        mode="json", exclude={"content"}, exclude_none=True
                    )
                    for source in complete_sources
                ]
            },
        )

    except httpx.TimeoutException:
        return ToolMessage(
            content="Search request timed out. Please try again.",
            name="internet_search",
            tool_call_id=runtime.tool_call_id,
        )
    except httpx.HTTPError as e:
        return ToolMessage(
            content=f"Search failed: {str(e)}",
            name="internet_search",
            tool_call_id=runtime.tool_call_id,
        )
    except Exception as e:
        return ToolMessage(
            content=f"Unexpected error during search: {str(e)}",
            name="internet_search",
            tool_call_id=runtime.tool_call_id,
        )


@tool("fetch_url_content", parse_docstring=True)
async def fetch_url_content(
    url: HttpUrl, runtime: ToolRuntime[Dict, Any]
) -> ToolMessage:
    """
    scrape the content of the webpage for a particular url

    Args:
        url (HttpUrl): A valid url

    Returns:
        Toolmessage: message containing the results with:
            - content
            - Source references
        Returns empty result if no relevant documents found or query cannot be processed.
    """

    try:
        result = await scrape_webpage_content(url=url)
        if result:
            tsource = ""
            for key, value in result:
                if value:
                    tsource += f"{key}: {value}, \n"
            return ToolMessage(
                content=tsource,
                name="fetch_url_content",
                tool_call_id=runtime.tool_call_id,
                additional_kwargs={
                    "sources": [
                        result.model_dump(
                            mode="json", exclude={"content"}, exclude_none=True
                        )
                    ]
                },
            )
        raise Exception("failed to scrape")
    except httpx.TimeoutException:
        return ToolMessage(
            content="Search request timed out. Please try again.",
            name="fetch_url_content",
            tool_call_id=runtime.tool_call_id,
        )
    except httpx.HTTPError as e:
        return ToolMessage(
            content=f"Search failed: {str(e)}",
            name="fetch_url_content",
            tool_call_id=runtime.tool_call_id,
        )
    except Exception as e:
        return ToolMessage(
            content=f"Unexpected error during search: {str(e)}",
            name="fetch_url_content",
            tool_call_id=runtime.tool_call_id,
        )


@tool("think_tool", parse_docstring=True)
def think_tool(reflection: str, runtime: ToolRuntime[Dict, Any]) -> ToolMessage:
    """
    Tool for strategic reflection on research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        reflection (str): Your detailed reflection on research progress, findings, gaps, and next steps

    Returns:
        ToolMessage: Confirmation that reflection was recorded for decision-making
    """
    return ToolMessage(
        content=f"Reflection recorded: {reflection}",
        name="think_tool",
        tool_call_id=runtime.tool_call_id,
    )
