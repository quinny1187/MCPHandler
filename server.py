from mcp.server import Server
from mcp.server.models import InitializationOptions, ServerCapabilities
import mcp.types as types

# Create a server instance
server = Server("example-server")

# Add a simple prompt capability
@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="hello-world",
            description="A simple prompt that says hello",
        )
    ]

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    if name != "hello-world":
        raise ValueError(f"Unknown prompt: {name}")

    return types.GetPromptResult(
        messages=[
            types.PromptMessage(
                role="assistant",
                content=types.TextContent(type="text", text="Hello, world!")
            )
        ],
        description="A simple hello-world prompt",
    )

# Run the server
if __name__ == "__main__":
    import anyio
    from mcp.server.stdio import stdio_server

    async def main():
        import sys
        print("Starting MCP server...", file=sys.stderr)
        async with stdio_server() as streams:
            await server.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name="example-server",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        list_prompts=True,
                        get_prompt=True
                    )
                )
            )
        print("MCP server is now running.")

    anyio.run(main)
