"""HTTP client and response parsing for Ollama LLM extraction."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests

from knowledge_graph.llm_config import LLMConfig
from knowledge_graph.llm_prompts import _SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def call_ollama(prompt: str, config: LLMConfig) -> tuple[str, dict[str, float | int]]:
    """Send *prompt* to Ollama ``/api/generate`` and return text + metadata."""
    url = f"{config.base_url}/api/generate"
    payload = {
        "model": config.model,
        "prompt": prompt,
        "system": _SYSTEM_PROMPT,
        "stream": False,
        "options": {"temperature": config.temperature, "num_predict": config.max_tokens},
    }
    resp = requests.post(url, json=payload, timeout=config.timeout_seconds)
    resp.raise_for_status()
    data = resp.json()
    response_text = data.get("response", "")
    eval_duration_ns = data.get("eval_duration", 0)
    eval_count = data.get("eval_count", 0)
    eval_duration_s = eval_duration_ns / 1e9 if eval_duration_ns else 0
    tokens_per_s = (eval_count / eval_duration_s) if eval_duration_s > 0 else 0
    meta = {
        "prompt_chars": len(prompt),
        "response_chars": len(response_text),
        "eval_duration_s": round(eval_duration_s, 2),
        "tokens_per_s": round(tokens_per_s, 1),
        "eval_count": eval_count,
    }
    return response_text, meta


def parse_llm_response(raw: str) -> list[dict[str, Any]]:
    """Parse the LLM JSON array response, stripping fences when present."""
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[:-3].rstrip()

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No JSON array found in LLM response: {text[:200]}")

    json_str = _repair_directional_quote_delimiters(text[start : end + 1])
    max_attempts = 2
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            # Small local models occasionally emit literal newlines or tabs
            # inside quoted evidence fields. ``strict=False`` accepts those
            # control characters while retaining JSON structure validation.
            result = json.loads(json_str, strict=False)
            break
        except json.JSONDecodeError as exc:
            logger.debug("LLM raw response: %s", raw)
            last_error = exc
            if attempt < max_attempts:
                time.sleep(2 * (2 ** (attempt - 1)))
            else:
                recovered = _recover_json_objects(json_str)
                if recovered:
                    logger.warning(
                        "Recovered %d complete JSON object(s) from malformed LLM array",
                        len(recovered),
                    )
                    return recovered
                raise ValueError(
                    f"Failed to parse JSON from LLM response after {max_attempts} attempts: {exc}"
                ) from exc
    else:
        raise ValueError(f"Failed to parse JSON: {last_error}")

    if not isinstance(result, list):
        raise ValueError(f"Expected JSON array, got {type(result).__name__}")
    return result


def _repair_directional_quote_delimiters(text: str) -> str:
    """Repair directional quotes used as JSON string delimiters by small LLMs.

    Models sometimes emit a JSON string with a Unicode closing quotation mark,
    for example ``"evidence_quote": "claim”,``.  The directional mark is
    valid Unicode text but not a JSON delimiter, so strict parsing rejects the
    complete response.  Only a directional mark adjacent to a JSON delimiter
    is rewritten; quotation marks occurring inside ordinary string content are
    retained as evidence text.
    """
    repaired: list[str] = []
    in_string = False
    escaped = False
    delimiters = {",", "]", "}", ":"}

    for index, character in enumerate(text):
        if escaped:
            repaired.append(character)
            escaped = False
            continue
        if character == "\\" and in_string:
            repaired.append(character)
            escaped = True
            continue
        if character == '"':
            repaired.append(character)
            in_string = not in_string
            continue
        if character == "“" and not in_string:
            repaired.append('"')
            in_string = True
            continue
        if character == "”" and in_string:
            following = text[index + 1 :].lstrip()
            if following and following[0] in delimiters:
                repaired.append('"')
                in_string = False
                continue
        repaired.append(character)

    return "".join(repaired)


def _recover_json_objects(text: str) -> list[dict[str, Any]]:
    """Recover complete object members when an LLM array is partly malformed."""
    decoder = json.JSONDecoder(strict=False)
    recovered: list[dict[str, Any]] = []
    cursor = 0
    while True:
        start = text.find("{", cursor)
        if start < 0:
            break
        try:
            value, end = decoder.raw_decode(text, start)
        except json.JSONDecodeError:
            cursor = start + 1
            continue
        if isinstance(value, dict):
            recovered.append(value)
        cursor = end
    return recovered
