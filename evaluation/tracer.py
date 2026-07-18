from langchain_core.messages import AIMessage, ToolMessage
from typing import Dict, Any, List

def extract_execution_trace(graph_output: Dict[str, Any], query_payload: Dict[str, Any], active_provider: str) -> Dict[str, Any]:
    """
    Parses the LangGraph run output to extract token usage, 
    tool calls with their inputs/outputs, and API key sources.
    """
    # 1. Determine LLM and key source
    llm_key_mapping = {
        "google": "google_api_key",
        "groq": "groq_api_key",
        "deepseek": "deepseek_api_key",
        "mistral": "mistral_api_key"
    }
    
    user_key_field = llm_key_mapping.get(active_provider)
    llm_key_source = "Host Key (.env)"
    if user_key_field and query_payload.get(user_key_field):
        llm_key_source = "User Key (BYOK)"
        
    model_info = {
        "provider": active_provider,
        "key_source": llm_key_source
    }
    
    # 2. Track token usage
    input_tokens = 0
    output_tokens = 0
    
    # 3. Track tool calls & map them to outputs
    tool_calls_map = {}
    tool_trace = []
    
    messages = graph_output.get("messages", [])
    
    for msg in messages:
        # Check if message is an AIMessage (LLM generated)
        if isinstance(msg, AIMessage) or msg.__class__.__name__ == "AIMessage":
            # Token counting
            if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                input_tokens += msg.usage_metadata.get("input_tokens", 0) or 0
                output_tokens += msg.usage_metadata.get("output_tokens", 0) or 0
            elif hasattr(msg, "response_metadata") and msg.response_metadata:
                token_usage = msg.response_metadata.get("token_usage", {})
                if isinstance(token_usage, dict):
                    input_tokens += token_usage.get("prompt_tokens", 0) or token_usage.get("input_tokens", 0) or 0
                    output_tokens += token_usage.get("completion_tokens", 0) or token_usage.get("output_tokens", 0) or 0
            
            # Extract tool calls
            tool_calls = getattr(msg, "tool_calls", [])
            for tc in tool_calls:
                tc_id = tc.get("id")
                tc_name = tc.get("name")
                tc_args = tc.get("args")
                
                # Determine tool key source
                tool_key_source = "Host Key (.env)"
                if tc_name in ["search_attractions", "search_restaurants", "search_hotels"]:
                    if query_payload.get("tavily_api_key") or query_payload.get("serp_api_key"):
                        tool_key_source = "User Key (BYOK)"
                elif tc_name in ["get_current_weather", "get_weather_forecast"]:
                    if query_payload.get("weather_api_key"):
                        tool_key_source = "User Key (BYOK)"
                elif tc_name in ["convert_currency", "get_exchange_rate"]:
                    if query_payload.get("exchange_api_key"):
                        tool_key_source = "User Key (BYOK)"
                
                trace_entry = {
                    "id": tc_id,
                    "name": tc_name,
                    "args": tc_args,
                    "output": "No output returned or tool execution failed.",
                    "key_source": tool_key_source
                }
                tool_calls_map[tc_id] = trace_entry
                tool_trace.append(trace_entry)
                
        # Check if message is a ToolMessage (tool response)
        elif isinstance(msg, ToolMessage) or msg.__class__.__name__ == "ToolMessage":
            tc_id = getattr(msg, "tool_call_id", None)
            if tc_id in tool_calls_map:
                content = getattr(msg, "content", "")
                tool_calls_map[tc_id]["output"] = str(content)
                
    # Clean internal IDs from final trace response
    cleaned_tool_trace = []
    for item in tool_trace:
        cleaned_tool_trace.append({
            "name": item["name"],
            "args": item["args"],
            "output": item["output"],
            "key_source": item["key_source"]
        })
        
    return {
        "model_info": model_info,
        "token_usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        },
        "tool_calls": cleaned_tool_trace
    }
