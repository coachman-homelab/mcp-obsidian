import logging
import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP, Context

# Import your existing tool definitions
from . import tools

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian")

api_key = os.getenv("OBSIDIAN_API_KEY")
if not api_key:
    raise ValueError(f"OBSIDIAN_API_KEY environment variable required.")

# Initialize FastMCP instead of the raw Server
mcp = FastMCP("mcp-obsidian")

# --- Bridge Logic ---
# This helper function bridges your existing class-based tools 
# to the FastMCP function-based system.
def register_tool_handler(handler_class):
    handler = handler_class()
    tool_def = handler.get_tool_description()
    
    # We define a dynamic function that mimics the tool's signature
    # This allows FastMCP to serve it correctly
    async def wrapper(**kwargs):
        try:
            # Your handlers expect a specific input structure
            result_list = handler.run_tool(kwargs)
            # FastMCP expects a string or list of content. 
            # Your tools return a list of [TextContent], so we extract the text.
            if result_list and hasattr(result_list[0], 'text'):
                return result_list[0].text
            return "No content returned"
        except Exception as e:
            logger.error(str(e))
            return f"Error: {str(e)}"

    # Register the tool with FastMCP using the metadata from your existing classes
    mcp.tool(
        name=tool_def.name,
        description=tool_def.description,
    )(wrapper)

# --- Register All Your Tools ---
register_tool_handler(tools.ListFilesInDirToolHandler)
register_tool_handler(tools.ListFilesInVaultToolHandler)
register_tool_handler(tools.GetFileContentsToolHandler)
register_tool_handler(tools.SearchToolHandler)
register_tool_handler(tools.PatchContentToolHandler)
register_tool_handler(tools.AppendContentToolHandler)
register_tool_handler(tools.PutContentToolHandler)
register_tool_handler(tools.DeleteFileToolHandler)
register_tool_handler(tools.ComplexSearchToolHandler)
register_tool_handler(tools.BatchGetFileContentsToolHandler)
register_tool_handler(tools.PeriodicNotesToolHandler)
register_tool_handler(tools.RecentPeriodicNotesToolHandler)
register_tool_handler(tools.RecentChangesToolHandler)

# FastMCP handles the execution loop automatically (supports both SSE and Stdio)
if __name__ == "__main__":
    mcp.run()
