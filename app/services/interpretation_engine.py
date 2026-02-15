from __future__ import annotations

import json
import time
from typing import Any, Dict

import requests
from app.utils.logger import get_logger


class InterpretationEngine:
    def __init__(self, model: str = "llama3:8b", base_url: str = "http://localhost:11434/api/generate") -> None:
        self.model = model
        self.base_url = base_url
        self.logger = get_logger(self.__class__.__name__)

    def _build_prompt(self, data: Dict[str, Any]) -> str:
        return (
            "You are a professional financial analyst.\n\n"
            "Strict rules:\n"
            "- Only use the provided data.\n"
            "- Do NOT fabricate numbers.\n"
            "- Do NOT give investment advice.\n"
            "- Output must be valid JSON only.\n"
            "- Do NOT include markdown, code fences, or extra text.\n\n"
            "Return exactly this JSON structure:\n"
            "{\n"
            "  \"executive_summary\": \"...\",\n"
            "  \"bull_case\": \"...\",\n"
            "  \"bear_case\": \"...\",\n"
            "  \"risk_assessment\": \"...\",\n"
            "  \"confidence\": \"Low/Medium/High\"\n"
            "}\n\n"
            "Data:\n"
            f"{data}\n"
        )

    def generate(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_prompt(structured_data)
        start_time = time.time()
        self.logger.info("Calling LLM | model=%s", self.model)

        response = requests.post(
            self.base_url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=90,
        )
        response.raise_for_status()
        output = response.json().get("response", "")
        self.logger.info("LLM response received in %.2fs", time.time() - start_time)

        parsed: Dict[str, Any]
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            self.logger.exception("Failed to parse LLM JSON output")
            parsed = {}

        return {
            "model_used": self.model,
            "raw_output": output,
            "parsed": parsed,
        }
