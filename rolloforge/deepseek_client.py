from __future__ import annotations

import logging
import time
from typing import Any

import requests

from config.settings import Settings
from rolloforge.utils import extract_json_object


LOGGER = logging.getLogger(__name__)


class DeepSeekClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.enabled = bool(settings.deepseek_api_key)
        self.session = requests.Session()

    def request_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        if not self.enabled:
            LOGGER.info("DeepSeek disabled because DEEPSEEK_API_KEY is not set.")
            return None

        url = f"{self.settings.deepseek_api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.deepseek_model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        last_error: Exception | None = None
        for attempt in range(1, self.settings.deepseek_max_retries + 1):
            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.settings.deepseek_timeout_seconds,
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return extract_json_object(content)
            except (requests.RequestException, KeyError, ValueError) as exc:
                last_error = exc
                LOGGER.warning(
                    "DeepSeek request failed on attempt %s/%s: %s",
                    attempt,
                    self.settings.deepseek_max_retries,
                    exc,
                )
                if attempt < self.settings.deepseek_max_retries:
                    time.sleep(min(2 ** (attempt - 1), 8))

        LOGGER.error("DeepSeek failed after retries: %s", last_error)
        return None
