import os
from dotenv import load_dotenv

# Load optional .env in frontend directory or parent directory
load_dotenv()

# Real-world API Base URL configuration:
# Defaults to localhost:8000 for local development,
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")
