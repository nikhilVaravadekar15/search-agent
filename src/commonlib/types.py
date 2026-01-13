import json
from typing import Any, Dict, List, Literal, Mapping, Optional

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask


class ApiResponse(BaseModel):
    msg: Literal["success", "error"]
    status_code: int
    data: Optional[Dict | List[Dict]] = None


class ApiResponseModel(JSONResponse):
    media_type = "application/json"

    def __init__(
        self,
        *,
        msg: Literal["success", "error"],
        data: Optional[Dict | List[Dict]] = None,
        status_code: int = status.HTTP_200_OK,
        headers: Optional[Mapping[str, str]] = None,
        background: Optional[BackgroundTask] = None,
    ) -> None:
        # Build the complete response content here
        content = ApiResponse(status_code=status_code, msg=msg, data=data).model_dump(
            mode="json"
        )

        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            background=background,
        )

    def render(self, content: Any) -> bytes:
        return json.dumps(content).encode("utf-8")


# crawl4ai
class Crawl4AIMediaData(BaseModel):
    src: str
    alt: str
    type: str
    format: Optional[str] = None


class Crawl4AIMedia(BaseModel):
    images: List[Crawl4AIMediaData]
    videos: List[Crawl4AIMediaData]
    audios: List[Crawl4AIMediaData]


class Crawl4AILinkData(BaseModel):
    href: str
    text: str
    title: str
    base_domain: str


class Crawl4AILinks(BaseModel):
    internal: List[Crawl4AILinkData]
    external: List[Crawl4AILinkData]


class Crawl4AIMarkdown(BaseModel):
    markdown: Optional[str] = None
    markdown_with_citations: Optional[str] = None
    references_markdown: Optional[str] = None


class Crawl4AIResponseResult(BaseModel):
    url: str
    html: Optional[str] = None
    fit_html: Optional[str] = None
    success: bool
    cleaned_html: Optional[str] = None
    media: Crawl4AIMedia
    links: Crawl4AILinks
    metadata: Optional[dict] = None
    status_code: int
    markdown: Crawl4AIMarkdown


class Crawl4AIResponse(BaseModel):
    success: bool
    results: List[Crawl4AIResponseResult]
