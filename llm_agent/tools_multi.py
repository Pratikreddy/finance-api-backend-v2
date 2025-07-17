import os
import pathlib
from langchain.tools import tool
from langchain_core.tools import tool as core_tool
from dotenv import load_dotenv
from exa_py import Exa

# Load environment variables
load_dotenv()

# Initialize Exa client
exa = Exa(api_key=os.environ["EXA_API_KEY"])

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


# ──────────────────────────────────────────────────────────────────────────────
# EXA SEARCH TOOLS
# ──────────────────────────────────────────────────────────────────────────────

@tool
def exa_search(
    query: str,
    include_domains: list[str] = None,
    exclude_domains: list[str] = None,
    start_published_date: str = None,
    end_published_date: str = None,
    include_text: list[str] = None,
    exclude_text: list[str] = None,
):
    """
    Search for webpages based on the query and retrieve their contents.

    Parameters:
    - query (str): The search query.
    - include_domains (list[str], optional): Restrict the search to these domains.
    - exclude_domains (list[str], optional): Exclude these domains from the search.
    - start_published_date (str, optional): Restrict to documents published after this date (YYYY-MM-DD).
    - end_published_date (str, optional): Restrict to documents published before this date (YYYY-MM-DD).
    - include_text (list[str], optional): Only include results containing these phrases.
    - exclude_text (list[str], optional): Exclude results containing these phrases.
    """
    return exa.search_and_contents(
        query,
        use_autoprompt=True,
        num_results=5,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        start_published_date=start_published_date,
        end_published_date=end_published_date,
        include_text=include_text,
        exclude_text=exclude_text,
        text=True,
        highlights=True,
    )


@tool
def exa_find_similar(
    url: str,
    exclude_source_domain: bool = False,
    start_published_date: str = None,
    end_published_date: str = None,
):
    """
    Search for webpages similar to a given URL and retrieve their contents.
    The url passed in should be a URL returned from `exa_search`.

    Parameters:
    - url (str): The URL to find similar pages for.
    - exclude_source_domain (bool, optional): If True, exclude pages from the same domain as the source URL.
    - start_published_date (str, optional): Restrict to documents published after this date (YYYY-MM-DD).
    - end_published_date (str, optional): Restrict to documents published before this date (YYYY-MM-DD).
    """
    return exa.find_similar_and_contents(
        url,
        num_results=5,
        exclude_source_domain=exclude_source_domain,
        start_published_date=start_published_date,
        end_published_date=end_published_date,
        text=True,
        highlights={"num_sentences": 1, "highlights_per_url": 1},
    )