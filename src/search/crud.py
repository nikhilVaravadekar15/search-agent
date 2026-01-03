from typing import List, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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


# async def add_message_to_thread(
#     db: AsyncSession,
#     thread_id: UUID,
#     role: str,
#     content: str,
#     error_message: str = None,
#     sources: dict = None,
# ) -> Message:
#     """Add a new message to an existing thread"""

#     # Verify thread exists
#     thread_result = await db.execute(
#         select(ConversationThread).where(ConversationThread.id == thread_id)
#     )
#     thread = thread_result.scalar_one_or_none()

#     if not thread:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Thread {thread_id} not found",
#         )

#     # Create new message
#     new_message = Message(
#         conversation_id=thread_id,
#         role=role,
#         content=content,
#         error_message=error_message,
#         sources=sources,
#     )
#     db.add(new_message)

#     # Update thread's updated_at timestamp
#     thread.updated_at = func.now()

#     await db.commit()
#     await db.refresh(new_message)

#     return new_message
