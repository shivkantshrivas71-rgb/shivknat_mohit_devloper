import os
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from bson import ObjectId
import httpx
from dotenv import load_dotenv

load_dotenv()

from database import get_chat_collection, get_message_collection

router = APIRouter(prefix="/chats", tags=["Chats"])


# -------------------------------------------------------------
# Pydantic Schemas for Chat Backend
# -------------------------------------------------------------
class CreateChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique ID of the user creating the conversation")


class CreateChatResponse(BaseModel):
    chat_id: str
    title: str
    created_at: Optional[str] = None


class ChatSessionResponse(BaseModel):
    chat_id: str
    user_id: str
    title: str
    created_at: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: str
    chat_id: str
    user_id: Optional[str] = None
    role: str
    content: str
    timestamp: Optional[str] = None


class SendMessageRequest(BaseModel):
    chat_id: str = Field(..., description="The chat session ID")
    user_id: str = Field(..., description="User ID sending the prompt")
    message: str = Field(..., description="User message text")
    api_key: Optional[str] = Field(None, description="OpenAI API key (optional if set in .env as OPENAI_API_KEY)")
    model_name: Optional[str] = Field("gpt-3.5-turbo", description="OpenAI model (default: gpt-3.5-turbo)")


class SendMessageResponse(BaseModel):
    chat_id: str
    reply: str
    role: str = "assistant"


class DeleteChatResponse(BaseModel):
    message: str
    chat_id: str


# -------------------------------------------------------------
# 1. Create New Chat Session
# -------------------------------------------------------------
@router.post(
    "/new",
    response_model=CreateChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat conversation"
)
async def create_new_chat(payload: CreateChatRequest):
    """
    Creates a new chat document in MongoDB 'chats' collection with
    default title 'New Conversation' and created_at timestamp.
    """
    chats = get_chat_collection()
    now = datetime.now(timezone.utc)

    new_chat_doc = {
        "user_id": payload.user_id.strip(),
        "title": "New Conversation",
        "created_at": now
    }

    result = await chats.insert_one(new_chat_doc)

    return CreateChatResponse(
        chat_id=str(result.inserted_id),
        title=new_chat_doc["title"],
        created_at=now.isoformat()
    )


# -------------------------------------------------------------
# 2. Get All Chats for a User
# -------------------------------------------------------------
@router.get(
    "/{user_id}",
    response_model=List[ChatSessionResponse],
    summary="Get all chat sessions for a user"
)
async def get_user_chats(user_id: str):
    """
    Fetches all previous chat sessions belonging to the given user_id,
    sorted by created_at in descending order.
    """
    chats = get_chat_collection()
    cursor = chats.find({"user_id": user_id.strip()}).sort("created_at", -1)
    docs = await cursor.to_list(length=1000)

    chat_list = []
    for doc in docs:
        created_val = doc.get("created_at")
        created_str = created_val.isoformat() if created_val else None

        chat_list.append(
            ChatSessionResponse(
                chat_id=str(doc["_id"]),
                user_id=doc.get("user_id", user_id),
                title=doc.get("title", "New Conversation"),
                created_at=created_str
            )
        )

    return chat_list


# -------------------------------------------------------------
# 3. Get Messages History for a Chat
# -------------------------------------------------------------
@router.get(
    "/{chat_id}/messages",
    response_model=List[ChatMessageResponse],
    summary="Get message history for a specific chat"
)
async def get_chat_messages(chat_id: str):
    """
    Fetches all message history from the messages collection for the
    specified chat_id, sorted by timestamp in ascending order.
    """
    messages = get_message_collection()
    cursor = messages.find({"chat_id": chat_id.strip()}).sort("timestamp", 1)
    docs = await cursor.to_list(length=1000)

    message_list = []
    for doc in docs:
        ts_val = doc.get("timestamp")
        ts_str = ts_val.isoformat() if ts_val else None

        message_list.append(
            ChatMessageResponse(
                id=str(doc["_id"]),
                chat_id=doc.get("chat_id", chat_id),
                user_id=doc.get("user_id"),
                role=doc.get("role", "user"),
                content=doc.get("content", ""),
                timestamp=ts_str
            )
        )

    return message_list


