"""
API Manager for multi-key Gemini API management
"""
import os
import logging
import random
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from datetime import datetime
# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages multiple Gemini API keys with load balancing and failover"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        
    def _load_api_keys(self) -> List[str]:
        """Load API keys from environment variables"""
        keys = []
        
        # Try to load multiple keys
        base_key = os.getenv("GOOGLE_API_KEY") 
        if base_key:
            keys.append(base_key)
        for i in range(1, 10):
            key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if key:
                keys.append(key)
        if not keys:
            raise ValueError("No Google API keys found in environment variables")
        
        logger.info(f"Loaded {len(keys)} API keys")
        return keys
    
    def get_next_key(self) -> str:
        """Get next API key using round-robin"""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def get_random_key(self) -> str:
        """Get random API key"""
        return random.choice(self.api_keys)

class ConversationManager:
    """Manages conversation history by conversation_id and user_id"""
    def __init__(self):
        self.conversations: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    
    def get_conversation_key(self, conversation_id: str, user_id: str) -> str:
        return f"{user_id}:{conversation_id}"
    
    def add_message(self, conversation_id: str, user_id: str, message: Dict[str, Any]):
        key = self.get_conversation_key(conversation_id, user_id)
        if key not in self.conversations:
            self.conversations[key] = []
        
        message['timestamp'] = datetime.now().isoformat()
        self.conversations[key].append(message)
        
        # Keep only last 20 messages per conversation
        if len(self.conversations[key]) > 20:
            self.conversations[key] = self.conversations[key][-20:]
    
    def get_history(self, conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
        key = self.get_conversation_key(conversation_id, user_id)
        return self.conversations.get(key, [])

# Global conversation manager
conversation_manager = None
# Global API key manager
_key_manager = None

def get_conversation_manager() -> ConversationManager:
    """Get global conversation manager instance"""
    global conversation_manager
    if conversation_manager is None:
        conversation_manager = ConversationManager()
    return conversation_manager

def get_key_manager() -> APIKeyManager:
    """Get global API key manager instance"""
    global _key_manager
    if _key_manager is None:
        _key_manager = APIKeyManager()
    return _key_manager

def get_llm(model_name: str = "gemini-2.5-flash-lite", temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """Get LLM instance with automatic key management"""
    try:
        key_manager = get_key_manager()
        api_key = key_manager.get_next_key()
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key  # Use correct parameter name
        )
    except Exception as e:
        logger.error(f"Error creating LLM instance: {e}")
        raise