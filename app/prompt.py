def build_sql_prompt(question: str, schema: str) -> str:
    """
    Builds the prompt in the format expected by SQLCoder.
    Reference: https://huggingface.co/defog/sqlcoder-7b-2

    The schema is injected as a CREATE TABLE statement so the model
    knows the exact column names and types before generating the query.
    """
    return f"""### Task
Generate a SQL query to answer [QUESTION]{question}[/QUESTION]

### Database Schema
The query will run on a database with the following schema:
{schema}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{question}[/QUESTION]
[SQL]"""


def build_nl_prompt(question: str, results: list[dict]) -> str:
    """
    Builds the prompt for llama3.2 to translate SQL results into
    a natural language sentence.
    """
    return f"""A user asked: "{question}"

The database returned these results: {results}

Write a single, concise sentence answering the user's question based on these results.
Be direct and natural. Do not explain the query or mention SQL or databases."""
