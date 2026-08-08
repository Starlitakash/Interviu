import json
import re
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from .logger import logger

T = TypeVar("T", bound=BaseModel)


def strip_thinking_tags(text: str) -> str:
    """
    Strip Qwen 3 / DeepSeek-style <think>...</think> blocks from LLM output.
    These thinking blocks wrap the model's chain-of-thought reasoning and
    appear before the actual JSON response, breaking all downstream parsers.
    """
    if not text:
        return text
    # Remove all <think>...</think> blocks (greedy, handles multi-line)
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Also handle unclosed <think> tags (model may have been truncated)
    cleaned = re.sub(r"<think>.*$", "", cleaned, flags=re.DOTALL)
    return cleaned.strip()


def parse_json_from_llm_text(text: str) -> Optional[dict]:
    """Extract JSON object from LLM response, handling thinking blocks and markdown fences."""
    if not text:
        return None

    # Step 1: Strip thinking blocks (critical for Qwen 3)
    text = strip_thinking_tags(text)
    if not text:
        return None

    text = text.strip()

    # Step 2: Try direct parse (model returned clean JSON)
    try:
        return json.loads(text)
    except Exception:
        pass

    # Step 3: Extract ```json ... ``` fenced block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Step 4: Extract ```json ... ``` with array at top level
    match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match:
        try:
            arr = json.loads(match.group(1))
            if isinstance(arr, list) and len(arr) > 0 and isinstance(arr[0], dict):
                return arr[0]
        except Exception:
            pass

    # Step 5: Find first { and last } — greedy brace matching
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            # Try fixing common LLM issues: trailing commas
            cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
            try:
                return json.loads(cleaned)
            except Exception:
                pass

    logger.warning(f"JSON extraction failed. Raw text (first 300 chars): {text[:300]}")
    return None


def parse_structured_output(text: str, model_cls: Type[T]) -> Optional[T]:
    """Parse LLM text into a Pydantic model with thinking-tag stripping."""
    data = parse_json_from_llm_text(text)
    if not data:
        logger.error(f"Failed to extract JSON for {model_cls.__name__} from text: {text[:200]}")
        return None
    try:
        return model_cls.model_validate(data)
    except Exception as e:
        logger.error(f"Validation error for {model_cls.__name__}: {e}")
        return None
