import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import execute_query, get_schema
from model import generate_natural_response, generate_sql
from prompt import build_nl_prompt, build_sql_prompt

app = FastAPI(
    title="SQL Query App",
    description="Natural language to SQL query application",
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
async def health():
    """Check the status of all downstream services."""
    try:
        get_schema()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(OLLAMA_URL)
            ollama_status = "ok" if resp.status_code == 200 else f"error: {resp.status_code}"
    except Exception as e:
        ollama_status = f"error: {e}"

    return {"database": db_status, "ollama": ollama_status}


@app.get("/schema")
def schema():
    """Return the sales table schema. Useful for debugging and UI display."""
    try:
        return {"schema": get_schema()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query(request: QueryRequest):
    """
    Full pipeline: natural language → SQL → results → natural language answer.

    1. Fetch the live table schema from PostgreSQL
    2. Build a SQLCoder prompt with schema injection
    3. Generate SQL via Ollama (sqlcoder:7b)
    4. Execute the SQL on PostgreSQL
    5. Generate a natural language answer via Ollama (llama3.2:3b)
    """
    schema = get_schema()

    sql_prompt = build_sql_prompt(request.question, schema)
    sql = await generate_sql(sql_prompt)

    try:
        results = execute_query(sql)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={"error": f"Generated SQL failed to execute: {str(e)}", "sql": sql},
        )

    nl_prompt = build_nl_prompt(request.question, results)
    answer = await generate_natural_response(nl_prompt)

    return {
        "question": request.question,
        "sql": sql,
        "results": results,
        "answer": answer,
    }
