"""
Observability wiring.

LangSmith: purely env-var driven (LangChain/LangGraph auto-detect it).
No code changes needed elsewhere — just set the env vars before the
graph is built. See .env.example.

Langfuse: self-hosted, OSS alternative — good fit if you want everything
local like your Ollama setup. Needs an explicit CallbackHandler passed
into `.invoke(..., config={"callbacks": [...]})`.

Both can run at once; get_callbacks() returns whichever are configured.
"""
import os


def setup_langsmith():
    """Call once at startup. Reads env vars set in .env / the shell."""
    if os.getenv("LANGCHAIN_API_KEY"):
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_PROJECT", "sre-ai-agent")
        print(f"[observability] LangSmith tracing ON — project: {os.environ['LANGCHAIN_PROJECT']}")
    else:
        print("[observability] LangSmith tracing OFF (no LANGCHAIN_API_KEY set)")


def get_langfuse_handler():
    """Returns a Langfuse CallbackHandler if configured, else None."""
    if not os.getenv("LANGFUSE_PUBLIC_KEY"):
        return None
    try:
        from langfuse.callback import CallbackHandler
        handler = CallbackHandler(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
        )
        print("[observability] Langfuse tracing ON")
        return handler
    except Exception as e:
        print(f"[observability] Langfuse configured but failed to init: {e}")
        return None


def get_callbacks():
    """Collect whichever callback handlers are actually configured."""
    callbacks = []
    lf = get_langfuse_handler()
    if lf:
        callbacks.append(lf)
    return callbacks
