# Finance Trading Assistant API

A sophisticated LangServe API that provides AI-powered trading strategy consultation, automated PineScript code generation, and interactive React visualizations. Built with FastAPI and powered by Azure OpenAI.

## 🚀 Features

- **AI Trading Consultant**: Get expert advice on trading strategies with comprehensive explanations
- **PineScript Code Generation**: Automatically generate PineScript v5 code for your trading strategies
- **Interactive Visualizations**: Generate React components with shadcn/ui and ApexCharts for strategy visualization
- **Conversation Context**: Maintains conversation summaries for contextual responses
- **RESTful API**: Easy-to-use endpoints with automatic documentation
- **Risk Management**: Built-in risk management considerations in all strategies
- **Educational Focus**: Detailed explanations of market conditions, indicators, and best practices

## 📋 Prerequisites

- Python 3.8+
- Azure OpenAI API access
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd astryx-ai-microservice-develop
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

## 🚦 Running the Application

1. **Start the server**
   ```bash
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8503 --reload
   ```

   Or with default settings:
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the API**
   - API Documentation: http://localhost:8503/docs
   - Interactive Playground: http://localhost:8503/chat/playground
   - Health Check: http://localhost:8503/health

## 📡 API Endpoints

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and examples |
| `/health` | GET | Health check status |
| `/chat/invoke` | POST | Process trading strategy queries |
| `/chat/stream` | POST | Stream responses (for real-time output) |
| `/chat/batch` | POST | Process multiple queries |
| `/chat/playground` | GET | Interactive testing interface |

### Request/Response Format

**Request Structure:**
```json
{
  "input": {
    "query": "Your trading strategy question",
    "previous_summary": "Optional: Summary of previous conversation"
  }
}
```

**Response Structure:**
```json
{
  "output": {
    "answer": "Comprehensive strategy explanation and analysis",
    "code": "Generated PineScript code (if applicable)",
    "visualizations": {
      "shadcn_component": "React component code using shadcn/ui",
      "apex_chart_config": "ApexCharts configuration object"
    },
    "chatsummary": "Summary of current conversation"
  },
  "metadata": {
    "run_id": "unique-execution-id",
    "feedback_tokens": []
  }
}
```

## 📚 Usage Examples

### 1. Basic Strategy Request with Visualization
```bash
curl -X POST http://localhost:8503/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "query": "Create a simple RSI strategy with visual representation"
    }
  }'
```

### 2. Contextual Follow-up
```bash
curl -X POST http://localhost:8503/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "query": "Add volume confirmation to this strategy",
      "previous_summary": "User created RSI strategy with oversold/overbought levels"
    }
  }'
```

### 3. Complex Strategy Request
```bash
curl -X POST http://localhost:8503/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "query": "Build a multi-timeframe strategy using RSI divergence and MACD confirmation with visual charts"
    }
  }'
```

### 4. Pretty-printed Response (with jq)
```bash
curl -X POST http://localhost:8503/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "query": "Create a Bollinger Bands squeeze strategy with charts"
    }
  }' | jq .output
```

## 🎨 Visualization Components

The API now generates interactive visualizations using:

### shadcn/ui Components
- Card layouts for strategy information
- Badges for signal indicators
- Alerts for risk warnings
- Clean, modern UI components

### ApexCharts Integration
- Candlestick charts for price action
- Line charts for indicators (RSI, MACD, etc.)
- Annotations for key levels
- Interactive tooltips and zoom

### Example Visualization Response
```javascript
{
  "visualizations": {
    "shadcn_component": "import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'...",
    "apex_chart_config": {
      "chart": { "type": "line", "height": 350 },
      "series": [{ "name": "RSI", "data": [30, 45, 60, 35, 25] }],
      "annotations": { "yaxis": [{ "y": 30, "label": { "text": "Oversold" }}]}
    }
  }
}
```

## 🏗️ Project Structure

```
astryx-ai-microservice-develop/
├── main.py                    # FastAPI application and endpoints
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project configuration
├── .env                      # Environment variables (create this)
└── llm_agent/
    ├── agent_multi.py        # Main agent logic
    ├── prompts_multi.py      # System prompts
    ├── tools_multi.py        # PineScript & visualization generation
    └── pinescript_knowledge.txt  # PineScript v5 knowledge base
```

## 🎯 Common Use Cases

### 1. Strategy Development with Visuals
- Moving Average strategies with crossover charts
- Momentum strategies with indicator visualizations
- Volatility strategies with band displays
- Pattern recognition with highlighted signals

### 2. Risk Management Dashboards
- Stop-loss and take-profit visualization
- Position sizing calculators
- Risk-reward ratio displays
- Drawdown charts

### 3. Educational Visualizations
- Interactive indicator explanations
- Strategy component breakdowns
- Signal generation demonstrations

## 🔧 Configuration

### Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | `sk-...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | `https://myresource.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name | `gpt-4` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-02-15-preview` |

### LLM Settings
- Temperature: 0 (for consistent outputs)
- Response format: JSON object
- Max iterations: 3 (for agent execution)
- Visualization components: shadcn/ui + ApexCharts

## 📝 Development Tips

1. **Testing Strategies**
   - Always test generated PineScript code in TradingView's Pine Editor
   - Verify React components render correctly
   - Test ApexCharts configurations with sample data

2. **API Usage**
   - Use the `/chat/playground` endpoint for interactive testing
   - Request "with visual representation" for charts
   - Include `previous_summary` for multi-turn conversations

3. **Visualization Best Practices**
   - Components are self-contained and ready to use
   - ApexCharts configs can be directly passed to ReactApexChart
   - All styling uses Tailwind CSS core classes

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the server is running on the correct port
   - Use `python3 -m uvicorn` if `uvicorn` command fails

2. **Import Errors**
   - Make sure virtual environment is activated
   - Install all dependencies: `pip install -r requirements.txt`

3. **No Visualizations Generated**
   - Include "visual", "chart", or "visualization" in your query
   - Ensure strategy involves indicators or patterns

4. **JSON Parse Errors**
   - Response always returns valid JSON
   - Check for network issues if response is truncated

### Debug Mode
Run with debug logging:
```bash
python3 -m uvicorn main:app --reload --log-level debug
```

## 📈 Example Outputs

### 1. RSI Strategy with Visualization
Returns:
- PineScript code for RSI strategy
- React component showing RSI levels
- ApexCharts config with oversold/overbought annotations

### 2. Moving Average Crossover
Returns:
- PineScript code for MA crossover
- React component with strategy explanation cards
- Line chart showing MA lines and crossover points

### 3. Bollinger Bands Squeeze
Returns:
- PineScript code for BB squeeze detection
- React component with squeeze indicators
- Chart showing bands and price action

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) and [LangServe](https://github.com/langchain-ai/langserve)
- Powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- UI components by [shadcn/ui](https://ui.shadcn.com/)
- Charts by [ApexCharts](https://apexcharts.com/)
- PineScript strategies for [TradingView](https://www.tradingview.com/)

## ⚠️ Disclaimer

This API provides educational content about trading strategies. Always do your own research and consider consulting with financial professionals before making trading decisions. Past performance does not guarantee future results.