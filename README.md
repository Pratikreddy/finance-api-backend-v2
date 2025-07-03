# Astryx AI Microservice

A sophisticated FastAPI-based trading strategy consultation service powered by LangGraph and Azure OpenAI.

## Features

- **LangGraph-Powered Agent**: Modern agent architecture for intelligent trading strategy consultation
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

## Quick Example

```bash
# Create a new conversation
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -H "x-user-uuid: your-user-id" \
  -d '{
    "query": "Create a simple RSI strategy for day trading"
  }'
```

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