from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.commonlib import types as common_types
from src.commonlib.config import settings
from src.commonlib.logger import search_logger
from src.health_check.router import router as health_check_router_v1
from src.search.router import router as search_router_v1

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Handle Starlette HTTP exceptions (like 404 for non-existent routes)
@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    return common_types.ApiResponseModel(
        status_code=exc.status_code,
        msg="error",
        data={
            "detail": exc.detail,
            "path": request.url.path,
            "error": "Route not found" if exc.status_code == 404 else "HTTP error",
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return common_types.ApiResponseModel(
        status_code=exc.status_code,
        msg="error",
        data={"detail": exc.detail, "path": request.url.path},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    search_logger.error(f"Unhandled error: {exc}", exc_info=True)
    return common_types.ApiResponseModel(
        status_code=exc.status_code,
        msg="error",
        data={"detail": exc.detail, "path": request.url.path},
    )


app.include_router(health_check_router_v1, prefix="/api/v1")
app.include_router(search_router_v1, prefix="/api/v1")

search_logger.info("Application started")
