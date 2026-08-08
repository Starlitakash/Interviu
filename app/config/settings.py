import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application Settings"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    STITCH_API_KEY: str = os.getenv("STITCH_API_KEY", "")

    # LLM Settings (Groq + Qwen 3 / Qwen 2.5 Coder)
    PRIMARY_LLM_PROVIDER: str = "groq"
    PRIMARY_MODEL_NAME: str = "qwen/qwen3.6-27b"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    TEMPERATURE_PLANNER: float = 0.3
    TEMPERATURE_GENERATOR: float = 0.7
    TEMPERATURE_EVALUATOR: float = 0.2
    TEMPERATURE_FEEDBACK: float = 0.3

    # Interview Constraints
    MIN_CURRICULUM_DAYS: int = 4
    DEFAULT_QUESTION_BUDGET: int = 8
    MAX_QUESTIONS_PER_TOPIC: int = 3

settings = Settings()
