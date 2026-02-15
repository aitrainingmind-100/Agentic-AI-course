from mcp.server.fastmcp import FastMCP
import logging
import sys

# IMPORTANT: log to STDERR so stdout stays clean for MCP protocol
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | SERVER | %(levelname)s | %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("mcp-server")

mcp = FastMCP("Math")

@mcp.tool()
def greet(name: str) -> str:
    log.info(f"greet called with name={name!r}")
    return f"Hello {name}, welcome to MCP!"

@mcp.tool()
def multiply(a: float, b: float) -> float:
    # DO NOT print() — use stderr logger
    log.info(f"multiply called: a={a}, b={b}")
    result = a * b
    log.info(f"multiply result: {result}")
    return result

if __name__ == "__main__":
    log.info("Starting MCP server over stdio...")
    mcp.run(transport="stdio")