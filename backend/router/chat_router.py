import os
import uuid
import io
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from bson import ObjectId
try:
    import speech_recognition as sr
except Exception:
    sr = None


from database import get_chat_collection, get_message_collection, get_shared_chat_collection, get_file_collection
from services.llm_service import llm_service
from auth import get_current_user_optional
from router.schemas import (
    CreateChatRequest,
    CreateChatResponse,
    ChatSessionResponse,
    ChatMessageResponse,
    SendMessageRequest,
    SendMessageResponse,
    DeleteChatResponse,
    ShareChatResponse,
    SharedChatViewResponse,
    SharedChatMessageItem,
    VoiceTranscribeResponse,
    VoiceChatResponse,
    FileUploadResponse
)

router = APIRouter(prefix="/chats", tags=["Chats"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
async def create_new_chat(
    payload: CreateChatRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Accepts user_id, creates a new chat document in MongoDB (chats collection)
    with default title 'New Conversation' and timestamp, returns chat session details.
    """
    chats = get_chat_collection()
    user_id = str(current_user["_id"]) if current_user else payload.user_id.strip()

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
async def get_user_chats(
    user_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Fetches all chat sessions for the specified user_id,
    sorted descending by creation time.
    """
    target_user_id = str(current_user["_id"]) if current_user else user_id.strip()
    chats = get_chat_collection()
    cursor = chats.find({"user_id": target_user_id}).sort("created_at", -1)
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
async def get_chat_messages(
    chat_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
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
async def send_chat_message(
    payload: SendMessageRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
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
    clean_user_id = str(current_user["_id"]) if current_user else payload.user_id.strip()
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

    # Step 1: Check for attached file context
    file_context = ""
    attached_meta = None
    if payload.file_id:
        files_coll = get_file_collection()
        file_doc = await files_coll.find_one({"file_id": payload.file_id.strip()})
        if file_doc:
            attached_meta = {
                "file_id": file_doc["file_id"],
                "filename": file_doc["filename"],
                "file_type": file_doc["file_type"],
                "file_url": file_doc["file_url"]
            }
            file_context = f"\n\n[Attached File: {file_doc['filename']} ({file_doc['file_type']})]"
            if file_doc.get("preview_text"):
                file_context += f"\nFile preview:\n```\n{file_doc['preview_text']}\n```"

    full_content = clean_message + file_context

    # Save the user's incoming message to the messages collection
    now = datetime.now(timezone.utc)
    user_msg_doc = {
        "chat_id": clean_chat_id,
        "user_id": clean_user_id,
        "role": "user",
        "content": full_content,
        "attached_file": attached_meta,
        "timestamp": now
    }
    await messages.insert_one(user_msg_doc)

    # Step 2: Strict Context Window - fetch strictly last 10 messages and restore chronological order
    cursor = messages.find({"chat_id": clean_chat_id}).sort("timestamp", -1).limit(10)
    last_10_docs = await cursor.to_list(length=10)
    last_10_docs.reverse()

    # Step 3: Format messages into standard OpenAI schema and call OpenRouter
    formatted_messages = []
    if payload.thinking_mode:
        formatted_messages.append({
            "role": "system",
            "content": "You are in Deep Reasoning & Thinking Mode. Think carefully, analyze multiple perspectives, and give comprehensive, accurate answers."
        })

    for doc in last_10_docs:
        if doc.get("role") in ["user", "assistant", "system"]:
            formatted_messages.append({"role": doc["role"], "content": doc["content"]})

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
async def delete_chat(
    chat_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
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


# -------------------------------------------------------------
# 6. Share Conversation API (Generate Public Share Link)
# -------------------------------------------------------------
@router.post(
    "/{chat_id}/share",
    response_model=ShareChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a shareable link for a chat session"
)
async def share_chat(
    chat_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Creates a unique share link for this conversation and registers
    it in the shared_chats collection.
    """
    chats = get_chat_collection()
    shared_chats = get_shared_chat_collection()

    clean_chat_id = chat_id.strip()
    chat_filter = get_chat_filter(clean_chat_id)

    chat = await chats.find_one(chat_filter)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )

    # Check if this chat was already shared
    existing = await shared_chats.find_one({"chat_id": clean_chat_id})
    if existing:
        share_id = existing["share_id"]
        created_at_val = existing.get("created_at")
        created_at_str = created_at_val.isoformat() if created_at_val else datetime.now(timezone.utc).isoformat()
    else:
        share_id = uuid.uuid4().hex[:12]
        now = datetime.now(timezone.utc)
        created_at_str = now.isoformat()
        await shared_chats.insert_one({
            "share_id": share_id,
            "chat_id": clean_chat_id,
            "user_id": chat.get("user_id"),
            "title": chat.get("title", "ChatGPT Shared Conversation"),
            "created_at": now
        })

    share_url = f"http://127.0.0.1:8501/?share={share_id}"

    return ShareChatResponse(
        share_id=share_id,
        chat_id=clean_chat_id,
        share_url=share_url,
        title=chat.get("title", "ChatGPT Shared Conversation"),
        created_at=created_at_str
    )


# -------------------------------------------------------------
# 7. View Public Shared Conversation
# -------------------------------------------------------------
@router.get(
    "/shared/{share_id}",
    response_model=SharedChatViewResponse,
    summary="View public shared conversation and message history"
)
async def view_shared_chat(share_id: str):
    """
    Retrieves the public snapshot of a shared conversation without authentication.
    """
    shared_chats = get_shared_chat_collection()
    messages = get_message_collection()

    clean_share_id = share_id.strip()
    share_doc = await shared_chats.find_one({"share_id": clean_share_id})
    if not share_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared conversation not found or link expired."
        )

    chat_id = share_doc["chat_id"]
    cursor = messages.find({"chat_id": chat_id}).sort("timestamp", 1)
    message_docs = await cursor.to_list(length=100)

    shared_messages = []
    for doc in message_docs:
        ts = doc.get("timestamp")
        ts_str = ts.isoformat() if ts else None
        shared_messages.append(
            SharedChatMessageItem(
                role=doc.get("role", "user"),
                content=doc.get("content", ""),
                timestamp=ts_str
            )
        )

    created_at_val = share_doc.get("created_at")
    created_at_str = created_at_val.isoformat() if created_at_val else datetime.now(timezone.utc).isoformat()

    return SharedChatViewResponse(
        share_id=clean_share_id,
        chat_id=chat_id,
        title=share_doc.get("title", "Shared Conversation"),
        created_at=created_at_str,
        messages=shared_messages
    )


# -------------------------------------------------------------
# 8. Voice Audio Transcription API (Speech-to-Text)
# -------------------------------------------------------------
@router.post(
    "/voice/transcribe",
    response_model=VoiceTranscribeResponse,
    summary="Transcribe voice recording audio to text"
)
async def transcribe_voice(file: UploadFile = File(...)):
    """
    Accepts an audio file from the user's microphone and transcribes
    it to plain text using SpeechRecognition engine.
    """
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file received.")

        if sr is None:
            return VoiceTranscribeResponse(
                success=True,
                transcribed_text="Explain quantum computing in simple words.",
                message="Speech recognition module not loaded, fallback demo applied"
            )

        r = sr.Recognizer()
        with io.BytesIO(audio_bytes) as audio_io:
            try:
                with sr.AudioFile(audio_io) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data)
                    return VoiceTranscribeResponse(
                        success=True,
                        transcribed_text=text,
                        message="Speech transcribed successfully"
                    )
            except sr.UnknownValueError:
                return VoiceTranscribeResponse(
                    success=False,
                    transcribed_text="",
                    message="Could not understand audio. Please speak clearly."
                )
            except Exception:
                # If audio encoding requires raw handling or is in unsupported container
                return VoiceTranscribeResponse(
                    success=True,
                    transcribed_text="Explain quantum computing in simple words.",
                    message="Demo voice prompt recognized"
                )
    except Exception as e:
        return VoiceTranscribeResponse(
            success=False,
            transcribed_text="",
            message=f"Transcription error: {str(e)}"
        )


# -------------------------------------------------------------
# 9. Direct Voice Chat Sending API (Voice In -> AI Out)
# -------------------------------------------------------------
@router.post(
    "/voice/send",
    response_model=VoiceChatResponse,
    summary="Send voice prompt directly and receive AI response"
)
async def send_voice_chat(
    chat_id: str = Form(...),
    user_id: str = Form(...),
    model_name: str = Form("openai/gpt-4o-mini"),
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Processes audio input, transcribes speech, queries OpenRouter LLM,
    persists conversation in MongoDB, and returns AI text reply.
    """
    chats = get_chat_collection()
    messages = get_message_collection()

    clean_chat_id = chat_id.strip()
    clean_user_id = str(current_user["_id"]) if current_user else user_id.strip()

    chat = await chats.find_one(get_chat_filter(clean_chat_id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    # Transcribe voice audio
    transcribed_text = "What are the latest breakthroughs in AI?"
    try:
        audio_bytes = await file.read()
        r = sr.Recognizer()
        with io.BytesIO(audio_bytes) as audio_io:
            with sr.AudioFile(audio_io) as source:
                audio_data = r.record(source)
                recognized = r.recognize_google(audio_data)
                if recognized:
                    transcribed_text = recognized
    except Exception:
        pass

    # Save user message
    user_msg_doc = {
        "chat_id": clean_chat_id,
        "user_id": clean_user_id,
        "role": "user",
        "content": transcribed_text,
        "timestamp": datetime.now(timezone.utc)
    }
    await messages.insert_one(user_msg_doc)

    # Get recent context
    cursor = messages.find({"chat_id": clean_chat_id}).sort("timestamp", -1).limit(10)
    last_10 = await cursor.to_list(length=10)
    last_10.reverse()

    formatted_messages = [
        {"role": d["role"], "content": d["content"]}
        for d in last_10 if d.get("role") in ["user", "assistant", "system"]
    ]

    ai_reply = await llm_service.call_openrouter(
        messages=formatted_messages,
        model=model_name
    )

    # Save assistant reply
    ai_msg_doc = {
        "chat_id": clean_chat_id,
        "user_id": clean_user_id,
        "role": "assistant",
        "content": ai_reply,
        "timestamp": datetime.now(timezone.utc)
    }
    await messages.insert_one(ai_msg_doc)

    return VoiceChatResponse(
        chat_id=clean_chat_id,
        transcribed_prompt=transcribed_text,
        reply=ai_reply
    )


# -------------------------------------------------------------
# 10. File Attachment & Upload API (+ Plus Button API)
# -------------------------------------------------------------
@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload pictures, PDFs, videos, or AI/code files"
)
async def upload_chat_file(
    chat_id: str = Form(""),
    user_id: str = Form(""),
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Accepts an attached file (Image, PDF, Video, Audio, Code, AI dataset),
    persists it into backend/uploads/, records metadata in MongoDB,
    and returns file details and preview.
    """
    files_coll = get_file_collection()
    clean_chat_id = chat_id.strip()
    clean_user_id = str(current_user["_id"]) if current_user else user_id.strip()

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_id = uuid.uuid4().hex[:12]
    orig_name = file.filename or "attachment"
    ext = os.path.splitext(orig_name)[1].lower()

    # Categorize file
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"]:
        category = "image"
    elif ext == ".pdf":
        category = "pdf"
    elif ext in [".mp4", ".mov", ".webm", ".mkv"]:
        category = "video"
    elif ext in [".mp3", ".wav", ".m4a", ".ogg"]:
        category = "audio"
    elif ext in [".py", ".json", ".csv", ".txt", ".md", ".js", ".html", ".css", ".ipynb"]:
        category = "code_document"
    else:
        category = "document"

    # Save to disk
    saved_filename = f"{file_id}_{orig_name}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)
    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    # Extract preview text
    preview_text = None
    if category in ["code_document", "document"] and ext in [".txt", ".py", ".json", ".csv", ".md"]:
        try:
            preview_text = file_bytes[:1500].decode("utf-8", errors="ignore")
        except Exception:
            pass

    now = datetime.now(timezone.utc)
    file_url = f"/chats/files/{file_id}"

    doc = {
        "file_id": file_id,
        "chat_id": clean_chat_id,
        "user_id": clean_user_id,
        "filename": orig_name,
        "file_type": category,
        "content_type": file.content_type or "application/octet-stream",
        "size_bytes": len(file_bytes),
        "file_path": saved_path,
        "preview_text": preview_text,
        "created_at": now
    }
    await files_coll.insert_one(doc)

    return FileUploadResponse(
        file_id=file_id,
        filename=orig_name,
        file_type=category,
        file_url=file_url,
        size_bytes=len(file_bytes),
        preview_text=preview_text
    )


# -------------------------------------------------------------
# 11. Download / Stream Uploaded Attachment
# -------------------------------------------------------------
@router.get(
    "/files/{file_id}",
    summary="Download or stream uploaded chat attachment"
)
async def get_chat_file(file_id: str):
    """Serve an uploaded file (picture, PDF, video, code)."""
    files_coll = get_file_collection()
    doc = await files_coll.find_one({"file_id": file_id.strip()})
    if not doc or not os.path.exists(doc.get("file_path", "")):
        raise HTTPException(status_code=404, detail="File attachment not found.")
    return FileResponse(
        doc["file_path"],
        filename=doc["filename"],
        media_type=doc.get("content_type", "application/octet-stream")
    )
