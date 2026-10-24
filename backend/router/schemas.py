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
    model_name: Optional[str] = Field("openai/gpt-3.5-turbo", description="OpenRouter model (default: openai/gpt-3.5-turbo)")
    api_key: Optional[str] = Field(None, description="Optional OpenRouter API key override (defaults to OPENROUTER_API_KEY from .env)")


class SendMessageResponse(BaseModel):
    chat_id: str
    reply: str
    role: str = "assistant"


class DeleteChatResponse(BaseModel):
    message: str
    chat_id: str
