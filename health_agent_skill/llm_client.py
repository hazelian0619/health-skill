"""Claude API client with fallback support."""

from __future__ import annotations

import json
import os
import time

import httpx
from dotenv import load_dotenv
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH, override=True)


class OpenAIClient:
    """OpenAI-compatible client using direct HTTP for relay support."""

    def __init__(self) -> None:
        self.api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        self.model = os.getenv("OPENAI_MODEL", "deepseek-chat")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://tbnx.plus7.plus/v1")
        self.mode = "mock"

        if self.api_key:
            self.mode = "real"

    def call(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1500,
        temperature: float = 0.7,
    ) -> str:
        if self.mode == "mock":
            return self._mock_response(prompt)

        try:
            start_time = time.time()
            url = self.base_url.rstrip("/") + "/chat/completions"
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            with httpx.Client(timeout=60) as client:
                resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            latency = time.time() - start_time
            print(f"✅ Relay API调用成功 (延迟: {latency:.2f}s)")
            return content
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Relay API调用失败: {exc}")
            print("   降级到mock模式")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        time.sleep(2)
        if "深蹲" in prompt or "硬拉" in prompt:
            return json.dumps(
                {
                    "risk_level": "dangerous",
                    "should_reject": True,
                    "recommendation": "不建议进行此动作，可能对髋关节造成损伤。",
                    "alternatives": ["臀桥", "箱式深蹲"],
                    "reasoning": "基于医疗史分析，该动作风险较高。",
                    "_mode": "mock",
                },
                ensure_ascii=False,
            )
        return json.dumps(
            {
                "risk_level": "safe",
                "should_reject": False,
                "recommendation": "该活动相对安全，注意循序渐进。",
                "reasoning": "未检测到明显风险因素。",
                "_mode": "mock",
            },
            ensure_ascii=False,
        )


_client: OpenAIClient | None = None


def get_llm_client() -> OpenAIClient:
    """Return a singleton OpenAI client."""
    global _client
    if _client is None:
        _client = OpenAIClient()
    return _client
