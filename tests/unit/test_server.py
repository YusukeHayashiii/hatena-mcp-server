"""Unit tests for the MCP server"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from hatena_blog_mcp.server import hello_world


def test_hello_world_default():
    """Test hello_world tool with default parameters"""
    result = hello_world()
    assert "Hello, World!" in result
    assert "Hatena Blog MCP Server" in result


def test_hello_world_custom_name():
    """Test hello_world tool with custom name"""
    result = hello_world("Claude")
    assert "Hello, Claude!" in result
    assert "Hatena Blog MCP Server" in result


def test_hello_world_empty_name():
    """Test hello_world tool with empty name"""
    result = hello_world("")
    assert "Hello, !" in result
    assert "Hatena Blog MCP Server" in result
