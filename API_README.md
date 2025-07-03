# Astryx AI Microservice API Documentation

## Overview

The Astryx AI Microservice is a LangGraph-powered FastAPI service that provides trading strategy consultation with PineScript code generation. It features conversation persistence, thread management, and real-time token usage tracking.

**Base URL**: `http://localhost:8000`

## Authentication

**ALL endpoints use the `x-user-uuid` header for authentication**. This provides a consistent authentication mechanism across the entire API.

## Quick Start

### 1. Start the Service

```bash
# Activate virtual environment
source venv/bin/activate

# Start the service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "type": "LangServe API",
  "features": [
    "LangGraph-powered agent execution",
    "Token usage tracking and cost calculation",
    "PineScript code generation",
    "Trading strategy consultation",
    "React component visualizations",
    "ApexCharts integration",
    "Conversation summaries",
    "Markdown formatted responses"
  ]
}
```


## API Endpoints

### 1. Thread Management

#### Create New Thread
```bash
curl -X POST http://localhost:8000/threads/new \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: your-user-uuid" \
  -d '{}'
```

**Response:**
```json
{
  "conversation_id": "a45154af-859c-428b-8cb4-a743d70b05ef",
  "thread_name": "Chat - 2025-07-03 21:34"
}
```

#### List All Threads
```bash
curl -X GET http://localhost:8000/threads/list \
  -H "x-user-uuid: your-user-uuid"
```

**Response:**
```json
{
  "conversations": [
    {
      "conversation_id": "a45154af-859c-428b-8cb4-a743d70b05ef",
      "thread_name": "Chat - Create a simple moving average...",
      "created_at": "2025-07-03T16:04:42.669823",
      "updated_at": "2025-07-03T16:04:48.352867",
      "message_count": 2,
      "total_tokens": 1234,
      "total_cost": 0.01234
    }
  ]
}
```

#### Get Specific Thread
```bash
curl -X GET http://localhost:8000/threads/{conversation_id} \
  -H "x-user-uuid: your-user-uuid"
```

**Response:**
```json
{
  "conversation_id": "a45154af-859c-428b-8cb4-a743d70b05ef",
  "user_uuid": "your-user-uuid",
  "thread_name": "Chat - Create a simple moving average...",
  "messages": [
    {
      "role": "user",
      "content": "Create a simple moving average crossover strategy",
      "timestamp": "2025-07-03T16:04:48.348893"
    },
    {
      "role": "assistant",
      "content": "The moving average crossover strategy is one of...",
      "timestamp": "2025-07-03T16:04:48.352857",
      "metadata": {
        "tokens": 1234,
        "cost": 0.01234,
        "full_response": {
          "answer": "Full markdown response...",
          "code": "```pinescript\n//@version=5\n...```",
          "visualizations": {
            "shadcn": "React component code...",
            "apexcharts": "Chart configuration..."
          },
          "chatsummary": "User requested moving average strategy..."
        }
      }
    }
  ],
  "created_at": "2025-07-03T16:04:42.669823",
  "updated_at": "2025-07-03T16:04:48.352867",
  "total_tokens": 1234,
  "total_cost": 0.01234
}
```

#### Rename Thread
```bash
curl -X PUT http://localhost:8000/threads/{conversation_id}/rename \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: your-user-uuid" \
  -d '{"new_name": "MA Crossover Strategy Discussion"}'
```

**Response:**
```json
{
  "success": true,
  "new_name": "MA Crossover Strategy Discussion"
}
```

#### Delete Thread
```bash
curl -X DELETE http://localhost:8000/threads/{conversation_id} \
  -H "x-user-uuid: your-user-uuid"
```

**Response:**
```json
{
  "success": true
}
```

### 2. Chat Operations

#### Send Chat Message

**Option 1: Auto-create new conversation (no conversation_id)**
```bash
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: your-user-uuid" \
  -d '{
    "query": "Create a simple RSI strategy for day trading"
  }'
