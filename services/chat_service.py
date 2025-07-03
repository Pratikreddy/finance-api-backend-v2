from typing import Dict, Optional, List
from storage.file_memory import FileMemoryStore
from llm_agent.agent_multi import run_pinescript_agent
import json

class ChatService:
    def __init__(self):
        self.storage = FileMemoryStore()
    
    async def process_chat(
        self,
        user_uuid: str,
        query: str,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """Process a chat query WITH STORAGE - ALWAYS STORES"""
        
        # Build context from previous messages if conversation_id provided
        previous_summary = "No previous conversation."
        
        if conversation_id:
            conversation = self.storage.load_conversation(user_uuid, conversation_id)
            if conversation and conversation['messages']:
                # Build summary from last few messages
                recent_messages = conversation['messages'][-5:]  # Last 5 messages
                summary_parts = []
                
                for msg in recent_messages:
                    if msg['role'] == 'user':
                        summary_parts.append(f"User: {msg['content']}")
                    elif msg['role'] == 'assistant':
                        # Try to get summary from metadata
                        if 'metadata' in msg and 'full_response' in msg['metadata']:
                            chat_summary = msg['metadata']['full_response'].get('chatsummary', '')
                            if chat_summary:
                                summary_parts.append(chat_summary)
                        else:
                            summary_parts.append(f"Assistant: {msg['content'][:100]}...")
                
                if summary_parts:
                    previous_summary = " ".join(summary_parts[-3:])  # Last 3 exchanges
        
        # Run the agent
        response_json, tokens, cost, _, _ = run_pinescript_agent(query, previous_summary)
        
        # Parse the response
        response = json.loads(response_json)
        
        # ALWAYS store the conversation
        # Create new conversation if no ID provided
        if not conversation_id:
            conversation_id = self.storage.create_conversation(
                user_uuid=user_uuid,
                thread_name=f"Chat - {query[:50]}..."
            )
        
        # Store user message
        user_message = {
            'role': 'user',
            'content': query
        }
        self.storage.append_message(user_uuid, conversation_id, user_message)
        
        # Store assistant message with metadata
        assistant_message = {
            'role': 'assistant',
            'content': response.get('answer', '')[:500],  # Store first 500 chars
            'metadata': {
                'tokens': tokens,
                'cost': cost,
                'full_response': response
            }
        }
        self.storage.append_message(user_uuid, conversation_id, assistant_message)
        
        # Add conversation_id to response
        response['conversation_id'] = conversation_id
        response['tokens_used'] = tokens
        response['cost'] = cost
        
        return response
    
    def list_conversations(self, user_uuid: str) -> List[Dict]:
        """List all conversations for a user"""
        return self.storage.list_conversations(user_uuid)
    
    def get_conversation(self, user_uuid: str, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation"""
        return self.storage.load_conversation(user_uuid, conversation_id)
    
    def rename_conversation(self, user_uuid: str, conversation_id: str, new_name: str) -> bool:
        """Rename a conversation"""
        return self.storage.rename_conversation(user_uuid, conversation_id, new_name)
    
    def delete_conversation(self, user_uuid: str, conversation_id: str) -> bool:
        """Delete a conversation"""
        return self.storage.delete_conversation(user_uuid, conversation_id)