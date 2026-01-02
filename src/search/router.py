from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from src.commonlib import types as common_types
from src.commonlib.constants import API_ERROR_MESSAGE
from src.commonlib.logger import search_logger
from src.database.connection import get_db
from src.search import types as search_types

router = APIRouter(prefix="/thread")


@router.post("/")
async def create_thread(
    body: search_types.APIRequest, db: AsyncSession = Depends(get_db)
):
    try:
        pass
    except HTTPException as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=API_ERROR_MESSAGE,
        )


@router.get("/{thread_id}")
async def list_conversations(
    thread_id: UUID,
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of messages per page"),
    db: AsyncSession = Depends(get_db),
):
    try:
        pass
    except HTTPException as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=API_ERROR_MESSAGE,
        )


@router.delete("/{thread_id}")
async def delete_thread(thread_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        pass
    except HTTPException as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=API_ERROR_MESSAGE,
        )


@router.put("/{thread_id}")
async def update_thread(
    thread_id: UUID, body: search_types.APIRequest, db: AsyncSession = Depends(get_db)
):
    try:
        pass
    except HTTPException as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=API_ERROR_MESSAGE,
        )


@router.get("/s")
async def list_threads(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of messages per page"),
    db: AsyncSession = Depends(get_db),
):
    try:
        pass
    except HTTPException as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=API_ERROR_MESSAGE,
        )


@router.post("/{thread_id}/conversation/")
async def conversation(
    thread_id: UUID, body: search_types.APIRequest
) -> StreamingResponse:
    try:
        pass
    except HTTPException as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=API_ERROR_MESSAGE,
        )