```
This automatically creates a new conversation and returns the `conversation_id` in the response.

**Option 2: Continue existing conversation (with conversation_id)**
```bash
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: your-user-uuid" \
  -d '{
    "query": "Create a simple RSI strategy for day trading",
    "conversation_id": "existing-conversation-id"
  }'
```

**Important Notes:**
- `x-user-uuid` MUST be in the request header
- If `conversation_id` is omitted, a new conversation is created automatically
- All conversations are ALWAYS stored (no option to disable)

**Response Structure:**
```json
{
  "output": {
    "answer": "# RSI Trading Strategy\n\n## Overview\nThe RSI strategy...",
    "code": "```pinescript\n//@version=5\nstrategy('RSI Strategy', overlay=true)\n...```",
    "visualizations": {
      "shadcn": ":::dual\n```jsx\nimport { Card } from '@/components/ui/card';\n...```\n:::",
      "apexcharts": "```chart\n{\"type\": \"candlestick\", \"data\": {...}}\n```"
    },
    "chatsummary": "User requested RSI strategy. Provided implementation with entry/exit rules.",
    "conversation_id": "a45154af-859c-428b-8cb4-a743d70b05ef",
    "tokens_used": 3456,
    "cost": 0.0345
  },
  "metadata": {
    "run_id": "execution-uuid",
    "feedback_tokens": []
  }
}
```

#### Streaming Chat
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: your-user-uuid" \
  -d '{
    "query": "Explain MACD indicator"
  }'
```

The response will be streamed as Server-Sent Events.

## Complete End-to-End Workflow Examples

### Workflow 1: Manual Thread Creation (Two-step process)

#### Step 1: User Login
Frontend authenticates user and obtains their UUID: `user-12345`

#### Step 2: Create Thread First
```bash
# Create new thread
curl -X POST http://localhost:8000/threads/new \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: user-12345" \
  -d '{}'
```
Response: `{"conversation_id": "conv-abc-123", "thread_name": "Chat - 2025-07-03 21:44"}`

#### Step 3: Send Messages to Thread
```bash
# Send message to the created thread
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: user-12345" \
  -d '{
    "query": "Create a simple RSI strategy",
    "conversation_id": "conv-abc-123"
  }'
```

### Workflow 2: Auto-create Thread (One-step process)

#### Step 1: User Login
Frontend authenticates user and obtains their UUID: `user-12345`

#### Step 2: Send Message (Thread auto-created)
```bash
# Send message WITHOUT conversation_id - thread is created automatically
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: user-12345" \
  -d '{
    "query": "Create a simple RSI strategy"
  }'
```
Response includes the newly created `conversation_id` which you use for follow-up messages.

### Common Workflow Pattern

#### Step 1: List Existing Conversations
```bash
curl -X GET http://localhost:8000/threads/list \
  -H "x-user-uuid: user-12345"
```

#### Step 2: Either create new or use existing
- If empty → Use auto-create (Option 1 above)
- If has conversations → Use existing conversation_id

#### Step 3: Continue Conversation
```bash
# Ask for RSI strategy
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: user-12345" \
  -d '{
    "query": "Create a simple RSI strategy for day trading with entry and exit signals",
    "conversation_id": "conv-abc-123"
  }'
```

Response includes explanation without code.

### Step 5: Continue Conversation
```bash
# Request PineScript code
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: user-12345" \
  -d '{
    "query": "Yes, please generate the PineScript code for this RSI strategy",
    "conversation_id": "conv-abc-123"
  }'
```

Response now includes:
- Detailed explanation (`answer`)
- PineScript code (`code`)
- React visualization (`visualizations.shadcn`)
- Chart configuration (`visualizations.apexcharts`)
- Token usage and cost

### Step 6: Rename Conversation
```bash
# Give it a meaningful name
curl -X PUT http://localhost:8000/threads/conv-abc-123/rename \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: user-12345" \
  -d '{"new_name": "RSI Day Trading Strategy"}'
```

