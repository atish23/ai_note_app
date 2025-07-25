"""
AI Agent Service - Full Featured (No Complex AI Chat)
"""
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .models import NoteItem, SearchResult, ItemType
from .database_service import DatabaseService
from .ai_service import AIService
from .search_service import SearchService

@dataclass
class AgentResponse:
    """Response from agent operations"""
    success: bool
    message: str
    data: Optional[Any] = None
    items_created: Optional[List[NoteItem]] = None

class NotesAgentService:
    """Full-featured AI agent for managing notes, tasks, and resources"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.ai_service = AIService()
        self.search_service = SearchService()
    
    def initialize(self) -> bool:
        """Initialize all services"""
        try:
            return self.ai_service.is_configured()
        except Exception as e:
            print(f"Error initializing agent: {e}")
            return False
    
    def create_item(self, content: str, force_type: Optional[str] = None) -> AgentResponse:
        """Create a single note/task/resource"""
        try:
            # Check for tags first, then determine item type
            cleaned_content, detected_type = self._extract_tags(content)
            item_type = self._determine_item_type(cleaned_content, force_type or detected_type)
            
            # Enhance content with AI
            enhanced = self.ai_service.enhance_text(cleaned_content, item_type)
            
            # Generate embedding
            embedding = self.ai_service.generate_embeddings([enhanced])[0]
            
            # Create item
            item = NoteItem(
                id=None,
                timestamp=time.time(),
                raw_content=content,  # Keep original content with tags
                enhanced_content=enhanced,
                item_type=item_type,
                is_completed=False
            )
            
            # Save to database
            item_id = self.db_service.create_item(item)
            item.id = item_id
            
            # Add to search index
            self.search_service.add_item(item_id, embedding)
            
            return AgentResponse(
                success=True,
                message=f"Created {item_type.value}: {enhanced[:50]}...",
                data=item
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error creating item: {str(e)}"
            )
    
    def search_items(self, query: str, limit: int = 10, similarity_threshold: float = 0.6) -> AgentResponse:
        """Search for items using semantic search"""
        try:
            # Generate query embedding
            query_embedding = self.ai_service.generate_embeddings([query])[0]
            
            # Search
            results = self.search_service.search_similar(
                query_embedding=query_embedding,
                db_service=self.db_service,
                top_k=limit,
                similarity_threshold=similarity_threshold
            )
            
            return AgentResponse(
                success=True,
                message=f"Found {len(results)} similar items",
                data=results
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error searching: {str(e)}"
            )
    
    def complete_task(self, task_id: int) -> AgentResponse:
        """Mark task as completed"""
        try:
            success = self.db_service.update_completion_status(task_id, True)
            if success:
                return AgentResponse(
                    success=True,
                    message=f"Task {task_id} marked as completed"
                )
            else:
                return AgentResponse(
                    success=False,
                    message=f"Failed to complete task {task_id}"
                )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error completing task: {str(e)}"
            )
    
    def reopen_task(self, task_id: int) -> AgentResponse:
        """Reopen a completed task"""
        try:
            success = self.db_service.update_completion_status(task_id, False)
            if success:
                return AgentResponse(
                    success=True,
                    message=f"Task {task_id} reopened"
                )
            else:
                return AgentResponse(
                    success=False,
                    message=f"Failed to reopen task {task_id}"
                )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error reopening task: {str(e)}"
            )
    
    def delete_item(self, item_id: int) -> AgentResponse:
        """Delete an item"""
        try:
            success = self.db_service.delete_item(item_id)
            if success:
                return AgentResponse(
                    success=True,
                    message=f"Item {item_id} deleted"
                )
            else:
                return AgentResponse(
                    success=False,
                    message=f"Failed to delete item {item_id}"
                )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error deleting item: {str(e)}"
            )
    
    def get_filtered_items(self, item_type: Optional[ItemType] = None, 
                          pending_only: bool = False, 
                          completed_only: bool = False) -> List[NoteItem]:
        """Get filtered items based on type and completion status"""
        try:
            all_items = self.db_service.get_all_items()
            
            # Filter by type
            if item_type:
                all_items = [item for item in all_items if item.item_type == item_type]
            
            # Filter by completion status
            if pending_only:
                all_items = [item for item in all_items if not item.is_completed]
            elif completed_only:
                all_items = [item for item in all_items if item.is_completed]
            
            return all_items
        except Exception as e:
            print(f"Error getting filtered items: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            all_items = self.db_service.get_all_items()
            
            stats = {
                "total_items": len(all_items),
                "notes": len([i for i in all_items if i.item_type == ItemType.NOTE]),
                "tasks": len([i for i in all_items if i.item_type == ItemType.TASK]),
                "resources": len([i for i in all_items if i.item_type == ItemType.RESOURCE]),
                "completed_tasks": len([i for i in all_items if i.item_type == ItemType.TASK and i.is_completed]),
                "pending_tasks": len([i for i in all_items if i.item_type == ItemType.TASK and not i.is_completed]),
                "search_index": self.search_service.get_stats(),
                "ai_configured": self.ai_service.is_configured()
            }
            
            return stats
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {}
    
    def bulk_create_items(self, items_data: List[Dict[str, Any]]) -> AgentResponse:
        """Create multiple items at once"""
        try:
            created_items = []
            
            for item_data in items_data:
                content = item_data.get('content', '')
                force_type = item_data.get('type')
                
                if not content.strip():
                    continue
                
                result = self.create_item(content, force_type)
                if result.success and result.data:
                    created_items.append(result.data)
            
            return AgentResponse(
                success=True,
                message=f"Created {len(created_items)} items",
                items_created=created_items
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error in bulk create: {str(e)}"
            )
    
    def get_recent_items(self, limit: int = 10) -> List[NoteItem]:
        """Get most recent items"""
        try:
            all_items = self.db_service.get_all_items()
            # Sort by timestamp descending
            sorted_items = sorted(all_items, key=lambda x: x.timestamp, reverse=True)
            return sorted_items[:limit]
        except Exception as e:
            print(f"Error getting recent items: {e}")
            return []
    
    def _extract_tags(self, content: str) -> Tuple[str, Optional[str]]:
        """Extract type tags from content and return cleaned content + detected type"""
        import re
        
        # Define tag patterns
        tag_patterns = {
            r'@task\b': 'task',
            r'@note\b': 'note', 
            r'@res\b': 'resource',
            r'@resource\b': 'resource'
        }
        
        detected_type = None
        cleaned_content = content
        
        # Check for tags (case insensitive)
        for pattern, item_type in tag_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                detected_type = item_type
                # Remove the tag from content
                cleaned_content = re.sub(pattern, '', content, flags=re.IGNORECASE).strip()
                break  # Take the first tag found
        
        return cleaned_content, detected_type
    
    def _determine_item_type(self, content: str, force_type: Optional[str] = None) -> ItemType:
        """Determine the type of content"""
        if force_type:
            return ItemType(force_type.lower())
        
        content_lower = content.lower()
        
        # Resource indicators
        resource_indicators = [
            'resource:', 'link:', 'url:', 'website:', 'tool:', 'document:', 'reference:', 
            'guide:', 'tutorial:', 'bookmark:', 'useful', 'check out', 'worth reading',
            'documentation', 'manual', 'article', 'blog post', 'video', 'course'
        ]
        
        has_url = any(pattern in content_lower for pattern in ['http://', 'https://', 'www.', '.com', '.org', '.net', '.io', '.edu'])
        is_resource = has_url or any(indicator in content_lower for indicator in resource_indicators)
        
        if is_resource:
            return ItemType.RESOURCE
        
        # Task indicators
        task_indicators = [
            'need to', 'have to', 'should', 'must', 'todo', 'task', 'complete', 'finish',
            'deadline', 'due', 'by', 'before', 'schedule', 'meeting', 'call', 'review',
            'prepare', 'create', 'build', 'fix', 'update', 'send', 'contact', 'follow up'
        ]
        
        is_task = any(indicator in content_lower for indicator in task_indicators)
        if is_task:
            return ItemType.TASK
        
        return ItemType.NOTE
