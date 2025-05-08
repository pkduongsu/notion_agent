# notion_agent/tools.py
import os
import asyncio
import os
import platform
from google.adk.tools.mcp_tool import MCPToolset
from mcp.client.stdio import StdioServerParameters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

_notion_tools = None
_exit_stack = None

def get_notion_tools():
    """Return empty tools list until MCPTools are initialized"""
    # This is a placeholder that will be replaced when init_notion_tools is called
    return []

async def init_notion_tools():
    """Initialize Notion MCP tools"""
    global _notion_tools, _exit_stack

    notion_token = os.environ.get("NOTION_TOKEN")

    try:
        print("Initializing Notion MCP tools...")
        # Set up Notion MCP tools
        _notion_tools, _exit_stack = await MCPToolset.from_server(
            connection_params=StdioServerParameters(
                command="npx",
                args=["-y", "@notionhq/notion-mcp-server"],
                env={
                    "OPENAPI_MCP_HEADERS": f'{{"Authorization": "Bearer {notion_token}", "Notion-Version": "2022-06-28"}}',
                }
            )
        )
        
        # Override the get_notion_tools function to return the actual tools
        global get_notion_tools
        def get_notion_tools():
            tools = _notion_tools.get_tools()
            print(f"Notion tools available: {len(tools)}")
            return tools
        
        print(f"Successfully loaded Notion MCP tools")
    except Exception as e:
        import traceback
        print(f"Error initializing Notion MCP tools: {e}")
        print(f"Detailed error: {traceback.format_exc()}")