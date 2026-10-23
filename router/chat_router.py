from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from database import get_chat_collection, get_message_collection
from services.llm_service import llm_service
from router.schemas import (
    CreateChatRequest,
    CreateChatResponse,
    ChatSessionResponse,
    ChatMessageResponse,
    SendMessageRequest,
    SendMessageResponse,
    DeleteChatResponse
)

router = APIRouter(prefix="/chats", tags=["Chats"])


# -------------------------------------------------------------
# Helper: MongoDB ObjectId Filter
# -------------------------------------------------------------
def get_chat_filter(chat_id: str) -> dict:
    """Build query filter supporting both ObjectId and string IDs."""
    clean_id = chat_id.strip()
    return {"_id": ObjectId(clean_id)} if ObjectId.is_valid(clean_id) else {"_id": clean_id}


# -------------------------------------------------------------
# 1. Create New Chat Session
# -------------------------------------------------------------
@router.post(
    "/new",
    response_model=CreateChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation session"
)
async def create_new_chat(payload: CreateChatRequest):
    """
    Accepts user_id, creates a new chat document in MongoDB (chats collection)
    with default title 'New Conversation' and timestamp, returns chat session details.
    """
    chats = get_chat_collection()
    user_id = payload.user_id.strip()

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required to create a chat session."
        )

    now = datetime.now(timezone.utc)
    new_chat = {
        "user_id": user_id,
        "title": "New Conversation",
        "created_at": now,
        "updated_at": now
    }

    result = await chats.insert_one(new_chat)

    return CreateChatResponse(
        chat_id=str(result.inserted_id),
        title=new_chat["title"],
        created_at=now.isoformat()
    )


# -------------------------------------------------------------
# 2. Fetch All Chat Sessions for a User
# -------------------------------------------------------------
@router.get(
    "/{user_id}",
    response_model=List[ChatSessionResponse],
    summary="Fetch all chat sessions for a specified user"
)
async def get_user_chats(user_id: str):
    """
    Fetches all chat sessions for the specified user_id,
    sorted descending by creation time.
    """
    chats = get_chat_collection()
    cursor = chats.find({"user_id": user_id.strip()}).sort("created_at", -1)
    documents = await cursor.to_list(length=1000)

    chat_sessions = []
    for doc in documents:
        created_at_val = doc.get("created_at")
        created_at_str = created_at_val.isoformat() if created_at_val else None

        chat_sessions.append(
            ChatSessionResponse(
                chat_id=str(doc["_id"]),
                user_id=doc.get("user_id", user_id),
                title=doc.get("title", "New Conversation"),
                created_at=created_at_str
            )
        )

    return chat_sessions


# -------------------------------------------------------------
# 3. Fetch Message History for a Chat Session
# -------------------------------------------------------------
@router.get(
    "/{chat_id}/messages",
    response_model=List[ChatMessageResponse],
    summary="Fetch message history for a specific chat"
)
async def get_chat_messages(chat_id: str):
    """
    Fetches all message history for a given chat_id from the messages collection,
    sorted ascending by timestamp.
    """
    messages = get_message_collection()
    cursor = messages.find({"chat_id": chat_id.strip()}).sort("timestamp", 1)
    documents = await cursor.to_list(length=1000)

    history = []
    for doc in documents:
        timestamp_val = doc.get("timestamp")
        timestamp_str = timestamp_val.isoformat() if timestamp_val else None

        history.append(
            ChatMessageResponse(
                id=str(doc["_id"]),
                chat_id=doc.get("chat_id", chat_id),
                user_id=doc.get("user_id"),
                role=doc.get("role", "user"),
                content=doc.get("content", ""),
                timestamp=timestamp_str
            )
        )

    return history


# -------------------------------------------------------------
# 4. LLM Integration & Context Memory - Send Message
# -------------------------------------------------------------
@router.post(
    "/send",
    response_model=SendMessageResponse,
    summary="Send message and receive AI reply via OpenRouter"
)
async def send_chat_message(payload: SendMessageRequest):
    """
    Step 1: Save user incoming message to messages collection.
    Step 2: Query MongoDB for strictly the last 10 messages, reverse to chronological order.
    Step 3: Call OpenRouter API with standard OpenAI schema and OPENROUTER_API_KEY.
    Step 4: Save AI response in messages collection.
    Step 5: Auto-title if title is 'New Conversation' with first 25 characters of prompt.
    Step 6: Return AI reply.
    """
    chats = get_chat_collection()
    messages = get_message_collection()

    clean_chat_id = payload.chat_id.strip()
    clean_user_id = payload.user_id.strip()
    clean_message = payload.message.strip()
    model = payload.model_name.strip() if payload.model_name else "openai/gpt-3.5-turbo"

    if not clean_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    # Verify chat session exists
    chat_filter = get_chat_filter(clean_chat_id)
    chat = await chats.find_one(chat_filter)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )

    # Step 1: Save the user's incoming message to the messages collection
    now = datetime.now(timezone.utc)
    user_msg_doc = {
        "chat_id": clean_chat_id,
        "user_id": clean_user_id,
        "role": "user",
        "content": clean_message,
        "timestamp": now
    }
    await messages.insert_one(user_msg_doc)

    # Step 2: Strict Context Window - fetch strictly last 10 messages and restore chronological order
    cursor = messages.find({"chat_id": clean_chat_id}).sort("timestamp", -1).limit(10)
    last_10_docs = await cursor.to_list(length=10)
    last_10_docs.reverse()

    # Step 3: Format messages into standard OpenAI schema and call OpenRouter
    formatted_messages = [
        {"role": doc["role"], "content": doc["content"]}
        for doc in last_10_docs
        if doc.get("role") in ["user", "assistant", "system"]
    ]

    ai_reply = await llm_service.call_openrouter(
        messages=formatted_messages,
        model=model,
        api_key_override=payload.api_key
    )

    # Step 4: Save AI response into the messages collection
    ai_msg_doc = {
        "chat_id": clean_chat_id,
        "user_id": clean_user_id,
        "role": "assistant",
        "content": ai_reply,
        "timestamp": datetime.now(timezone.utc)
    }
    await messages.insert_one(ai_msg_doc)

    # Step 5: Auto-Title - if chat title is still "New Conversation", update it with the first 25 characters
    if chat.get("title") == "New Conversation":
        new_title = clean_message[:25]
        if len(clean_message) > 25:
            new_title = f"{new_title}..."
        await chats.update_one(
            chat_filter,
            {"$set": {"title": new_title, "updated_at": datetime.now(timezone.utc)}}
        )

    # Step 6: Return AI reply
    return SendMessageResponse(
        chat_id=clean_chat_id,
        reply=ai_reply,
        role="assistant"
    )


# -------------------------------------------------------------
# 5. Delete Chat Session & Cascade Associated Messages
# -------------------------------------------------------------
@router.delete(
    "/{chat_id}",
    response_model=DeleteChatResponse,
    summary="Delete chat session and all associated messages"
)
async def delete_chat(chat_id: str):
    """
    Cleans up/deletes the chat session and its associated messages.
    """
    chats = get_chat_collection()
    messages = get_message_collection()

    clean_chat_id = chat_id.strip()
    chat_filter = get_chat_filter(clean_chat_id)

    delete_result = await chats.delete_one(chat_filter)
    if delete_result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )

    # Delete all associated messages matching this chat_id
    await messages.delete_many({"chat_id": clean_chat_id})

    return DeleteChatResponse(
        message="Chat session and associated message history deleted successfully.",
        chat_id=clean_chat_id
    )
