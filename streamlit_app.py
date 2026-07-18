import warnings
warnings.filterwarnings("ignore", category=UserWarning, message='Field name "output_schema" in "TavilyResearch" shadows an attribute in parent "BaseTool"')
warnings.filterwarnings("ignore", category=UserWarning, message='Field name "stream" in "TavilyResearch" shadows an attribute in parent "BaseTool"')

import streamlit as st
import datetime
import requests
import os
import sys
import json

# Configuration: Default to local backend if no environment variable is set
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
if BASE_URL and not BASE_URL.startswith(("http://", "https://")):
    BASE_URL = f"https://{BASE_URL}"

# Set page configuration
st.set_page_config(
    page_title="GetSetGoAI | Premium Travel Concierge",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium look
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    /* Force sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] a {
        color: #f8fafc !important;
    }
    /* Force Alert/Info boxes to be readable */
    div[data-testid="stAlert"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stAlert"] p, div[data-testid="stAlert"] div {
        color: #f8fafc !important;
    }
    .main-header {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(to right, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        text-align: center;
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    /* Fix text color for inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        color: #f8fafc;
    }
    .stSelectbox>div>div>div {
        color: #f8fafc;
    }
    h1, h2, h3, p {
        color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown('<p class="main-header">✈️ GetSetGoAI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your Elite Agentic Travel Concierge</p>', unsafe_allow_html=True)

# Initialize session ID for persistence if not exists
if "thread_id" not in st.session_state:
    import uuid
    st.session_state["thread_id"] = str(uuid.uuid4())

# --- SIDEBAR: Information and Settings ---
with st.sidebar:
    st.header("🌟 Premier Services")
    st.write(
        "Experience the future of travel planning with our agentic intelligence."
    )
    
    # Unsplash travel image for better UI
    img_url = "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=400&q=80"
    st.image(img_url, use_container_width=True)
        
    st.markdown("---")
    st.write(f"🕒 {datetime.datetime.now().strftime('%H:%M, %d %b %Y')}")

    st.markdown("---")
    st.subheader("🔑 API Configuration")
    st.info("Enter your own keys to run the concierge under your provider account.")
    
    st.markdown('<div style="font-size: 0.85rem; margin-bottom: -15px;">'
                '<a href="https://console.groq.com/keys" target="_blank">Get Groq Key</a>'
                '</div>', unsafe_allow_html=True)
    groq_key = st.text_input("Groq API Key", type="password")

    st.markdown('<div style="font-size: 0.85rem; margin-bottom: -15px;">'
                '<a href="https://aistudio.google.com/" target="_blank">Get Google Key</a>'
                '</div>', unsafe_allow_html=True)
    google_key = st.text_input("Google AI (Gemini) Key", type="password")

    st.markdown('<div style="font-size: 0.85rem; margin-bottom: -15px;">'
                '<a href="https://www.deepseek.com/" target="_blank">Get DeepSeek Key</a>'
                '</div>', unsafe_allow_html=True)
    deepseek_key = st.text_input("DeepSeek API Key", type="password")
    
    st.markdown('<div style="font-size: 0.85rem; margin-bottom: -15px;">'
                '<a href="https://tavily.com/" target="_blank">Get Tavily Key</a>'
                '</div>', unsafe_allow_html=True)
    tavily_key = st.text_input("Tavily Search Key", type="password")
    
    st.markdown('<div style="font-size: 0.85rem; margin-bottom: -15px;">'
                '<a href="https://openweathermap.org/api" target="_blank">Get Weather Key</a>'
                '</div>', unsafe_allow_html=True)
    weather_key = st.text_input("OpenWeatherMap Key", type="password")
    
    st.markdown('<div style="font-size: 0.85rem; margin-bottom: -15px;">'
                '<a href="https://www.exchangerate-api.com/" target="_blank">Get Currency Key</a>'
                '</div>', unsafe_allow_html=True)
    exchange_key = st.text_input("ExchangeRate-API Key", type="password")
    
    st.markdown('<div style="font-size: 0.85rem; margin-bottom: -15px;">'
                '<a href="https://serpapi.com/" target="_blank">Get SerpAPI Key</a>'
                '</div>', unsafe_allow_html=True)
    serp_key = st.text_input("SerpAPI Key (Optional)", type="password")

    st.session_state["groq_key"] = groq_key
    st.session_state["google_key"] = google_key
    st.session_state["deepseek_key"] = deepseek_key
    st.session_state["tavily_key"] = tavily_key
    st.session_state["weather_key"] = weather_key
    st.session_state["exchange_key"] = exchange_key
    st.session_state["serp_key"] = serp_key

    st.markdown("---")
    st.subheader("⚙️ Preferences")
    currency = st.selectbox("Currency Display", ["USD", "INR", "EUR", "GBP"], index=0)
    st.session_state["currency"] = currency

    auto_convert = st.checkbox("Proactive Price Conversion", value=True)
    st.session_state["auto_convert"] = auto_convert

    st.markdown("---")
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        st.session_state["thread_id"] = str(uuid.uuid4())
        st.rerun()

# --- MAIN INTERFACE: Chatting with the AI ---
st.header("Chat with Your Travel Assistant")

# Initialize chat history state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history with custom avatars
for message in st.session_state.messages:
    avatar = "✈️" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        
        # Render technical execution trace if available
        if message["role"] == "assistant" and "trace" in message and message["trace"]:
            trace = message["trace"]
            with st.expander("🔍 Technical Execution Trace", expanded=False):
                # 1. Model Info
                model_info = trace.get("model_info", {})
                st.markdown(f"**LLM Provider:** `{model_info.get('provider', 'N/A')}` | **LLM Key Source:** `{model_info.get('key_source', 'N/A')}`")
                
                # 2. Token Usage
                token_usage = trace.get("token_usage", {})
                st.markdown("**Token Usage Summary:**")
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    st.metric("Prompt (Input)", f"{token_usage.get('input_tokens', 0)}")
                with col_t2:
                    st.metric("Completion (Output)", f"{token_usage.get('output_tokens', 0)}")
                with col_t3:
                    st.metric("Total Tokens", f"{token_usage.get('total_tokens', 0)}")
                
                # 3. Tool Calls
                tool_calls = trace.get("tool_calls", [])
                if tool_calls:
                    st.markdown("**Tool Execution Timeline:**")
                    for idx, tool_call in enumerate(tool_calls):
                        tool_name = tool_call.get("name", "Unknown Tool")
                        tool_args = tool_call.get("args", {})
                        tool_output = tool_call.get("output", "")
                        tool_key_src = tool_call.get("key_source", "Host Key (.env)")
                        
                        with st.container(border=True):
                            st.markdown(f"**Step {idx+1}:** Called `{tool_name}` (using `{tool_key_src}`)")
                            st.code(f"Inputs: {json.dumps(tool_args, indent=2)}", language="json")
                            st.markdown("**Output / Result:**")
                            if len(tool_output) > 500:
                                st.text(tool_output[:500] + "\n... (truncated for layout) ...")
                                with st.expander("Show Full Tool Output", expanded=False):
                                    st.text(tool_output)
                            else:
                                st.text(tool_output)
                else:
                    st.markdown("ℹ️ *No tools were called for this response.*")

# Trip parameters for contextual planning
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    num_travelers = st.number_input("Travelers", min_value=1, value=1, step=1)
with col2:
    travel_month = st.selectbox(
        "Approx. month",
        ["Any", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    )
with col3:
    allow_web = st.checkbox("Allow web lookups for live info", value=True)

# Modern Chat Input
if prompt := st.chat_input("E.g., Plan a 5-day honeymoon in the Maldives"):
    # Add user message to history and UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="✈️"):
        st.markdown(prompt)

    # Fetch Assistant Response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Our AI is planning your trip..."):
            try:
                payload = {
                    "query": prompt,
                    "num_travelers": int(num_travelers),
                    "travel_month": travel_month if travel_month != "Any" else None,
                    "allow_web": bool(allow_web),
                    "auto_convert": st.session_state.get("auto_convert", False),
                    "target_currency": st.session_state.get("currency", "USD"),
                    "thread_id": st.session_state.get("thread_id", "default"),
                    # Pass user-provided keys
                    "google_api_key": st.session_state.get("google_key"),
                    "groq_api_key": st.session_state.get("groq_key"),
                    "deepseek_api_key": st.session_state.get("deepseek_key"),
                    "tavily_api_key": st.session_state.get("tavily_key"),
                    "weather_api_key": st.session_state.get("weather_key"),
                    "exchange_api_key": st.session_state.get("exchange_key"),
                    "serp_api_key": st.session_state.get("serp_key")
                }
                
                response = requests.post(f"{BASE_URL}/query", json=payload, timeout=180)
                
                if response.status_code == 402:
                    st.error("💳 Agentic credits exceeded. Please top up your provider account.")
                else:
                    response.raise_for_status()
                    resp_json = response.json()
                    answer = resp_json.get("answer", "I prepared a plan for you, but could not retrieve the text.")
                    trace = resp_json.get("trace", {})
                    st.markdown(answer)
                    
                    # Render trace for the live response
                    if trace:
                        with st.expander("🔍 Technical Execution Trace", expanded=False):
                            model_info = trace.get("model_info", {})
                            st.markdown(f"**LLM Provider:** `{model_info.get('provider', 'N/A')}` | **LLM Key Source:** `{model_info.get('key_source', 'N/A')}`")
                            
                            token_usage = trace.get("token_usage", {})
                            st.markdown("**Token Usage Summary:**")
                            col_t1, col_t2, col_t3 = st.columns(3)
                            with col_t1:
                                st.metric("Prompt (Input)", f"{token_usage.get('input_tokens', 0)}")
                            with col_t2:
                                st.metric("Completion (Output)", f"{token_usage.get('output_tokens', 0)}")
                            with col_t3:
                                st.metric("Total Tokens", f"{token_usage.get('total_tokens', 0)}")
                            
                            tool_calls = trace.get("tool_calls", [])
                            if tool_calls:
                                st.markdown("**Tool Execution Timeline:**")
                                for idx, tool_call in enumerate(tool_calls):
                                    tool_name = tool_call.get("name", "Unknown Tool")
                                    tool_args = tool_call.get("args", {})
                                    tool_output = tool_call.get("output", "")
                                    tool_key_src = tool_call.get("key_source", "Host Key (.env)")
                                    
                                    with st.container(border=True):
                                        st.markdown(f"**Step {idx+1}:** Called `{tool_name}` (using `{tool_key_src}`)")
                                        st.code(f"Inputs: {json.dumps(tool_args, indent=2)}", language="json")
                                        st.markdown("**Output / Result:**")
                                        if len(tool_output) > 500:
                                            st.text(tool_output[:500] + "\n... (truncated for layout) ...")
                                            with st.expander("Show Full Tool Output", expanded=False):
                                                st.text(tool_output)
                                        else:
                                            st.text(tool_output)
                            else:
                                st.markdown("ℹ️ *No tools were called for this response.*")
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer, "trace": trace})

            except Exception as e:
                st.error(f"Failed to reach the travel assistant: {str(e)}")

# --- EXPORT: Chat-to-PDF Functionality ---
if st.session_state.get("messages"):
    with st.sidebar:
        st.markdown("---")
        st.subheader("Export Itinerary")
        if st.button("Export current results to PDF"):
            # Convert history to a single markdown string
            md_lines = [f"**{m['role'].title()}**:\n\n{m['content']}\n\n" for m in st.session_state.messages]
            payload = {"content": "\n\n".join(md_lines), "title": "GetSetGoAI Travel Plan"}
            try:
                r = requests.post(f"{BASE_URL}/export_pdf", json=payload, timeout=60)
                if r.status_code == 200:
                    st.download_button("Download PDF", data=r.content, file_name="travel_plan.pdf", mime="application/pdf")
                else:
                    st.error("PDF export failed. Check backend logs.")
            except Exception as e:
                st.error(f"Request failed: {e}")

# Footer attribution in sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>
            Developed by <b>Rishabh Kumar</b><br>
            © 2026 GetSetGoAI Project
        </div>
        """,
        unsafe_allow_html=True
    )