### Step 7: Load Conversation Later
```bash
# Get full conversation history
curl -X GET http://localhost:8000/threads/conv-abc-123 \
  -H "x-user-uuid: user-12345"
```

## Response Field Details

### Main Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Markdown-formatted explanation of the strategy |
| `code` | string/null | PineScript code wrapped in markdown code blocks |
| `visualizations` | object | Always contains `shadcn` and `apexcharts` keys |
| `visualizations.shadcn` | string/null | React component using shadcn/ui |
| `visualizations.apexcharts` | string/null | ApexCharts configuration |
| `chatsummary` | string | Brief summary of the conversation |
| `conversation_id` | string | UUID of the conversation |
| `tokens_used` | integer | Total tokens used in this request |
| `cost` | float | Estimated cost in USD |

### Visualization Formats

**shadcn Component Example:**
```jsx
:::dual
```jsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function RSIStrategy() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>RSI Trading Strategy</CardTitle>
      </CardHeader>
      <CardContent>
        <Badge>Timeframe: 15-minute</Badge>
      </CardContent>
    </Card>
  );
}
```
:::
```

**ApexCharts Configuration Example:**
```json
```chart
{
  "chart": {
    "type": "candlestick",
    "height": 350
  },
  "series": [{
    "data": [
      {"x": "2023-10-01", "y": [100, 105, 95, 102]}
    ]
  }],
  "annotations": {
    "yaxis": [
      {"y": 30, "borderColor": "#00E396", "label": {"text": "RSI Oversold"}}
    ]
  }
}
```
```

## Error Handling

### Common Errors

1. **Conversation Not Found (500)**
   - Occurs when using a conversation_id that doesn't exist for the user
   - Solution: Create a new conversation or use an existing one

2. **Missing x-user-uuid header (422)**
   - Occurs when the x-user-uuid header is not provided
   - Solution: Always include x-user-uuid in the request headers

3. **Invalid JSON (422)**
   - Malformed request body
   - Solution: Ensure proper JSON formatting

### Error Response Format
```json
{
  "detail": "Error message describing the issue"
}
```

## Token Usage and Costs

- **Token Tracking**: Every response includes actual token usage
- **Cost Calculation**: Based on Azure OpenAI GPT-4o pricing
  - Input: $0.005 per 1K tokens
  - Output: $0.015 per 1K tokens
- **Average Usage**: ~3,400 tokens per complex strategy request
- **Average Cost**: ~$0.03 per query

## Important Implementation Notes

1. **Stateless Service**: No memory between requests - context passed via API
2. **Mandatory Storage**: ALL conversations are automatically stored
3. **Consistent Authentication**: ALL endpoints use `x-user-uuid` header
4. **LangGraph Backend**: Uses LangGraph 0.5.1 for agent orchestration
5. **Azure OpenAI**: Requires valid Azure OpenAI credentials

## Testing with cURL

### Complete Test Sequence
```bash
# Set your user UUID
USER_UUID="test-user-$(date +%s)"

# 1. Create new thread
RESPONSE=$(curl -s -X POST http://localhost:8000/threads/new \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: $USER_UUID" \
  -d '{}')
echo "Thread created: $RESPONSE"
CONV_ID=$(echo $RESPONSE | grep -o '"conversation_id":"[^"]*"' | cut -d'"' -f4)

# 2. Send message
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: $USER_UUID" \
  -d "{
    \"query\": \"Create a simple RSI strategy\",
    \"conversation_id\": \"$CONV_ID\"
  }"

# 3. List conversations
curl -X GET http://localhost:8000/threads/list \
  -H "x-user-uuid: $USER_UUID"

# 4. Get specific conversation
curl -X GET http://localhost:8000/threads/$CONV_ID \
  -H "x-user-uuid: $USER_UUID"
```

## Playground


## API Documentation

Full OpenAPI documentation available at: `http://localhost:8000/docs`