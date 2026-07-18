from utils.model_loaders import ModelLoader
from tools.weather_info_tool import WeatherInfoTool
from tools.place_search_tool import LocationInfoTool
from tools.currency_converter_tool import CurrencyConverterTool
from tools.arithematic_operations_tool import ArithematicOperationsTool
from tools.expense_calculator_tool import CalculatorTool
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import Any, Dict, Optional, TypedDict
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from prompt_library.prompt import SYSTEM_PROMPT
import json
import re
import logging

logger = logging.getLogger(__name__)

class AgentState(MessagesState):
    structured: Optional[Dict[str, Any]]
    api_keys: Optional[Dict[str, str]]

from langchain_core.runnables import RunnableConfig

class GraphBuilder():
    def __init__(self, model_provider :str ="deepseek"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        self.tools = []
        self.weather_tools = WeatherInfoTool()
        self.currency_tools = CurrencyConverterTool()
        self.location_tools = LocationInfoTool()
        self.arithmetic_tools = ArithematicOperationsTool()
        self.expense_tools = CalculatorTool()
        
        self.tools.extend([
            *self.weather_tools.weather_tools_list,
            *self.location_tools.place_search_tools_list,
            *self.arithmetic_tools.calculater_tools_list,
            *self.currency_tools.currency_tools_list,
            *self.expense_tools.calculator_tool_list
        ])
        
        # Using parallel_tool_calls=False for higher reliability with Groq/Llama
        if self.llm:
            self.llm_with_tools = self.llm.bind_tools(self.tools, parallel_tool_calls=False)
        else:
            self.llm_with_tools = None
            logger.warning("GraphBuilder initialized without a default LLM. Requests must provide their own API keys.")
        self.system_prompt = SYSTEM_PROMPT

    async def agent_function(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Processes the current state, invokes the LLM with tools, 
        and extracts any structured JSON payload.
        """
        input_messages = state.get('messages', [])
        
        # --- HISTORY SANITIZATION ---
        # Filter out any message containing hallucinated tags to prevent 'copycat' errors
        messages = [self.system_prompt]
        for msg in input_messages:
            content = getattr(msg, 'content', "")
            if isinstance(content, str):
                if "<function" in content or "tool_use_failed" in content or "failed_generation" in content:
                    logger.info("Sanitizing history: removing message with suspected malformed content")
                    continue
            messages.append(msg)

        try:
            # BYOK: Check for custom LLM keys
            api_keys = config.get("configurable", {}).get("api_keys", {})
            google_key = api_keys.get("google_api_key")
            groq_key = api_keys.get("groq_api_key")
            deepseek_key = api_keys.get("deepseek_api_key")
            
            # Use specific LLM if key provided, otherwise use default
            current_llm = self.llm_with_tools
            
            if not current_llm and not (google_key or groq_key or deepseek_key):
                 raise ValueError("No API key provided. Please enter your API key in the configuration sidebar.")
            
            target_key = None
            if self.model_loader.model_provider == "google" and google_key:
                target_key = google_key
                logger.info("Using user-provided Google API key for this request")
            elif self.model_loader.model_provider == "groq" and groq_key:
                target_key = groq_key
                logger.info("Using user-provided Groq API key for this request")
            elif self.model_loader.model_provider == "deepseek" and deepseek_key:
                target_key = deepseek_key
                logger.info("Using user-provided DeepSeek API key for this request")

            if target_key:
                custom_llm = self.model_loader.load_llm(api_key=target_key)
                current_llm = custom_llm.bind_tools(self.tools, parallel_tool_calls=False)

            # Invoke LLM asynchronously
            response = await current_llm.ainvoke(messages)
            
            # --- TOOL-CALL VALIDATION GUARD ---
            # If this is the first user turn and the model skipped tools,
            # nudge it to call tools before answering
            tool_calls = getattr(response, "tool_calls", [])
            if not tool_calls and len(input_messages) <= 3:
                logger.info("Tool-call guard triggered: model skipped tools on first turn, re-prompting")
                nudge_msg = HumanMessage(
                    content="You must use your tools before answering. "
                    "Start by calling search_attractions and get_weather_forecast for the destination. "
                    "Do NOT write a final answer yet — call the tools first."
                )
                messages.append(response)
                messages.append(nudge_msg)
                response = await current_llm.ainvoke(messages)
            
            # Robust content extraction
            content = getattr(response, 'content', "")
            text = str(content) if not isinstance(content, list) else " ".join([str(c) for c in content])

            # Look for JSON block
            structured = None
            try:
                json_blocks = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
                if json_blocks:
                    structured = json.loads(json_blocks[-1])
            except Exception:
                pass

            return {"messages": [response], "structured": structured} if structured else {"messages": [response]}

        except Exception as e:
            logger.exception("Agent node execution failed: %s", e)
            friendly_msg = "I encountered a technical issue while processing your request. Please try again or rephrase your query."
            if "400" in str(e) and "tool_use_failed" in str(e):
                 friendly_msg = "I had trouble using my research tools correctly. I'm resetting my approach."
            
            error_msg = AIMessage(content=friendly_msg)
            return {"messages": [error_msg]}
    
    def build_graph(self):
        memory = MemorySaver()
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        return graph_builder.compile(checkpointer=memory)
        
    def __call__(self):
        return self.build_graph()