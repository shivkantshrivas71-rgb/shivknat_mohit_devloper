from typing import Optional
from pydantic import BaseModel, Field


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
    model_name: Optional[str] = Field("openai/gpt-4o-mini", description="OpenRouter model (default: openai/gpt-4o-mini)")
    api_key: Optional[str] = Field(None, description="Optional OpenRouter API key override (defaults to OPENROUTER_API_KEY from .env)")
    file_id: Optional[str] = Field(None, description="Optional attached file ID")
    file_url: Optional[str] = Field(None, description="Optional attached file URL")
    thinking_mode: Optional[bool] = Field(False, description="Enable Think / Reasoning Mode")


class SendMessageResponse(BaseModel):
    chat_id: str
    reply: str
    role: str = "assistant"
    thinking_content: Optional[str] = None


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    file_url: str
    size_bytes: int
    preview_text: Optional[str] = None


class DeleteChatResponse(BaseModel):
    message: str
    chat_id: str


# -------------------------------------------------------------
# Share Chat Schemas
# -------------------------------------------------------------
class ShareChatResponse(BaseModel):
    share_id: str
    chat_id: str
    share_url: str
    title: str
    created_at: str


class SharedChatMessageItem(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class SharedChatViewResponse(BaseModel):
    share_id: str
    chat_id: str
    title: str
    created_at: str
    messages: list[SharedChatMessageItem]


# -------------------------------------------------------------
# Voice / Mic Schemas
# -------------------------------------------------------------
class VoiceTranscribeResponse(BaseModel):
    success: bool
    transcribed_text: str
    message: Optional[str] = None


class VoiceChatResponse(BaseModel):
    chat_id: str
    transcribed_prompt: str
    reply: str
    role: str = "assistant"
