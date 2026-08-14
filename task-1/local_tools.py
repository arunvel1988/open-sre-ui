
"""
Local (non-MCP) tools available to the agent.
These live in-process — use them for anything that doesn't need to be
its own MCP server (simple calculators, app-specific business logic, etc).

MCP is for tools that live *outside* this process (filesystem, web fetch,
your internal APIs, other people's servers). Keep genuinely local, cheap
logic here instead of wrapping it in an MCP server for no reason.
"""
from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '2 + 2 * 3'.
    Supports + - * / ( ) and decimals. No variables, no functions.
    """
    import ast
    import operator

    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported expression")

    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval(tree.body))
    except Exception as e:
        return f"Error evaluating expression: {e}"


LOCAL_TOOLS = [calculator]
