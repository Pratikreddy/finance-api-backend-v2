import os
import pathlib
from langchain.tools import tool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# PINESCRIPT GENERATION TOOL
# ──────────────────────────────────────────────────────────────────────────────
@tool
def generate_pinescript(strategy_description: str) -> str:
    """
    Generate PineScript code for trading strategies
    
    This tool calls a specialized PineScript agent that has deep knowledge
    of Pine Script v5 syntax, trading indicators, and strategy patterns.
    
    Args:
        strategy_description: Natural language description of the trading strategy
        
    Returns:
        JSON string containing the PineScript code and explanation
    """
    from langchain_openai import AzureChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    
    # Load PineScript knowledge file
    knowledge_path = pathlib.Path(__file__).parent / "pinescript_knowledge.txt"
    pinescript_knowledge = ""
    
    if knowledge_path.exists():
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            pinescript_knowledge = f.read()
    
    # Create specialized PineScript LLM
    pinescript_llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    
    # PineScript expert prompt with visualization support
    system_message = """You are an expert PineScript v5 developer and React visualization specialist.

PINESCRIPT KNOWLEDGE BASE:
""" + pinescript_knowledge + """

VISUALIZATION COMPONENTS AVAILABLE:
- shadcn/ui components:
  import {{ Card, CardContent, CardDescription, CardHeader, CardTitle }} from '@/components/ui/card'
  import {{ Badge }} from '@/components/ui/badge'
  import {{ Alert, AlertDescription }} from '@/components/ui/alert'
- Charts: import ReactApexChart from 'react-apexcharts'
- Styling: Use only Tailwind CSS core utility classes (no custom classes)

Your task is to:
1. Generate clean, efficient PineScript code based on the strategy description
2. Create React components to visualize the strategy using shadcn/ui
3. Include ApexCharts configuration ONLY when showing candlestick patterns, price action, or indicators

Guidelines:
1. PineScript: Use v5 syntax with proper declarations and comments
2. React Component: Create a complete, self-contained component that explains the strategy visually
3. ApexCharts: Only include if the strategy requires price/indicator visualization
4. Text: Return clean text without escape characters or formatting codes

You must ALWAYS return valid JSON with these fields:
- pinescript_code: Complete PineScript code starting with //@version=5
- explanation: Clean text explanation of the strategy (no \\n or escape sequences)
- visualizations: {{
    shadcn: Complete React component wrapped in markdown format: ":::dual\\n```jsx\\nCODE_HERE\\n```\\n:::",
    apexcharts: Chart config wrapped in markdown format: "```chart\\nJSON_CONFIG_HERE\\n```" (null if not needed)
  }}
- parameters: Array of key parameters that can be adjusted
- usage_notes: Important notes about using this script (clean text)

Never include any text before or after the JSON. The response must be valid JSON only."""
    
    pinescript_prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", "{strategy_description}")
    ])
    
    # Generate PineScript code and visualizations
    chain = pinescript_prompt | pinescript_llm
    result = chain.invoke({"strategy_description": strategy_description})
    
    return result.content