import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import deque
import tiktoken
from dataclasses import dataclass, asdict

from .llm_integration import MultiModelManager
from .vector_manager import VectorManager

@dataclass
class Message:
    """Message representation for conversation history"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )

@dataclass
class ConversationSession:
    """Conversation session with ring buffer for memory management"""
    session_id: str
    messages: deque
    max_history: int
    created_at: datetime
    last_activity: datetime
    
    def add_message(self, message: Message):
        """Add message to conversation with ring buffer"""
        if len(self.messages) >= self.max_history:
            self.messages.popleft()
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_messages(self, last_n: int = None) -> List[Message]:
        """Get messages from conversation"""
        if last_n is None:
            return list(self.messages)
        return list(self.messages)[-last_n:]
    
    def clear(self):
        """Clear conversation history"""
        self.messages.clear()
        self.last_activity = datetime.now()

class GarudaAIAgent:
    """Main AI Agent with multi-provider LLM and RAG capabilities"""
    
    def __init__(self, 
                 config_path: str = "config.yaml",
                 vector_store_path: str = "./data/vector_store",
                 max_history: int = 50,
                 context_window: int = 4096):
        
        self.logger = logging.getLogger(__name__)
        self.max_history = max_history
        self.context_window = context_window
        
        # Initialize components
        self.llm_manager = MultiModelManager(config_path)
        self.vector_manager = VectorManager(vector_store_path)
        
        # Initialize tokenizer for context management
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None
            self.logger.warning("Could not load tokenizer, using character count")
        
        # Conversation sessions storage
        self.sessions: Dict[str, ConversationSession] = {}
        
        # System prompt
        self.system_prompt = """You are Garuda AI Assistant, a helpful and knowledgeable AI assistant. 
