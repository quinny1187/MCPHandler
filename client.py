import logging
import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("client")


async def receive_loop(session: ClientSession):
    """Receive messages from the server."""
    logger.info("Starting receive loop")
    async for message in session.incoming_messages:
        if isinstance(message, Exception):
            logger.error("Error: %s", message)
            continue

        logger.info("Received message from server: %s", message)


async def run_session(read_stream, write_stream):
    """Run the client session."""
    async with (
        ClientSession(read_stream, write_stream) as session,
        anyio.create_task_group() as tg,
    ):
        tg.start_soon(receive_loop, session)

        logger.info("Initializing session")
        await session.initialize()
        logger.info("Session initialized")

        # Example: List available prompts
        prompts = await session.list_prompts()
        logger.info("Available Prompts: %s", prompts)

        # Example: Get the "hello-world" prompt
        result = await session.get_prompt("hello-world")
        logger.info("Prompt Result: %s", result)


async def main():
    """Main entry point for the client."""
    # Get the absolute paths using raw strings
    python_exe = os.path.abspath(r"venv\Scripts\python.exe")
    server_script = os.path.abspath("server.py")

    # Verify paths exist
    if not os.path.exists(python_exe):
        raise FileNotFoundError(f"Python executable not found at: {python_exe}")
    if not os.path.exists(server_script):
        raise FileNotFoundError(f"Server script not found at: {server_script}")

    # Create server parameters
    server_parameters = StdioServerParameters(
        command=python_exe,
        args=[server_script],
        env=os.environ.copy(),  # Pass current environment variables
    )

    # Connect to the server using stdio
    async with stdio_client(server_parameters) as streams:
        await run_session(*streams)

    print(f"Python executable path: {python_exe}")
    print(f"Server script path: {server_script}")


if __name__ == "__main__":
    anyio.run(main)
