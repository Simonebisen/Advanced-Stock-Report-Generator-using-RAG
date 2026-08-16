# simple_mcp.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Simple Stock Server")

@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()