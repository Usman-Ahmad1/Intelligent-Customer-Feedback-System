import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for FeedbackFlow AI."""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Email settings
    FROM_EMAIL = os.getenv("FROM_EMAIL", "uahmaddatascientist@gmail.com")
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "uahmaddatascientist@gmail.com")
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "uahmaddatascientist@gmail.com")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    
    # Model configuration
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "groq")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")
        return True

Config.validate()