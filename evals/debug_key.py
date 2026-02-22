import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")

BASE_URLS = [
    "https://tbnx.plus7.plus",
    "https://tbnx.plus7.plus/",
    "https://tbnx.plus7.plus/v1",
    "https://tbnx.plus7.plus/v1/chat/completions",
]


def test_openai(base_url: str):
    try:
        client = OpenAI(api_key=OPENAI_KEY, base_url=base_url)
        start = time.time()
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        latency = time.time() - start
        return True, f"ok latency={latency:.2f}s output={resp.choices[0].message.content}"
    except Exception as exc:  # noqa: BLE001
        return False, f"error: {exc}"


def main():
    for url in BASE_URLS:
        ok, msg = test_openai(url)
        print(f"{url} -> {msg}")
        if ok:
            print(f"RESULT: success with {url}")
            return
    print("RESULT: failed for all base_url variants")


if __name__ == "__main__":
    main()
