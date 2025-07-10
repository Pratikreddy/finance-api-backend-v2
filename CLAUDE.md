# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Generated: July 3, 2025 at 9:00 PM PST (Updated with UUID-based conversation storage)

## Project Overview

This is the **Astryx AI Microservice** (v0.1.0) - a sophisticated FastAPI-based trading strategy consultation service that generates PineScript code and interactive visualizations. The service uses Azure OpenAI through LangGraph agents to provide expert trading advice with automated code generation, real token usage tracking, and **UUID-based conversation storage**.

### Key Features
- **Stateless Service**: No memory between requests - context passed via API
- **Conversation Storage**: UUID-based file storage for conversation history
- **Thread Management**: Create, list, rename, and delete conversation threads
- **Context via API**: Previous summary passed in request JSON (no buffer memory)
- **Token & Cost Tracking**: Accurate tracking of token usage and costs per conversation
- **Dual Visualizations**: shadcn/ui components and ApexCharts for strategy visualization
- **Mandatory Storage**: ALL conversations are ALWAYS stored (no optional flag)

## Package Management & Versioning

- **Python Version**: 3.13+ (required in pyproject.toml)
- **Package Manager**: pip with requirements.txt (uv.lock exists but pip is used for installation)
- **Project Version**: 0.1.0 (defined in pyproject.toml)
- **Dependencies**: Pinned versions in requirements.txt for reproducible builds
- **Key Dependencies**: 
  - LangGraph 0.5.1 (for agent orchestration)
  - LangChain-Core 0.3.67 (for base functionality)
  - Azure OpenAI (through langchain-openai 0.3.16)

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Service
```bash
# Development server with auto-reload
uvicorn main:app --reload

# Production-like setup with specific host/port
python3 -m uvicorn main:app --host 0.0.0.0 --port 8503 --reload
```

### Testing API
```bash
# Health check
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"query": "Create a simple RSI strategy"}}'
```

## Architecture Overview

### Core Architecture Pattern
- **FastAPI + LangServe**: RESTful API with LangChain integration for streaming and batch processing
- **LangGraph Agent**: Modern LangGraph 0.5.1 with real token tracking
- **Stateless Design**: No memory between requests - context passed via previous_summary in API
- **Conversation Storage**: File-based storage with UUID organization (not in-memory state)
- **Dual-Agent System**: Main trading consultant + specialized PineScript code generator tool
- **Azure OpenAI Integration**: Environment-based configuration with tool calling support
- **Token Tracking**: Real usage tracking with UsageMetadataCallbackHandler (~3,400 tokens per complex query)

### Key Components

#### 1. FastAPI Application (`main.py`)
- **LangServe Integration**: Uses `add_routes()` to expose LangChain agent as REST API
- **CORS Configuration**: Allows all origins for development
- **Health Endpoint**: Returns service status and feature list
- **Request Processing**: Converts chat input to agent format and handles JSON responses

#### 2. Configuration Management (`core/config.py`)
- **Pydantic Settings**: Environment variable validation and type checking
- **Azure OpenAI Config**: API key, endpoint, deployment, and version management
- **Environment File**: Loads from `.env` file with case-sensitive variables

#### 3. Agent System (`llm_agent/`)
- **Main Agent** (`agent_multi.py`): LangGraph-based agent that coordinates trading strategy consultation
  - Uses `create_react_agent` from LangGraph for tool orchestration
  - Implements custom response formatting to maintain API compatibility
  - Tracks token usage through callbacks
- **System Prompts** (`prompts_multi.py`): Detailed markdown formatting instructions
- **Specialized Tool** (`tools_multi.py`): PineScript code generation with knowledge base
- **Knowledge Base** (`pinescript_knowledge.txt`): Domain-specific PineScript v5 patterns

#### 4. Storage System (`storage/`)
- **FileMemoryStore** (`file_memory.py`): UUID-based conversation storage
  - Folder structure: `./storage/chat/{user_uuid}/{conversation_id}.json`
  - Auto-generated thread names: "Chat - YYYY-MM-DD HH:MM"
  - Tracks total tokens and costs per conversation
  - Stores full response metadata for each message

