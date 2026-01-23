from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException
from langchain_core.messages import ai
from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.commonlib.constants import API_ERROR_MESSAGE
from src.database.connection import AsyncSessionLocal
from src.database.model import ConversationThread, Message
from src.search import types as search_types


async def create_thread(
    db: AsyncSession, body: search_types.APIRequest
) -> ConversationThread:
    """Create a new conversation thread with an initial user message"""

    # Create the thread
    new_thread = ConversationThread(
        title=(f"{body.query[:100]}..." if len(body.query) > 100 else body.query)
    )
    db.add(new_thread)
    await db.commit()
    await db.refresh(new_thread)
    return new_thread


async def get_thread(
    db: AsyncSession,
    thread_id: UUID,
) -> ConversationThread:
    # Verify thread exists
    return (
        await db.execute(
            select(ConversationThread).where(ConversationThread.id == thread_id)
        )
    ).scalar_one_or_none()


async def list_conversations(
    db: AsyncSession, thread_id: UUID, page: int, page_size: int
) -> Tuple[int, List[Message]]:
    """List all messages in a conversation with pagination"""
    # Get total count
    total_count = (
        await db.execute(
            select(func.count(Message.id)).where(Message.conversation_id == thread_id)
        )
    ).scalar()

    # Get paginated messages
    messages = (
        (
            await db.execute(
                select(Message)
                .where(Message.conversation_id == thread_id)
                .order_by(Message.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        .scalars()
        .all()
    )

    return total_count, reversed(messages)


async def delete_thread(db: AsyncSession, thread_id: UUID):
    """Delete a conversation thread and all its messages"""
    # Delete the thread
    await db.execute(
        sql_delete(ConversationThread).where(ConversationThread.id == thread_id)
    )
    await db.commit()


async def update_thread(
    db: AsyncSession, thread: ConversationThread, body: search_types.APIRequest
) -> ConversationThread:
    """Update thread title (or add a new message to the thread)"""
    thread.title = body.query[:100] if len(body.query) > 100 else body.query
    await db.commit()
    await db.refresh(thread)
    return thread


async def list_threads(
    db: AsyncSession, page: int = 1, page_size: int = 10
) -> Tuple[int, List[ConversationThread]]:
    """List all conversations/threads with pagination"""
    # Get total count
    total_count = (await db.execute(select(func.count(ConversationThread.id)))).scalar()

    # Get paginated threads
    threads = (
        (
            await db.execute(
                select(ConversationThread)
                .order_by(ConversationThread.updated_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        .scalars()
        .all()
    )

    return total_count, threads


async def create_message(
    thread_id: UUID,
    role: search_types.MessageRole,
    parent_message_id: Optional[UUID],
    query: Optional[str] = None,
    follow_context: Optional[search_types.FollowContext] = None,
) -> Message:
    """Create a new message under thread with an initial user message"""
    async with AsyncSessionLocal() as session:
        try:
            new_message = Message(
                conversation_id=thread_id,
                content=query,
                role=role,
                parent_id=parent_message_id,
                follow_context=(
                    follow_context.model_dump(mode="json") if follow_context else None
                ),
            )
            session.add(new_message)
            await session.commit()
            await session.refresh(new_message)
            return new_message
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def update_aimessage_in_thread(
    thread_id: UUID,
    message_id: UUID,
    content: Optional[str] = None,
    error_message: Optional[str] = None,
    sources: Optional[dict] = None,
) -> Message:
    """Add a new message to an existing thread"""
    async with AsyncSessionLocal() as session:
        try:

            ai_message = (
                await session.execute(
                    select(Message).where(
                        Message.id == message_id, Message.conversation_id == thread_id
                    )
                )
            ).scalar_one_or_none()
            if not ai_message:
                raise HTTPException(status_code=500, detail=API_ERROR_MESSAGE)

            # Update the message
            ai_message.content = content
            ai_message.error_message = error_message
            ai_message.sources = sources

            await session.commit()
            await session.refresh(ai_message)
            return ai_message
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
