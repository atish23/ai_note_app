#!/Users/amaske/Documents/AI_Note_App/venv_mcp/bin/python
"""
MCP Server for AI Notes/Task Manager
Uses shared agent service - no code duplication
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import MCP types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Import our shared agent service
from core.agent_service import NotesAgentService
from core.models import ItemType


# ---------- MCP SERVER SETUP ------------------------------------------------

# Initialize the MCP server
server = Server("ai-notes-manager")

# Global agent service
agent = NotesAgentService()

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="notes://all",
            name="All Notes/Tasks/Resources",
            description="Access to all stored notes, tasks, and resources",
        ),
        Resource(
            uri="notes://tasks",
            name="Tasks Only",
            description="Access to task items only",
        ),
        Resource(
            uri="notes://notes",
            name="Notes Only", 
            description="Access to note items only",
        ),
        Resource(
            uri="notes://resources",
            name="Resources Only",
            description="Access to resource items only",
        ),
        Resource(
            uri="notes://stats",
            name="System Statistics",
            description="System statistics and health information",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource content"""
    
    if uri == "notes://all":
        result = agent.get_all_items()
        if not result.success:
            return f"Error: {result.message}"
        
        items = result.data or []
        content = "# All Notes, Tasks & Resources\n\n"
        
        for item in items:
            status = "✅ COMPLETED" if item.is_completed else "📝 ACTIVE"
            type_emoji = {"note": "📝", "task": "✅", "resource": "🔗"}.get(item.item_type.value, "📝")
            
            content += f"## #{item.id} - {type_emoji} {item.item_type.value.title()} - {status}\n"
            content += f"**Created:** {item.formatted_date}\n\n"
            content += f"{item.enhanced_content}\n\n"
            content += "---\n\n"
        
        return content
    
    elif uri == "notes://tasks":
        result = agent.get_all_items(item_type=ItemType.TASK)
        if not result.success:
            return f"Error: {result.message}"
        
        items = result.data or []
        content = "# Tasks\n\n"
        
        for item in items:
            status = "✅ COMPLETED" if item.is_completed else "⏳ PENDING"
            content += f"## #{item.id} - {status}\n"
            content += f"**Created:** {item.formatted_date}\n\n"
            content += f"{item.enhanced_content}\n\n"
            content += "---\n\n"
        
        return content
    
    elif uri == "notes://notes":
        result = agent.get_all_items(item_type=ItemType.NOTE)
        if not result.success:
            return f"Error: {result.message}"
        
        items = result.data or []
        content = "# Notes\n\n"
        
        for item in items:
            content += f"## #{item.id} - 📝 Note\n"
            content += f"**Created:** {item.formatted_date}\n\n"
            content += f"{item.enhanced_content}\n\n"
            content += "---\n\n"
        
        return content
    
    elif uri == "notes://resources":
        result = agent.get_all_items(item_type=ItemType.RESOURCE)
        if not result.success:
            return f"Error: {result.message}"
        
        items = result.data or []
        content = "# Resources\n\n"
        
        for item in items:
            content += f"## #{item.id} - 🔗 Resource\n"
            content += f"**Created:** {item.formatted_date}\n\n"
            content += f"{item.enhanced_content}\n\n"
            content += "---\n\n"
        
        return content
    
    elif uri == "notes://stats":
        stats = agent.get_stats()
        content = "# System Statistics\n\n"
        content += f"**Total Items:** {stats.get('total_items', 0)}\n\n"
        content += f"**Notes:** {stats.get('notes', 0)}\n"
        content += f"**Tasks:** {stats.get('tasks', 0)} (Completed: {stats.get('completed_tasks', 0)}, Pending: {stats.get('pending_tasks', 0)})\n"
        content += f"**Resources:** {stats.get('resources', 0)}\n\n"
        
        search_stats = stats.get('search_index', {})
        content += f"**Search Index:** {search_stats.get('total_items', 0)} indexed items\n"
        content += f"**AI Service:** {'✅ Configured' if stats.get('ai_configured') else '❌ Not configured'}\n"
        
        return content
    
    else:
        return f"Unknown resource: {uri}"

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="create_note",
            description="Create a new note (will be auto-categorized as note/task/resource). Use tags @task, @note, @res/@resource to force specific types.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content of the note/task/resource to create. Use @task, @note, @res/@resource tags to force specific types."
                    },
                    "force_type": {
                        "type": "string",
                        "enum": ["note", "task", "resource"],
                        "description": "Force a specific type instead of auto-detection (optional)"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="chat_and_create",
            description="Have a conversation that can automatically create multiple notes/tasks/resources. Use @task, @note, @res/@resource tags for precise control.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Your message or request to the AI assistant. Use @task, @note, @res/@resource tags to force specific types."
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="search_content",
            description="Search through all notes, tasks, and resources using semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to find relevant content"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of results to return (default: 10)"
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "default": 0.6,
                        "description": "Minimum similarity score (0.0-1.0, default: 0.6)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_item",
            description="Get a specific note/task/resource by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "integer",
                        "description": "The ID of the item to retrieve"
                    }
                },
                "required": ["item_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as completed"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="reopen_task",
            description="Mark a completed task as pending by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to reopen"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_item",
            description="Delete a note/task/resource by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "integer",
                        "description": "The ID of the item to delete"
                    }
                },
                "required": ["item_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "create_note":
        content = arguments.get("content", "")
        force_type = arguments.get("force_type")
        
        if not content:
            return [TextContent(type="text", text="Error: Content is required")]
        
        result = agent.create_item(content, force_type)
        return [TextContent(type="text", text=result.message)]
    
    elif name == "chat_and_create":
        message = arguments.get("message", "")
        
        if not message:
            return [TextContent(type="text", text="Error: Message is required")]
        
        result = agent.chat_and_create(message)
        return [TextContent(type="text", text=result.message)]
    
    elif name == "search_content":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        similarity_threshold = arguments.get("similarity_threshold", 0.6)
        
        if not query:
            return [TextContent(type="text", text="Error: Search query is required")]
        
        result = agent.search_items(query, limit, similarity_threshold)
        
        if not result.success:
            return [TextContent(type="text", text=f"Error: {result.message}")]
        
        results = result.data or []
        if not results:
            return [TextContent(type="text", text="No similar items found")]
        
        response = f"Found {len(results)} similar items:\n\n"
        for search_result in results:
            item = search_result.item
            score = search_result.similarity_score
            type_emoji = {"note": "📝", "task": "✅", "resource": "🔗"}.get(item.item_type.value, "📝")
            status = " (✅ Completed)" if item.is_completed else ""
            
            response += f"{type_emoji} **#{item.id}** - {item.item_type.value.title()}{status} (Score: {score:.3f})\n"
            response += f"*{item.formatted_date}*\n"
            response += f"{item.enhanced_content[:100]}...\n\n"
        
        return [TextContent(type="text", text=response)]
    
    elif name == "get_item":
        item_id = arguments.get("item_id")
        
        if item_id is None:
            return [TextContent(type="text", text="Error: item_id is required")]
        
        result = agent.get_item(item_id)
        
        if not result.success:
            return [TextContent(type="text", text=result.message)]
        
        item = result.data
        type_emoji = {"note": "📝", "task": "✅", "resource": "🔗"}.get(item.item_type.value, "📝")
        status = " (✅ Completed)" if item.is_completed else ""
        
        response = f"{type_emoji} **#{item.id}** - {item.item_type.value.title()}{status}\n"
        response += f"**Created:** {item.formatted_date}\n\n"
        response += f"**Raw:** {item.raw_content}\n\n"
        response += f"**Enhanced:** {item.enhanced_content}\n"
        
        return [TextContent(type="text", text=response)]
    
    elif name == "complete_task":
        task_id = arguments.get("task_id")
        
        if task_id is None:
            return [TextContent(type="text", text="Error: task_id is required")]
        
        result = agent.complete_task(task_id)
        return [TextContent(type="text", text=result.message)]
    
    elif name == "reopen_task":
        task_id = arguments.get("task_id")
        
        if task_id is None:
            return [TextContent(type="text", text="Error: task_id is required")]
        
        result = agent.reopen_task(task_id)
        return [TextContent(type="text", text=result.message)]
    
    elif name == "delete_item":
        item_id = arguments.get("item_id")
        
        if item_id is None:
            return [TextContent(type="text", text="Error: item_id is required")]
        
        result = agent.delete_item(item_id)
        return [TextContent(type="text", text=result.message)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    # Initialize agent
    if not agent.initialize():
        print("❌ Failed to initialize agent - check API key configuration")
        print("💡 Run the Streamlit app first to set up your API key")
        return
    
    print("🚀 AI Notes/Task Manager MCP Server starting...")
    print("🔧 Agent service initialized successfully")
    
    # Import transport
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ai-notes-manager",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(
                        resources_changed=True,
                        tools_changed=True
                    ),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
