from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from src.commonlib import types as common_types
from src.commonlib.constants import (
    API_ERROR_MESSAGE,
    SEARCH_JOB_CANCEL_ERROR,
    THREAD_DELETED_ERROR,
    THREAD_NOT_FOUND_ERROR,
)
from src.commonlib.logger import search_logger
from src.database.connection import get_db
from src.search import crud
from src.search import types as search_types
from src.search.agents.agent_manager import AgentManager

agent_manager = AgentManager()
router = APIRouter(prefix="/thread")


@router.get("/list")
async def list_threads(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of messages per page"),
    db: AsyncSession = Depends(get_db),
):
    try:
        count, threads = await crud.list_threads(db=db, page=page, page_size=page_size)
        print(count)

        return common_types.ApiResponseModel(
            status_code=status.HTTP_200_OK,
            msg="success",
            data={
                "threads": [
                    search_types.ConversationThread.model_validate(thread).model_dump()
                    for thread in threads
                ],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_threads": count,
                    "total_pages": (count + page_size - 1) // page_size,
                },
            },
        )
    except HTTPException as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=API_ERROR_MESSAGE,
        )


@router.post("/")
async def create_thread(
    body: search_types.APIRequest, db: AsyncSession = Depends(get_db)
):
    try:
        new_thread = await crud.create_thread(db=db, body=body)
        thread_model = search_types.ConversationThread.model_validate(new_thread)
        return common_types.ApiResponseModel(
            status_code=status.HTTP_200_OK,
            msg="success",
            data=thread_model.model_dump(),
        )
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
        db_thread = await crud.get_thread(db=db, thread_id=thread_id)
        if not db_thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=THREAD_NOT_FOUND_ERROR,
            )

        count, messages = await crud.list_conversations(
            db=db, thread_id=thread_id, page=page, page_size=page_size
        )

        return common_types.ApiResponseModel(
            status_code=status.HTTP_200_OK,
            msg="success",
            data={
                "messages": [
                    search_types.Message.model_validate(message).model_dump()
                    for message in messages
                ],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_threads": count,
                    "total_pages": (count + page_size - 1) // page_size,
                },
            },
        )
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
        db_thread = await crud.get_thread(db=db, thread_id=thread_id)
        if not db_thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=THREAD_NOT_FOUND_ERROR,
            )
        await crud.delete_thread(db=db, thread_id=thread_id)
        return common_types.ApiResponseModel(
            status_code=status.HTTP_200_OK,
            msg="success",
            data={"message": THREAD_DELETED_ERROR},
        )
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
        db_thread = await crud.get_thread(db=db, thread_id=thread_id)
        if not db_thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=THREAD_NOT_FOUND_ERROR,
            )
        new_thread = await crud.update_thread(db=db, thread=db_thread, body=body)
        thread_model = search_types.ConversationThread.model_validate(new_thread)
        return common_types.ApiResponseModel(
            status_code=status.HTTP_200_OK,
            msg="success",
            data=thread_model.model_dump(),
        )
    except HTTPException as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=API_ERROR_MESSAGE,
        )


@router.post("/{thread_id}/chat/completions")
async def conversation(
    request: Request, thread_id: UUID, body: search_types.ConversationAPIRequest
) -> StreamingResponse:
    try:
        user_message = None
        if body.context.type != search_types.FlowType.REGENERATE.value:
            user_message = await crud.create_message(
                thread_id=thread_id,
                role=search_types.MessageRole.USER,
                parent_message_id=body.parent_message_id,  # previous ai message
                query=body.query,
                follow_context=body.context.model_dump(mode="json"),
            )
            search_logger.info(
                f"Created message {search_types.MessageRole.USER.value} message_id={user_message.id} under thread_id={thread_id}"
            )

        ai_message = await crud.create_message(
            thread_id=thread_id,
            role=search_types.MessageRole.ASSISTANT,
            parent_message_id=(
                user_message.id
                if user_message and user_message.id
                else body.context.um_id
            ),  # previous human message
            query=None,
            follow_context=body.context.model_dump(mode="json"),
        )
        search_logger.info(
            f"Created message {search_types.MessageRole.ASSISTANT.value} message_id={ai_message.id} under thread_id={thread_id}"
        )

        generator = agent_manager.run(
            request=request,
            query=body.query,
            thread_id=thread_id,
            track_id=(
                user_message.id
                if user_message and user_message.id
                else body.parent_message_id
            ),
            um_id=(
                user_message.id
                if user_message and user_message.id
                else body.context.um_id
            ),
            aim_id=ai_message.id,  # ai message for next user message
            context=body.context,
        )
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
        )

    except HTTPException as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        search_logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=API_ERROR_MESSAGE,
        )


@router.post("/{thread_id}/chat/completions/stop")
async def stop_streaming_job(
    thread_id: UUID,
    body: search_types.APICancelRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to stop stream the output of a search job/message.
    Args:
        thread_id (UUID): thread id,
        body (APICancelRequest): The request body containing the message id.
    Raises:
        HTTPException: If the job/message not found
    """
    try:
        db_message = await crud.get_message(
            db=db, message_id=body.track_id, thread_id=thread_id
        )
        if not db_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        flag = await agent_manager.stop_stream_message(body.track_id)
        if not flag:
            search_logger.warning(
                f"Failed to stop job (may have been already cancelled) track_id={body.track_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stream job already cancelled",
            )

        return common_types.ApiResponseModel(
            status_code=status.HTTP_200_OK,
            msg="success",
            data={"message": SEARCH_JOB_CANCEL_ERROR},
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        search_logger.error(
            f"Failed to stop in streaming job, error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )
