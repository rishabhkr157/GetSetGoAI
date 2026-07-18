# 🧠 Technical Architecture: How GetSetGoAI Thinks

GetSetGoAI is not just a chatbot; it is a **Stateful Agentic System** built on top of **LangGraph**. Unlike traditional LLM applications that follow a linear "Input -> Process -> Output" flow, GetSetGoAI uses a **Directed Cyclic Graph (DCG)** to reason, act, and refine its plans.

---

## 🏗️ 1. The Core Reasoning Loop (LangGraph)

The "Brain" of the system resides in `Agent/agentic_workflow.py`. The architecture follows the **ReAct (Reason + Act)** pattern:

1.  **Agent Node**: The LLM receives the user query and the current state (conversation history). It decides whether it has enough information to answer or if it needs to use a tool.
2.  **Conditional Edge**: The system checks the LLM's output. 
    - If the LLM generated a "Tool Call," the graph transitions to the **Tools Node**.
    - If the LLM generates a final response, the graph transitions to **END**.
3.  **Tool Node**: The system executes the requested Python functions (Weather, Search, Currency, etc.) and returns the raw data to the state.
4.  **Cycle**: The graph loops back to the **Agent Node**. The LLM now sees the tool results and uses them to formulate either the final answer or another tool call.

---

## 🛠️ 2. Tool Integration & Orchestration

The agent has access to a specialized suite of tools, each designed to handle a specific domain:

-   **Research**: `TavilyResearch` and `LocationInfoTool` (SerpAPI fallback) for finding attractions and hotels.
-   **Environment**: `WeatherInfoTool` for real-time climate data.
-   **Financials**: `CurrencyConverterTool` and `ArithematicOperationsTool` for budget calculations.
-   **Computation**: `CalculatorTool` for specialized expense tracking.

### **Reliable Tool Calling**
We use `parallel_tool_calls=False` when binding tools to the LLM (especially for Llama-based models like Groq). This forces the agent to reason about each tool call sequentially, significantly reducing "hallucinations" and malformed JSON errors.

### **Tool-Call Validation Guard & Workflow Sequence**
To ensure the LLM does not rely on its outdated internal training data, the prompt specifies a mandatory 6-step sequence (Weather -> Attractions -> Hotels -> Restaurants -> Budget -> Respond). 
Additionally, we implement a **Tool-Call Validation Guard** in `Agent/agentic_workflow.py`. If the model attempts to skip tool calls and write a final answer on its first turn, the guard intercepts the flow, injects a nudge instruction reminding the model of its mandatory tools, and re-invokes the LLM to guarantee proper real-time data collection.

---

## 🛡️ 3. State Management & Resilience

### **Stateless Memory (FastAPI + Checkpointers)**
The backend is built with **FastAPI**, but conversation state is preserved using LangGraph's **MemorySaver**. This allows the server to handle multiple users simultaneously without mixing up their trip plans.

### **Self-Cleaning History**
To prevent the LLM from getting confused by its own previous technical output (like raw tool tags), we implemented a **History Sanitization Layer**. Before every LLM call, the system:
1.  Reviews the message history.
2.  Removes or reformats internal markers that could lead to "copycat" errors.
3.  Truncates older messages to maintain a highly relevant context window.

---

## 🌐 4. Production-Grade Networking

The system is split into two microservices:
1.  **Backend (FastAPI)**: Responsible for the graph execution and tool orchestration.
2.  **Frontend (Streamlit)**: Provides a modern, responsive UI and handles user-provided API keys (BYOK).

Communication between services is optimized for Render's infrastructure, using automated health checks and public DNS resolution to ensure 100% uptime with automatic "server wake-up" logic.

---

## 🔍 5. Execution Tracing & Diagnostics

To make the agent's operations transparent and facilitate debugging, the system features robust observability layers:

1.  **Execution Trace Extraction (`evaluation/tracer.py`)**: After the graph completes its run, the backend parses the transaction history. It tracks token usage metrics (prompt/input tokens and completion/output tokens) from the model's metadata.
2.  **API Key Attribution**: The tracer dynamically checks the source of the API keys used for both the LLM and the individual tool executions. It distinguishes between the default environment keys (`Host Key (.env)`) and keys supplied by the user (`User Key (BYOK)`).
3.  **Step-by-Step Timeline**: The trace details every tool execution, mapping the exact inputs, outputs, and status.
4.  **UI Visualization**: The Streamlit interface displays this trace inside a dedicated, collapsible **Technical Execution Trace** expander below each response, offering real-time performance metrics and deep diagnostics.
5.  **Enterprise Observability (LangSmith)**: Built-in support for LangSmith. By setting the environment variables `LANGCHAIN_TRACING_V2=true` and your `LANGCHAIN_API_KEY`, the agent automatically routes full traces, latency reports, and internal prompt nodes to your LangSmith project dashboard for diagnostic tracking and evaluation datasets.