You have access to uploaded documents through RAG (Retrieval-Augmented Generation) when enabled.
When RAG is active, you should use the provided context to give more accurate and detailed responses.
Always be helpful, accurate, and cite sources when using information from documents."""
        
        self.logger.info("GarudaAIAgent initialized successfully")
    
    def create_session(self, session_id: str) -> ConversationSession:
        """Create new conversation session"""
        session = ConversationSession(
            session_id=session_id,
            messages=deque(maxlen=self.max_history),
            max_history=self.max_history,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        # Add system message
        system_message = Message(
            role="system",
            content=self.system_prompt,
            timestamp=datetime.now(),
            metadata={"type": "system_init"}
        )
        session.add_message(system_message)
        
        self.sessions[session_id] = session
        self.logger.info(f"Created new session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> ConversationSession:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            return self.create_session(session_id)
        return self.sessions[session_id]
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimation: 1 token ≈ 4 characters
            return len(text) // 4
    
    def _prepare_messages_for_llm(self, 
                                  session: ConversationSession,
                                  context: str = None) -> List[Dict[str, str]]:
        """Prepare messages for LLM while managing context window"""
        
        messages = []
        current_tokens = 0
        
        # Add system message with context if available
        system_content = self.system_prompt
        if context:
            system_content += f"\n\nRelevant context from documents:\n{context}"
        
        system_msg = {"role": "system", "content": system_content}
        system_tokens = self._count_tokens(system_content)
        
        if system_tokens < self.context_window:
            messages.append(system_msg)
            current_tokens += system_tokens
        
        # Add conversation history (newest first, then reverse)
        conversation_messages = []
        for message in reversed(session.get_messages()):
            if message.role == "system":
                continue  # Skip system messages from history
                
            msg_dict = {"role": message.role, "content": message.content}
            msg_tokens = self._count_tokens(message.content)
            
            if current_tokens + msg_tokens < self.context_window:
                conversation_messages.insert(0, msg_dict)
                current_tokens += msg_tokens
            else:
                break
        
        messages.extend(conversation_messages)
        
        self.logger.debug(f"Prepared {len(messages)} messages with ~{current_tokens} tokens")
        return messages
    
    def chat(self, 
             message: str,
             session_id: str = "default",
             provider: str = "openai",
             model: str = None,
             use_rag: bool = True,
             temperature: float = 0.7,
             max_tokens: int = 2048) -> Dict[str, Any]:
        """
        Main chat function with RAG support
        
        Args:
            message: User message
            session_id: Conversation session ID
            provider: LLM provider to use
            model: Specific model to use
            use_rag: Whether to use RAG for context
            temperature: Response randomness
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict with response and metadata
        """
        
        try:
            # Get or create session
            session = self.get_session(session_id)
            
            # Add user message to session
            user_message = Message(
                role="user",
                content=message,
                timestamp=datetime.now(),
                metadata={"provider": provider, "model": model, "use_rag": use_rag}
            )
            session.add_message(user_message)
            
            # Get context from RAG if enabled
            context = ""
            rag_sources = []
            if use_rag:
                context, rag_sources = self.vector_manager.get_context(
                    message, 
                    max_context_length=self.context_window // 2  # Reserve half for conversation
                )
            
            # Prepare messages for LLM
            llm_messages = self._prepare_messages_for_llm(session, context)
            
            # Generate response
            response_data = self.llm_manager.generate(
                messages=llm_messages,
                provider=provider,
                model_name=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if response_data["success"]:
                # Add assistant message to session
                assistant_message = Message(
                    role="assistant",
                    content=response_data["response"],
                    timestamp=datetime.now(),
                    metadata={
                        "provider": response_data["provider"],
                        "model": response_data["model"],
                        "tokens_used": response_data["tokens_used"],
                        "rag_used": use_rag,
                        "rag_sources_count": len(rag_sources)
                    }
                )
                session.add_message(assistant_message)
                
                return {
                    "success": True,
                    "response": response_data["response"],
                    "provider": response_data["provider"],
                    "model": response_data["model"],
                    "tokens_used": response_data["tokens_used"],
                    "response_time": response_data.get("response_time", 0),
                    "rag_used": use_rag,
                    "rag_sources": rag_sources,
                    "fallback_used": response_data.get("fallback_used", False),
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": response_data["error"],
                    "response": response_data["response"],
                    "provider": provider,
                    "model": model,
                    "rag_used": use_rag,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error in chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request.",
                "provider": provider,
                "model": model,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def upload_document(self, file_path: str) -> Dict[str, Any]:
        """Upload and process document for RAG"""
        try:
            # Load document
            documents = self.vector_manager.load_document(file_path)
            
            # Add to vector store
            success = self.vector_manager.add_documents(documents)
            
            if success:
                return {
                    "success": True,
                    "message": f"Document uploaded successfully",
                    "file_path": file_path,
                    "chunks_created": len(documents),
                    "doc_id": documents[0].doc_id if documents else None
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to add document to vector store",
                    "file_path": file_path
                }
                
        except Exception as e:
            self.logger.error(f"Error uploading document {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents"""
        return self.vector_manager.list_documents()
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete document from vector store"""
        success = self.vector_manager.delete_document(doc_id)
        return {
            "success": success,
            "doc_id": doc_id,
            "message": "Document deleted successfully" if success else "Failed to delete document"
        }
    
    def get_conversation_history(self, session_id: str, last_n: int = None) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        if session_id not in self.sessions:
            return []
        
        session = self.sessions[session_id]
        messages = session.get_messages(last_n)
        return [msg.to_dict() for msg in messages if msg.role != "system"]
    
    def clear_conversation(self, session_id: str) -> Dict[str, Any]:
        """Clear conversation history"""
        if session_id in self.sessions:
            self.sessions[session_id].clear()
            return {"success": True, "message": f"Conversation {session_id} cleared"}
        else:
            return {"success": False, "message": f"Session {session_id} not found"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        vector_stats = self.vector_manager.get_stats()
        
        return {
            "sessions_count": len(self.sessions),
            "providers": self.llm_manager.get_providers(),
            "vector_store": vector_stats,
            "system_info": {
                "max_history": self.max_history,
                "context_window": self.context_window,
                "tokenizer_available": self.tokenizer is not None
            }
        }
    
    def test_providers(self) -> Dict[str, bool]:
        """Test all LLM providers"""
        return self.llm_manager.test_providers() 