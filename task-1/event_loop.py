
"""
A single, persistent asyncio event loop that lives for the whole app
process, running in its own background thread.

Why this exists: MCP tool connections (stdio subprocesses wrapped in
anyio streams) are bound to the event loop they were created on. If you
load them with `asyncio.run(...)` at startup, that loop is closed the
moment `asyncio.run` returns — any later attempt to use those tools from
a *different* loop (e.g. one Flask spins up per async request) raises
"Event loop is closed" or similar RuntimeErrors.

Fix: create the loop once, keep it running forever in a background
thread, and submit every async operation — startup tool loading AND
every request — onto that same loop via run_coro().
"""
import asyncio
import threading

_loop = asyncio.new_event_loop()
_thread = threading.Thread(target=_loop.run_forever, daemon=True)
_thread.start()


def run_coro(coro):
    """Run an async coroutine on the persistent loop from sync code
    (a normal Flask view) and block until it finishes."""
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result()
