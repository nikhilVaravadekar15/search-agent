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
        content = ApiResponse(status_code=status_code, msg=msg, data=data).model_dump()

        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            background=background,
        )

    def render(self, content: Any) -> bytes:
        return json.dumps(content).encode("utf-8")
