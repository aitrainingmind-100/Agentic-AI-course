import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    print("Starting MCP client...")

    server = StdioServerParameters(
        command=sys.executable,  # IMPORTANT: same python running the client
        args=["03_Lab_MCP_Server_Simple.py"],
    )

    async with stdio_client(server) as (read, write):
        print("Connected to MCP server.")
        async with ClientSession(read, write) as session:
            print("Initializing MCP session...")
            await session.initialize()
            print("Session initialized.")

            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            r1 = await session.call_tool("greet", {"name": "Anandh"})
            print("greet:", r1.content)

            r2 = await session.call_tool("multiply", {"a": 6, "b": 7})
            print("multiply:", r2.content)

if __name__ == "__main__":
    asyncio.run(main())