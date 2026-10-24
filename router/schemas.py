from typing import Optional
from pydantic import BaseModel, Field


class CreateChatRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="Optional user ID (inferred from JWT token)")


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
    model: Optional[str] = None
    timestamp: Optional[str] = None


class SendMessageRequest(BaseModel):
    chat_id: str = Field(..., description="The chat session ID")
    user_id: Optional[str] = Field(None, description="User ID (inferred from authenticated token)")
    message: str = Field(..., description="User message text")
    model_name: Optional[str] = Field(None, description="OpenRouter model (defaults to OPENROUTER_MODEL_NAME from .env)")
    api_key: Optional[str] = Field(None, description="Optional OpenRouter API key override (defaults to OPENROUTER_API_KEY from .env)")


class SendMessageResponse(BaseModel):
    chat_id: str
    reply: str
    role: str = "assistant"
    model: Optional[str] = None


class DeleteChatResponse(BaseModel):
    message: str
    chat_id: str
