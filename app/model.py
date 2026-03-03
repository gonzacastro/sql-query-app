import os
import re

import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")


def clean_sql(raw: str) -> str:
    """
    Extract clean SQL from model output.
    SQLCoder sometimes wraps the query in markdown or adds extra text —
    this function strips all of that and returns only the first SQL statement.
    """
    raw = re.sub(r"\[SQL\]", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```sql\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```\s*", "", raw)

    parts = [p.strip() for p in raw.split(";") if p.strip()]
    if parts:
        return parts[0].strip() + ";"
    return raw.strip()


async def generate_sql(prompt: str) -> str:
    """Call SQLCoder via Ollama to translate a natural language prompt into SQL."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "sqlcoder:7b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},
            },
        )
        response.raise_for_status()
        return clean_sql(response.json()["response"])


async def generate_natural_response(prompt: str) -> str:
    """Call llama3.2 via Ollama to translate SQL results into natural language."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3},
            },
        )
        response.raise_for_status()
        return response.json()["response"].strip()
