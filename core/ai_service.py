"""
Core AI service for text enhancement and chat
Supports multiple LLM providers: Gemini, Ollama
"""
import os
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

import google.generativeai as genai
from google.generativeai import GenerationConfig

from .models import NoteItem, ItemType


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, model_text: str = "gemini-1.5-flash", 
                 model_embedding: str = "embedding-001"):
        self.model_text = model_text
        self.model_embedding = model_embedding
        self._api_configured = False
        self._api_key = None
        self.cache_file = Path(".api_key_cache")
    
    def configure(self, api_key: Optional[str] = None) -> bool:
        """Configure Gemini API"""
        if api_key:
            self._api_key = api_key
        
        key = self._get_api_key()
        if key:
            genai.configure(api_key=key)
            self._api_configured = True
            return True
        return False
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from multiple sources"""
        if self._api_key:
            return self._api_key
            
        # Try environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self._api_key = api_key
            return api_key
        
        # Try cache file
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cached_key = f.read().strip()
                    if cached_key:
                        self._api_key = cached_key
                        return cached_key
        except:
            pass
        
        return None
    
    def save_api_key(self, api_key: str):
        """Save API key to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                f.write(api_key)
            self._api_key = api_key
        except Exception as e:
            print(f"Error saving API key: {e}")
    
    def get_api_key(self) -> Optional[str]:
        """Get current API key"""
        return self._get_api_key()
    
    def generate_response(self, prompt: str) -> str:
        """Generate AI response using Gemini"""
        if not self.is_configured():
            return "Error: Gemini API not configured"
        
        try:
            model = genai.GenerativeModel(self.model_text)
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1024
                )
            )
            return response.text.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Gemini"""
        if not self.is_configured():
            return []
        
        try:
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model=f"models/{self.model_embedding}",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
    
    def is_configured(self) -> bool:
        """Check if Gemini is properly configured"""
        return self._api_configured


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, model_text: str = "llama3.2:3b",
                 model_embedding: str = "nomic-embed-text",
                 base_url: str = "http://localhost:11434"):
        self.model_text = model_text
        self.model_embedding = model_embedding
        self.base_url = base_url
        self._configured = False
    
    def configure(self) -> bool:
        """Configure Ollama connection"""
        try:
            import requests
            # Test connection to Ollama
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            
            if response.status_code == 200:
                self._configured = True
                return True
                
        except requests.exceptions.ConnectionError as e:
            print(f"Ollama connection error: {e}")
        except requests.exceptions.Timeout as e:
            print(f"Ollama timeout error: {e}")
        except Exception as e:
            print(f"Ollama not available: {e}")
            
        return False
    
    def generate_response(self, prompt: str) -> str:
        """Generate AI response using Ollama"""
        if not self.is_configured():
            return "Error: Ollama not configured or not running"
        
        try:
            import requests
            
            payload = {
                "model": self.model_text,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1024
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"Error: Ollama API returned {response.status_code}"
                
        except Exception as e:
            return f"Error generating response with Ollama: {str(e)}"
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama"""
        if not self.is_configured():
            return []
        
        try:
            import requests
            embeddings = []
            
            for text in texts:
                payload = {
                    "model": self.model_embedding,
                    "prompt": text
                }
                
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embedding = result.get("embedding", [])
                    if embedding:
                        embeddings.append(embedding)
                    else:
                        # Fallback: create dummy embedding
                        embeddings.append([0.0] * 768)
                else:
                    # Fallback: create dummy embedding
                    embeddings.append([0.0] * 768)
            
            return embeddings
            
        except Exception as e:
            print(f"Error generating embeddings with Ollama: {e}")
            # Return dummy embeddings as fallback
            return [[0.0] * 768 for _ in texts]
    
    def is_configured(self) -> bool:
        """Check if Ollama is properly configured"""
        return self._configured

