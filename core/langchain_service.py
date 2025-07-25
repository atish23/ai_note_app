"""
Simple Chat service for AI Notes/Task Manager
Provides basic conversational capabilities without LangChain dependency
"""
import time
import json
from typing import List, Dict, Any, Optional

# Import local services
from .models import NoteItem, SearchResult, ItemType
from .agent_service import AgentResponse
from .ai_service import AIService
from .database_service import DatabaseService
from .search_service import SearchService


class LangChainService:
    """Simple chat service without LangChain dependency"""
    
    def __init__(self, ai_service, db_service, search_service):
        self.ai_service = ai_service
        self.db_service = db_service
        self.search_service = search_service
        print("Simple chat service initialized (no LangChain)")
    
    def run_agent(self, user_input: str):
        """Run a simple conversational agent without LangChain"""
        try:
            # Get relevant context from existing items
            context_items = self._get_relevant_context(user_input)
            
            # Build context string
            context_str = ""
            if context_items:
                context_str = "\n\nRelevant items from your workspace:\n"
                for item in context_items[:3]:  # Limit to 3 most relevant
                    context_str += f"• {item.item_type.value.title()}: {item.enhanced_content[:100]}...\n"
            
            # Create a simple prompt
            prompt = f"""You are an AI assistant that helps users manage their work. 

User message: "{user_input}"
{context_str}

Please provide a helpful response. If the user wants to create items, search for items, or complete tasks, let them know you can help with that."""
            
            response = self.ai_service.generate_response(prompt)
            
            return AgentResponse(
                success=True,
                message=response,
                items_created=[]
            )
            
        except Exception as e:
            import traceback
            print(f"Error in simple chat agent: {str(e)}")
            print(traceback.format_exc())
            return AgentResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    def _get_relevant_context(self, query: str, limit: int = 5) -> List[NoteItem]:
        """Get relevant context items for the query"""
        try:
            if not self.ai_service.is_configured():
                return []
                
            # Generate query embedding
            query_embedding = self.ai_service.generate_embeddings([query])[0]
            
            # Search for similar items
            results = self.search_service.search_similar(
                query_embedding=query_embedding,
                db_service=self.db_service,
                top_k=limit,
                similarity_threshold=0.7
            )
            
            return [result.item for result in results]
            
        except Exception as e:
            print(f"Error getting context: {e}")
            return []
