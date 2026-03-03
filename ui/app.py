import os

import httpx
import pandas as pd
import streamlit as st

API_URL = os.getenv("API_URL", "http://app:8000")

st.set_page_config(
    page_title="SQL Query App",
    layout="centered",
)

st.title("SQL Query App")
st.caption("Ask questions about your sales data in plain English")

# ── Sidebar: system status + schema ──────────────────────────────────────────
with st.sidebar:
    st.header("System Status")
    try:
        health = httpx.get(f"{API_URL}/health", timeout=5).json()
        db_ok = health["database"] == "ok"
        ol_ok = health["ollama"] == "ok"
        st.markdown(f"{'✅' if db_ok else '❌'} **Database:** {health['database']}")
        st.markdown(f"{'✅' if ol_ok else '❌'} **Ollama:** {health['ollama']}")
    except Exception as e:
        st.error(f"API unreachable: {e}")

    st.divider()

    st.header("Table Schema")
    try:
        schema = httpx.get(f"{API_URL}/schema", timeout=5).json()["schema"]
        st.code(schema, language="sql")
    except Exception:
        st.warning("Schema unavailable")

# ── Main area ─────────────────────────────────────────────────────────────────
question = st.text_input(
    "Your question",
    placeholder="What is the most bought product on Fridays?",
)

if st.button("Ask", type="primary", disabled=not question):
    with st.spinner("Generating SQL and running query..."):
        try:
            resp = httpx.post(
                f"{API_URL}/query",
                json={"question": question},
                timeout=180.0,
            )

            if resp.status_code == 200:
                data = resp.json()

                # Natural language answer — most prominent element
                st.success(data["answer"])

                # Generated SQL — always visible for transparency
                with st.expander("Generated SQL", expanded=True):
                    st.code(data["sql"], language="sql")

                # Raw results as a table
                if data["results"]:
                    with st.expander("Results", expanded=True):
                        st.dataframe(
                            pd.DataFrame(data["results"]),
                            use_container_width=True,
                        )
                else:
                    st.info("The query returned no results.")

            elif resp.status_code == 422:
                # SQL was generated but failed to execute
                detail = resp.json()["detail"]
                st.error(detail["error"])
                with st.expander("Generated SQL (failed)", expanded=True):
                    st.code(detail["sql"], language="sql")

            else:
                st.error(f"Unexpected error ({resp.status_code}): {resp.text}")

        except httpx.TimeoutException:
            st.error(
                "The request timed out. The model may still be loading — "
                "please wait a moment and try again."
            )
        except Exception as e:
            st.error(f"Could not reach the API: {e}")