class AIService:
    """Central AI service supporting multiple LLM providers"""
    
    def __init__(self):
        self.config_file = Path("llm_config.json")
        self.config = self._load_config()
        self.provider = None
        self._initialize_provider()
    
    def _load_config(self) -> Dict:
        """Load LLM configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading LLM config: {e}")
        
        # Default configuration
        return {
            "llm_provider": "gemini",
            "providers": {
                "gemini": {
                    "model_text": "gemini-1.5-flash",
                    "model_embedding": "embedding-001",
                    "api_key_required": True
                },
                "ollama": {
                    "model_text": "llama3.2:3b",
                    "model_embedding": "nomic-embed-text",
                    "base_url": "http://localhost:11434",
                    "api_key_required": False
                }
            }
        }
    
    def _save_config(self):
        """Save current configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving LLM config: {e}")
    
    def _initialize_provider(self):
        """Initialize the current LLM provider"""
        provider_name = self.config.get("llm_provider", "gemini")
        provider_config = self.config["providers"].get(provider_name, {})
        
        if provider_name == "gemini":
            self.provider = GeminiProvider(
                model_text=provider_config.get("model_text", "gemini-1.5-flash"),
                model_embedding=provider_config.get("model_embedding", "embedding-001")
            )
        elif provider_name == "ollama":
            self.provider = OllamaProvider(
                model_text=provider_config.get("model_text", "llama3.2:3b"),
                model_embedding=provider_config.get("model_embedding", "nomic-embed-text"),
                base_url=provider_config.get("base_url", "http://localhost:11434")
            )
            # Auto-configure Ollama since it doesn't need API keys
            self.provider.configure()
        else:
            # Default to Gemini
            self.provider = GeminiProvider()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        return list(self.config["providers"].keys())
    
    def get_current_provider(self) -> str:
        """Get current LLM provider name"""
        return self.config.get("llm_provider", "gemini")
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different LLM provider"""
        if provider_name not in self.config["providers"]:
            return False
        
        self.config["llm_provider"] = provider_name
        self._save_config()
        self._initialize_provider()
        
        # Try to configure the new provider
        return self.configure_api()
    
    def configure_api(self, api_key: Optional[str] = None) -> bool:
        """Configure the current LLM provider"""
        if not self.provider:
            return False
        
        provider_name = self.get_current_provider()
        provider_config = self.config["providers"][provider_name]
        
        if provider_name == "gemini":
            return self.provider.configure(api_key)
        elif provider_name == "ollama":
            return self.provider.configure()
        
        return False
    
    def is_configured(self) -> bool:
        """Check if current provider is configured"""
        return self.provider and self.provider.is_configured()
    
    def generate_response(self, prompt: str) -> str:
        """Generate AI response using current provider"""
        if not self.provider:
            return "Error: No LLM provider configured"
        return self.provider.generate_response(prompt)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using current provider"""
        if not self.provider:
            return []
        return self.provider.generate_embeddings(texts)
    
    # Gemini-specific methods for backward compatibility
    def get_api_key(self) -> Optional[str]:
        """Get API key (Gemini only)"""
        if isinstance(self.provider, GeminiProvider):
            return self.provider.get_api_key()
        return None
    
    def save_api_key(self, api_key: str):
        """Save API key (Gemini only)"""
        if isinstance(self.provider, GeminiProvider):
            self.provider.save_api_key(api_key)
    
    # Additional methods for text enhancement and item detection
    def detect_item_type(self, text: str) -> ItemType:
        """Auto-detect if text is a task, resource, or note"""
        text_lower = text.lower()
        
        # Check for resource indicators
        resource_indicators = [
            'resource:', 'link:', 'url:', 'website:', 'tool:', 'document:', 'reference:', 
            'guide:', 'tutorial:', 'bookmark:', 'useful', 'check out', 'worth reading',
            'documentation', 'manual', 'article', 'blog post', 'video', 'course'
        ]
        
        has_url = any(pattern in text_lower for pattern in 
                     ['http://', 'https://', 'www.', '.com', '.org', '.net', '.io', '.edu'])
        
        is_resource = has_url or any(indicator in text_lower for indicator in resource_indicators)
        
        if is_resource:
            return ItemType.RESOURCE
        
        # Check for task indicators
        task_indicators = [
            'need to', 'have to', 'should', 'must', 'todo', 'task', 'complete', 'finish',
            'deadline', 'due', 'by', 'before', 'schedule', 'meeting', 'call', 'review',
            'prepare', 'create', 'build', 'fix', 'update', 'send', 'contact', 'follow up'
        ]
        
        is_task = any(indicator in text_lower for indicator in task_indicators)
        
        if is_task:
            return ItemType.TASK
            
        return ItemType.NOTE
    
    def enhance_text(self, text: str, 
                    item_type: Optional[ItemType] = None,
                    user_context: str = "") -> str:
        """Enhance text using AI based on detected or specified type"""
        if not self.is_configured():
            return text
        
        if item_type is None:
            item_type = self.detect_item_type(text)
        
        current_date = time.strftime("%Y-%m-%d")
        
        # Build prompt based on item type
        if item_type == ItemType.RESOURCE:
            prompt = (
                "Convert this to a clear resource description. "
                "Reply with ONLY the description, no formatting, no extra text.\n\n"
            )
        elif item_type == ItemType.TASK:
            prompt = (
                "Convert this to a clear, actionable task. "
                "Reply with ONLY the task description, no formatting, no extra text, no explanations.\n\n"
            )
        else:  # NOTE
            prompt = (
                "Make this note clear and concise. "
                "Reply with ONLY the improved note, no formatting, no extra text.\n\n"
            )
        
        if user_context:
            prompt += f"User Context:\n{user_context}\n\n"
        
        if item_type == ItemType.TASK:
            prompt += f"Input: {text}\n\nTask:"
        elif item_type == ItemType.RESOURCE:
            prompt += f"Input: {text}\n\nResource:"
        else:  # NOTE
            prompt += f"Input: {text}\n\nNote:"
        
        enhanced = self.generate_response(prompt)
        return enhanced if enhanced and not enhanced.startswith("Error:") else text
