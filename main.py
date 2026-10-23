from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatMessage(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "Chatbot API is running"}


@app.post("/chat")
def chat(data: ChatMessage):
    user_message = data.message

    return {
        "user_message": user_message,
        "reply": f"You said: {user_message}"
    }