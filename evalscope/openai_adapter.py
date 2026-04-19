from __future__ import annotations

import os


def run_openai_prompt(model: str, prompt: str, system: str | None = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Use simulate_output in your spec for local dry runs."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The openai package is not installed. Run `pip install -e .` first."
        ) from exc

    client = OpenAI(api_key=api_key)
    input_messages: list[dict[str, str]] = []
    if system:
        input_messages.append({"role": "system", "content": system})
    input_messages.append({"role": "user", "content": prompt})

    response = client.responses.create(model=model, input=input_messages)
    text = getattr(response, "output_text", "")
    if not text:
        raise RuntimeError("OpenAI response did not include output_text")
    return text
