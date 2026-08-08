import os
import time
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from app.config.settings import settings
from app.utils.logger import logger
from app.utils.output_parser import parse_structured_output

T = TypeVar("T", bound=BaseModel)

MAX_RETRIES = 2
RETRY_DELAY_SECS = 1.0


class LLMClient:
    """Unified LLM Client supporting Groq (Qwen 3 / Qwen 2.5), ChatOpenAI, and fallback."""

    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)
        self.openai_key = os.getenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        self.gemini_key = os.getenv("GEMINI_API_KEY", settings.GEMINI_API_KEY)
        self._init_llm_instance()

    def _init_llm_instance(self):
        self.has_real_llm = False
        self.llm = None

        # 1. Try Groq (Qwen 3 / Qwen 2.5 Coder)
        if self.groq_key and self.groq_key != "your_groq_api_key_here":
            try:
                from langchain_openai import ChatOpenAI
                model_name = settings.PRIMARY_MODEL_NAME if settings.PRIMARY_MODEL_NAME else "qwen-2.5-coder-32b"
                self.llm = ChatOpenAI(
                    base_url=settings.GROQ_BASE_URL,
                    api_key=self.groq_key,
                    model=model_name,
                    temperature=0.7
                )
                self.has_real_llm = True
                logger.info(f"[OK] LLM initialized: Groq ({model_name})")
                return
            except Exception as e:
                logger.warning(f"[FAIL] Failed to initialize Groq client: {e}")

        # 2. Try OpenAI
        if self.openai_key and self.openai_key != "your_openai_api_key_here":
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    api_key=self.openai_key,
                    model="gpt-4o",
                    temperature=0.7
                )
                self.has_real_llm = True
                logger.info("[OK] LLM initialized: OpenAI gpt-4o")
                return
            except Exception as e:
                logger.warning(f"[FAIL] Failed to initialize ChatOpenAI: {e}")

        # 3. Try Gemini
        if self.gemini_key and self.gemini_key != "your_gemini_api_key_here":
            try:
                from langchain_community.chat_models import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    google_api_key=self.gemini_key,
                    model="gemini-1.5-flash",
                    temperature=0.7
                )
                self.has_real_llm = True
                logger.info("[OK] LLM initialized: Gemini 1.5 Flash")
                return
            except Exception as e:
                logger.warning(f"[FAIL] Failed to initialize Gemini: {e}")

        logger.warning("[WARN] No LLM API key configured. All agents will use heuristic fallbacks.")

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate raw text response from LLM with retry logic."""
        if not self.has_real_llm or not self.llm:
            logger.debug("No LLM available, returning empty for fallback.")
            return ""

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if hasattr(self.llm, "temperature"):
                    self.llm.temperature = temperature
                res = self.llm.invoke(prompt)
                content = res.content if hasattr(res, "content") else str(res)

                if content:
                    logger.debug(f"LLM response received ({len(content)} chars, attempt {attempt})")
                    return content
                else:
                    logger.warning(f"LLM returned empty content on attempt {attempt}")

            except Exception as e:
                error_str = str(e)
                logger.error(f"LLM call failed (attempt {attempt}/{MAX_RETRIES}): {error_str}")

                # Don't retry on auth errors
                if "401" in error_str or "403" in error_str or "invalid_api_key" in error_str:
                    logger.error("Authentication error — not retrying.")
                    break

                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY_SECS}s...")
                    time.sleep(RETRY_DELAY_SECS)

        logger.warning("All LLM attempts exhausted, returning empty for fallback.")
        return ""

    def generate_structured(self, prompt: str, response_model: Type[T], temperature: float = 0.7) -> Optional[T]:
        """Generate structured output validated against Pydantic schema."""
        if self.has_real_llm and self.llm:
            try:
                if hasattr(self.llm, "with_structured_output"):
                    structured_llm = self.llm.with_structured_output(response_model)
                    res = structured_llm.invoke(prompt)
                    if isinstance(res, response_model):
                        return res
            except Exception as e:
                logger.warning(f"Structured output call failed, falling back to manual parse: {e}")

            text_res = self.generate(prompt, temperature=temperature)
            parsed = parse_structured_output(text_res, response_model)
            if parsed:
                return parsed

        return None


llm_client = LLMClient()
