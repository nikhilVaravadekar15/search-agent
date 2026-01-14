import httpx
from pydantic import HttpUrl

from src.commonlib.config import settings
from src.commonlib.logger import search_logger
from src.commonlib.types import Crawl4AIResponse


class AsyncCrawl4AIClient:
    def __init__(self, timeout: float = 100):
        self._base_url = settings.CRAWL4AI_HOST
        self._timeout = timeout

    async def scrape(self, url: HttpUrl) -> Crawl4AIResponse:
        """
        request to crawl4ai server

        Args:
            url (HttpUrl): website url to scrape
        Returns:
            Crawl4AIResponse: response from crawl4ai server
        Raises:
            asyncio.TimeoutError: if the request times out
            aiohttp.ClientError: if the request fails
        """
        payload = {
            "urls": [str(url)],
            "crawler_config": {
                "type": "CrawlerRunConfig",
                "params": {
                    "stream": False,
                },
            },
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(self._base_url, json=payload)
                response.raise_for_status()
                return Crawl4AIResponse(**response.json())
        except httpx.ConnectError as ce:
            search_logger.error(
                f"Failed to connect to Crawl4AI server at {self._base_url}: {ce}"
            )
            raise ce
        except httpx.TimeoutException as te:
            search_logger.error(f"Request to {url} timed out after {self._timeout}s")
            raise te
        except httpx.HTTPStatusError as he:
            search_logger.error(f"crawl4ai scraping error: {str(he)}")
            raise he
        except httpx.RequestError as re:
            search_logger.error(f"Unexpected client error: {str(re)}")
            raise re
        except Exception as e:  # Covers httpx.JsonDecodeError, ValueError, etc.
            search_logger.error(
                f"crawl4ai scraping error {type(e).__name__ }, {str(e)}"
            )
            raise e
