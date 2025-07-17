# Astryx AI Microservice

A sophisticated FastAPI-based trading strategy consultation service powered by LangGraph and Azure OpenAI.

## Features

- **LangGraph-Powered Agent**: Modern agent architecture for intelligent trading strategy consultation
- **Real-time Web Search**: Integrated Exa search for current market data, earnings reports, and financial news
- **PineScript Code Generation**: Automated generation of TradingView PineScript v5 code
- **Interactive Visualizations**: Dual visualization support with shadcn/ui components and ApexCharts
- **Conversation Persistence**: UUID-based file storage for conversation history
- **Token & Cost Tracking**: Real-time tracking of API usage and costs
- **Stateless Architecture**: Clean separation of concerns with context passed via API

## Prerequisites

- Python 3.13+
- Azure OpenAI API access
- Virtual environment (venv)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/astryx-ai-microservice.git
cd astryx-ai-microservice
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

## Running the Service

Development mode:
```bash
uvicorn main:app --reload
```

Production-like setup:
```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

See [API_README.md](API_README.md) for comprehensive API documentation including:
- All endpoints with examples
- Authentication details
- Request/response formats
- End-to-end workflow examples

## Quick Examples

### Trading Strategy Generation
```bash
# Create a new conversation with strategy request
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: your-user-id" \
  -d '{
    "query": "Create a simple RSI strategy for day trading"
  }'
```

### Real-time Market Search
```bash
# Search for current market data and news
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: your-user-id" \
  -d '{
    "query": "What are the latest earnings results for HDFC Bank?"
  }'
```

### Sample Response

```json
{
  "output": {
    "answer": "# RSI Strategy Explanation\n\n## Overview\nThe RSI strategy uses the Relative Strength Index...\n\n## PineScript Implementation\n\n```pinescript\n//@version=5\nstrategy(\"RSI Strategy\", overlay=true)\n...\n```\n\n## Visualization Component\n\n```jsx\nimport { Card } from '@/components/ui/card';\n...\n```",
    "chatsummary": "User asked: Create RSI strategy. Provided PineScript strategy with implementation.",
    "whatsapp_summary": "*Create a PineScript RSI strategy*\n\nKey Parameters:\n• RSI Length: 14\n• Overbought Level: 70\n• Oversold Level: 30\n• Stop Loss: 2%\n\nThis strategy uses RSI to identify...\n\n_PineScript code included in full response_",
    "conversation_id": "cb47e119-ff4b-40a4-afde-9fbda876acab",
    "tokens_used": 4827,
    "cost": 0.042405
  },
  "metadata": {
    "run_id": "",
    "feedback_tokens": []
  }
}
```

### Key Changes in Response Format

1. **Removed Keys**: `code` and `visualizations` fields have been removed
2. **Integrated Content**: All content (strategy, code, visualizations) is now in the `answer` field
3. **WhatsApp Summary**: New field that provides a concise, mobile-friendly summary of the response
   - Shows the user's query
   - Lists key parameters or main points
   - Provides a brief description
   - Perfect for WhatsApp message previews

## Architecture

- **FastAPI**: Web framework
- **LangGraph 0.5.1**: Agent orchestration
- **Azure OpenAI**: LLM backend
- **File-based Storage**: Conversation persistence

## Development

For detailed development notes and architecture decisions, see:
- [CLAUDE.md](CLAUDE.md) - Project guidance and conventions
- [LANGGRAPH_MIGRATION.md](LANGGRAPH_MIGRATION.md) - Migration documentation

## License

[Your License Here]