#### 5. Authentication (`core/auth.py`)
- **Header-based Auth**: Reads `x-user-uuid` from request headers
- **Test UUID Fallback**: Uses default UUID for development
- **User Model**: Simple User class with UUID property

#### 6. Chat Service (`services/chat_service.py`)
- **Process Chat**: ALWAYS stores conversations (no optional storage)
- **Context Building**: Builds previous_summary from stored messages
- **Thread Management**: Create, list, load, rename, delete conversations
- **Metadata Tracking**: Stores tokens, cost, and full responses

### Response Pipeline Architecture

1. **User Query** → FastAPI endpoint
2. **Agent Processing** → LangChain agent with tools
3. **Tool Execution** → Specialized PineScript generator
4. **Response Formatting** → JSON with markdown fields
5. **Visualization Generation** → React components + ApexCharts configs

## Environment Configuration

### Required .env Variables
```env
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### LLM Configuration
- **Temperature**: 0 (main agent), 0.1 (PineScript tool)
- **Model Version**: "0125" for proper tool calling support
- **Response Format**: Tool calls for code generation, then formatted to JSON
- **Max Iterations**: 10 (recursion_limit in LangGraph)
- **API Version**: 2025-01-01-preview for Azure OpenAI
- **Token Tracking**: Enabled with UsageMetadataCallbackHandler

## API Structure

### Chat Endpoints
- `/chat/invoke` - Single query processing with automatic storage
- `/chat/stream` - Streaming responses for real-time output
- `/chat/batch` - Multiple query processing
- `/chat/playground` - Interactive testing interface

### Thread Management Endpoints
- `POST /threads/new` - Create new conversation thread
- `GET /threads/list` - List all user conversations
- `GET /threads/{id}` - Get specific conversation
- `PUT /threads/{id}/rename` - Rename conversation thread
- `DELETE /threads/{id}` - Delete conversation thread

### Other Endpoints
- `/health` - Service health check with feature list
- `/` - Root endpoint with API documentation

### Request Format
```json
{
  "input": {
    "query": "Trading strategy question",
    "user_uuid": "optional-user-uuid",
    "conversation_id": "optional-existing-conversation-id"
  }
}
```

### Response Format
```json
{
  "output": {
    "answer": "# Markdown Strategy Explanation\n\n## Overview\nDetailed explanation...\n\n## PineScript Implementation\n\n```pinescript\n//@version=5\nstrategy(...)\n```\n\n## Visualization\n\n```jsx\nimport { Card } from '@/components/ui/card';\n...\n```",
    "chatsummary": "User requested X. Provided Y with Z.",
    "whatsapp_summary": "*User Query*\n\nKey Parameters:\n• Parameter 1\n• Parameter 2\n\nBrief description of what was generated...\n\n_Full details in main response_",
    "conversation_id": "uuid-of-conversation",
    "tokens_used": 3456,
    "cost": 0.0345
  },
  "metadata": {
    "run_id": "execution-uuid",
    "feedback_tokens": []
  }
}
```

### Storage Data Format
```json
{
  "conversation_id": "uuid",
  "user_uuid": "user-uuid",
  "thread_name": "Chat - 2025-07-03 20:30",
  "messages": [
    {
      "role": "user",
      "content": "User's query",
      "timestamp": "2025-07-03T20:30:00.000Z"
    },
    {
      "role": "assistant",
      "content": "First 500 chars of answer...",
      "timestamp": "2025-07-03T20:30:05.000Z",
      "metadata": {
        "tokens": 3456,
        "cost": 0.0345,
        "full_response": {
          "answer": "Complete markdown answer with integrated code and visualizations",
          "chatsummary": "Summary text",
          "whatsapp_summary": "WhatsApp-friendly summary"
        }
      }
    }
  ],
  "created_at": "2025-07-03T20:30:00.000Z",
  "updated_at": "2025-07-03T20:30:05.000Z",
  "total_tokens": 3456,
  "total_cost": 0.0345
}
```

## Specialized Features

### PineScript Code Generation
- **Knowledge Base**: Comprehensive PineScript v5 patterns and functions
- **Validation**: Syntax checking and best practices enforcement
- **Risk Management**: Automatic inclusion of stop-loss and position sizing
- **Version Compliance**: Ensures //@version=5 compatibility

### React Visualization Generation
- **shadcn/ui Components**: Cards, badges, alerts for strategy presentation
- **ApexCharts Integration**: Candlestick charts, indicators, annotations
- **Tailwind CSS**: Core utility classes for styling
- **Self-contained**: Components are ready-to-use without external dependencies

### Conversation Context
- **Stateless Design**: No persistent memory storage
- **Summary Generation**: Automatic conversation summaries for context
- **Context Passing**: Previous summary included in subsequent requests

## Development Patterns

### LangGraph Agent Pattern
The service uses LangGraph's modern agent architecture:
1. **Main Agent**: Uses `create_react_agent` for tool orchestration
2. **Tool Calling**: Explicit tool usage for PineScript generation
3. **Message Format**: Internally converts API format to LangGraph messages
4. **Response Building**: Parses tool outputs and formats to expected JSON structure

### Token Usage Tracking
- **Callback Handler**: `UsageMetadataCallbackHandler` captures all token usage
- **Cost Calculation**: Based on Azure OpenAI pricing ($0.005/1K input, $0.015/1K output)
- **Aggregation**: Sums tokens across all model calls in the agent execution

### Response Processing Pipeline
1. **Input Validation**: Pydantic models ensure proper request format
2. **Agent Execution**: LangChain agent with tool calling
3. **JSON Processing**: Handles both structured and unstructured LLM responses
4. **Markdown Formatting**: Converts responses to structured markdown
5. **Visualization Processing**: Converts component objects to markdown syntax

### Error Handling
- **JSON Fallback**: Creates valid JSON structure if LLM returns malformed JSON
- **Null Handling**: Sets code/visualizations to null when not applicable
- **Escape Sequence Processing**: Properly handles newlines and formatting in markdown

## Important Notes

- **STATELESS SERVICE**: Each request is independent with no memory between calls
- **Context via API**: Previous conversation context passed through `previous_summary` field in request
- **No Buffer Memory**: No LangChain memory modules or persistent agent state
- **Storage ≠ State**: File storage is for conversation history, NOT for maintaining state between requests
- **Azure OpenAI Dependency**: Service requires valid Azure OpenAI credentials with tool calling support
- **Python 3.13+**: Uses latest Python features and type hints
- **Integrated Response**: All content (explanation, code, visualizations) now in single `answer` field
- **WhatsApp Summary**: New `whatsapp_summary` field provides mobile-friendly conversation preview
- **Markdown Everything**: All text fields use markdown formatting for rich UI rendering
- **Code Blocks**: Specific language tags for PineScript (`pinescript`), React (`jsx`), and charts (`chart`)
- **LangGraph Migration**: See `LANGGRAPH_MIGRATION.md` for detailed migration documentation
- **API Compatibility**: External API unchanged despite internal LangGraph migration
- **Token Usage**: Now properly tracks usage (~3,400 tokens, ~$0.03 per complex query)

## Recent Updates (July 2025)

### LangGraph Migration
- Migrated from legacy AgentExecutor to LangGraph 0.5.1
- Fixed token tracking (was returning 0, now returns actual usage)
- Improved tool calling reliability
- Maintained 100% API compatibility
- Added comprehensive migration documentation

### UUID-Based Storage Implementation
- Added FileMemoryStore for conversation persistence
- Automatic storage of ALL conversations (no optional flag)
- Thread management endpoints for CRUD operations
- Context building from stored conversation summaries
- Preserves stateless architecture - storage is NOT state

### Response Format Simplification (July 10, 2025)
- Removed `code` and `visualizations` fields from response
- All content now integrated into single `answer` field with proper markdown sections
- Added `whatsapp_summary` field for mobile-friendly conversation previews
- WhatsApp summaries show actual content instead of generic placeholders
- Maintains full backward compatibility for content structure

### Performance Metrics
- **Average Token Usage**: ~3,400 tokens for complex strategies
- **Average Cost**: ~$0.03 per query (Azure OpenAI GPT-4o)
- **Response Time**: Similar to previous AgentExecutor implementation
- **Tool Calling Success**: Improved reliability with proper prompt engineering

This microservice is designed for high-throughput trading strategy consultation with automated code generation and visualization capabilities, now with conversation storage for history tracking.