import json
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class FileMemoryStore:
    def __init__(self, storage_path: str = "./storage/chat"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_user_dir(self, user_uuid: str) -> Path:
        """Get user's directory, create if doesn't exist"""
        user_dir = self.storage_path / user_uuid
        user_dir.mkdir(exist_ok=True)
        return user_dir
    
    def _get_conversation_file(self, user_uuid: str, conversation_id: str) -> Path:
        """Get conversation file path"""
        user_dir = self._get_user_dir(user_uuid)
        return user_dir / f"{conversation_id}.json"
    
    def create_conversation(self, user_uuid: str, thread_name: str = None) -> str:
        """Create a new conversation and return its ID"""
        conversation_id = str(uuid.uuid4())
        
        # Generate default name if none provided
        if not thread_name:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            thread_name = f"Chat - {timestamp}"
        
        # Create initial conversation data
        data = {
            'conversation_id': conversation_id,
            'user_uuid': user_uuid,
            'thread_name': thread_name,
            'messages': [],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'total_tokens': 0,
            'total_cost': 0.0
        }
        
        # Save to file
        file_path = self._get_conversation_file(user_uuid, conversation_id)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return conversation_id
    
    def list_conversations(self, user_uuid: str) -> List[Dict]:
        """List all conversations for a user"""
        user_dir = self._get_user_dir(user_uuid)
        conversations = []
        
        # Get all JSON files in user directory
        for file_path in user_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Return minimal info for listing
                    conversations.append({
                        'conversation_id': data['conversation_id'],
                        'thread_name': data['thread_name'],
                        'created_at': data['created_at'],
                        'updated_at': data['updated_at'],
                        'message_count': len(data['messages']),
                        'total_tokens': data.get('total_tokens', 0),
                        'total_cost': data.get('total_cost', 0.0)
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        # Sort by updated_at descending (most recent first)
        conversations.sort(key=lambda x: x['updated_at'], reverse=True)
        return conversations
    
    def load_conversation(self, user_uuid: str, conversation_id: str) -> Optional[Dict]:
        """Load a specific conversation"""
        file_path = self._get_conversation_file(user_uuid, conversation_id)
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def append_message(self, user_uuid: str, conversation_id: str, message: Dict):
        """Append a message to the conversation"""
        conversation = self.load_conversation(user_uuid, conversation_id)
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Add timestamp if not provided
        if 'timestamp' not in message:
            message['timestamp'] = datetime.utcnow().isoformat()
        
        # Append message
        conversation['messages'].append(message)
        
        # Update metadata
        conversation['updated_at'] = datetime.utcnow().isoformat()
        
        # Update token counts if provided in metadata
        if 'metadata' in message and 'tokens' in message['metadata']:
            conversation['total_tokens'] += message['metadata']['tokens']
            
        if 'metadata' in message and 'cost' in message['metadata']:
            conversation['total_cost'] += message['metadata']['cost']
        
        # Save updated conversation
        file_path = self._get_conversation_file(user_uuid, conversation_id)
        with open(file_path, 'w') as f:
            json.dump(conversation, f, indent=2)
    
    def rename_conversation(self, user_uuid: str, conversation_id: str, new_name: str) -> bool:
        """Rename a conversation"""
        conversation = self.load_conversation(user_uuid, conversation_id)
        
        if not conversation:
            return False
        
        # Update thread name
        conversation['thread_name'] = new_name
        conversation['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated conversation
        file_path = self._get_conversation_file(user_uuid, conversation_id)
        with open(file_path, 'w') as f:
            json.dump(conversation, f, indent=2)
        
        return True
    
    def delete_conversation(self, user_uuid: str, conversation_id: str) -> bool:
        """Delete a conversation"""
        file_path = self._get_conversation_file(user_uuid, conversation_id)
        
        if not file_path.exists():
            return False
        
        # Delete the file
        file_path.unlink()
        return True