# -------------------------------------------------------------
# 4. Send Message & Receive AI Reply
# -------------------------------------------------------------
@router.post(
    "/send",
    response_model=SendMessageResponse,
    summary="Send message and receive AI reply with context memory"
)
async def send_chat_message(payload: SendMessageRequest):
    """
    Step A: Save incoming user message in 'messages' collection.
    Step B: Fetch strictly the last 10 messages (.sort("timestamp", -1).limit(10)), reverse to oldest -> newest.
    Step C: Format messages and call OpenAI chat completions API.
    Step D: Save AI response in 'messages' collection.
    Step E: If chat title is 'New Conversation', auto-update to first 25 chars + '...'.
    Step F: Return AI reply to the client.
    """
    chats = get_chat_collection()
    messages = get_message_collection()

    clean_chat_id = payload.chat_id.strip()
    clean_user_id = payload.user_id.strip()
    # Extract API key from request payload or fallback to .env
    clean_api_key = payload.api_key.strip() if payload.api_key else os.getenv("OPENAI_API_KEY", "").strip()
    model = payload.model_name.strip() if payload.model_name else "gpt-3.5-turbo"

    if not clean_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty"
        )

    if not clean_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key must be provided in the request body ('api_key') or set in the .env file as 'OPENAI_API_KEY'"
        )

    # Verify chat session exists
    chat_filter = {"_id": ObjectId(clean_chat_id)} if ObjectId.is_valid(clean_chat_id) else {"_id": clean_chat_id}
    chat = await chats.find_one(chat_filter)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    # Step A: Save incoming user message
    now = datetime.now(timezone.utc)
    user_msg_doc = {
        "chat_id": clean_chat_id,
        "user_id": clean_user_id,
        "role": "user",
        "content": clean_message,
        "timestamp": now
    }
    await messages.insert_one(user_msg_doc)

    # Step B: Fetch strictly the last 10 messages and reverse to chronological order
    cursor = messages.find({"chat_id": clean_chat_id}).sort("timestamp", -1).limit(10)
    last_10_messages = await cursor.to_list(length=10)
    last_10_messages.reverse()

    # Step C: Format into OpenAI schema and invoke OpenAI API
    openai_messages = [
        {"role": doc["role"], "content": doc["content"]}
        for doc in last_10_messages
        if doc.get("role") in ["user", "assistant", "system"]
    ]

    headers = {
        "Authorization": f"Bearer {clean_api_key}",
        "Content-Type": "application/json"
    }
    openai_payload = {
        "model": model,
        "messages": openai_messages
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            openai_resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=openai_payload
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to communicate with OpenAI API: {str(exc)}"
        )

    if openai_resp.status_code != 200:
        try:
            error_json = openai_resp.json()
            error_detail = error_json.get("error", {}).get("message", openai_resp.text)
        except Exception:
            error_detail = openai_resp.text
        raise HTTPException(
            status_code=openai_resp.status_code,
            detail=f"OpenAI Error: {error_detail}"
        )

    response_data = openai_resp.json()
    try:
        ai_reply = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected response structure from OpenAI API"
        )

    # Step D: Save AI response in messages collection
    ai_msg_doc = {
        "chat_id": clean_chat_id,
        "user_id": clean_user_id,
        "role": "assistant",
        "content": ai_reply,
        "timestamp": datetime.now(timezone.utc)
    }
    await messages.insert_one(ai_msg_doc)

    # Step E: Auto-update title if it is still default "New Conversation"
    if chat.get("title") == "New Conversation":
        new_title = f"{clean_message[:25]}..."
        await chats.update_one(
            {"_id": chat["_id"]},
            {"$set": {"title": new_title}}
        )

    # Step F: Return AI reply to client
    return SendMessageResponse(
        chat_id=clean_chat_id,
        reply=ai_reply,
        role="assistant"
    )


# -------------------------------------------------------------
# 5. Delete Chat Session & Associated Messages
# -------------------------------------------------------------
@router.delete(
    "/{chat_id}",
    response_model=DeleteChatResponse,
    summary="Delete chat session and all its messages"
)
async def delete_chat_session(chat_id: str):
    """
    Deletes the chat session and all associated messages matching the chat_id.
    """
    chats = get_chat_collection()
    messages = get_message_collection()

    clean_chat_id = chat_id.strip()
    chat_filter = {"_id": ObjectId(clean_chat_id)} if ObjectId.is_valid(clean_chat_id) else {"_id": clean_chat_id}

    delete_result = await chats.delete_one(chat_filter)
    if delete_result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    # Delete all associated messages
    await messages.delete_many({"chat_id": clean_chat_id})

    return DeleteChatResponse(
        message="Chat session and all associated messages deleted successfully.",
        chat_id=clean_chat_id
    )
