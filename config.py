import os

class Config:
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "/path/to/firebase-credentials.json")
    PORT = os.getenv("PORT", "8080")