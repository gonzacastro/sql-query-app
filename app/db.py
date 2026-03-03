import os

import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "salesdb"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
    )


def get_schema() -> str:
    """
    Returns the sales table schema as a CREATE TABLE statement.
    Queried dynamically from PostgreSQL so it stays in sync with the actual table.
    The 'id' column is excluded — it's internal and would confuse the model.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length,
                       numeric_precision, numeric_scale
                FROM information_schema.columns
                WHERE table_name = 'sales'
                  AND table_schema = 'public'
                  AND column_name != 'id'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()

    col_defs = []
    for col_name, data_type, char_len, num_prec, num_scale in columns:
        if data_type == "character varying":
            type_str = f"VARCHAR({char_len})" if char_len else "VARCHAR"
        elif data_type == "numeric":
            type_str = f"NUMERIC({num_prec},{num_scale})" if num_prec else "NUMERIC"
        else:
            type_str = data_type.upper()
        col_defs.append(f"    {col_name} {type_str}")

    return "CREATE TABLE sales (\n" + ",\n".join(col_defs) + "\n);"


def execute_query(sql: str) -> list[dict]:
    """Execute a SQL query and return results as a list of dicts."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            return [dict(row) for row in cur.fetchall()]
