import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():

    print("Loading MCP configuration...")

    # Load MCP JSON config
    with open("mcp.json", "r") as f:
        config = json.load(f)

    postgres_config = config["mcpServers"]["postgres"]

    server = StdioServerParameters(
        command=postgres_config["command"],
        args=postgres_config["args"]
    )

    print("Starting Postgres MCP server via npx...")

    async with stdio_client(server) as (read, write):
        print("Connected to Postgres MCP server.")

        async with ClientSession(read, write) as session:
            print("Initializing session...")
            await session.initialize()
            print("Session initialized.")

            # List tools
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print("Available tools:", tool_names)

            # Most official server exposes "query"
            tool_name = "query" if "query" in tool_names else tool_names[0]

            print("\nRunning SQL query...")
            result = await session.call_tool(
                tool_name,
                {"sql": "SELECT * from users"}
            )

            print("\nQuery Result:")
            print(result.content)

if __name__ == "__main__":
    asyncio.run(main())