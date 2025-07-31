"""
Hatena Blog MCP Server using FastMCP for simplified implementation.
"""

import logging
from typing import Annotated

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hatena-mcp-server")

# Create FastMCP server
mcp = FastMCP("hatena-blog-mcp")


@mcp.tool()
def hello_world(
    name: Annotated[str, "Name to say hello to"] = "World"
) -> str:
    """A simple hello world tool for testing MCP server connectivity"""

    logger.info(f"Hello world tool called with name: {name}")

    try:
        response_text = f"Hello, {name}! This is the Hatena Blog MCP Server."
        return response_text
    except Exception as e:
        logger.error(f"Error in hello_world tool: {e}")
        return f"エラーが発生しました: {str(e)}"


def main() -> None:
    """Main entry point for the MCP server"""
    logger.info("Starting Hatena Blog MCP Server with FastMCP")
    mcp.run()


if __name__ == "__main__":
    main()
