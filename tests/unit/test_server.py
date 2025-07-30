"""Unit tests for the MCP server"""

import pytest
from unittest.mock import patch, MagicMock
from hatena_blog_mcp.server import create_server


@pytest.mark.asyncio
async def test_create_server():
    """Test server creation"""
    server = create_server()
    assert server is not None
    

@pytest.mark.asyncio
async def test_list_tools():
    """Test tools listing"""
    server = create_server()
    
    # Mock the list_tools handler
    tools = await server._handlers["list_tools"]()
    
    assert len(tools) == 1
    assert tools[0].name == "hello_world"
    assert "hello world tool" in tools[0].description


@pytest.mark.asyncio
async def test_hello_world_tool():
    """Test hello_world tool execution"""
    server = create_server()
    
    # Test with default name
    result = await server._handlers["call_tool"]("hello_world", {})
    assert len(result) == 1
    assert "Hello, World!" in result[0].text
    assert "Hatena Blog MCP Server" in result[0].text
    
    # Test with custom name
    result = await server._handlers["call_tool"]("hello_world", {"name": "Claude"})
    assert len(result) == 1
    assert "Hello, Claude!" in result[0].text