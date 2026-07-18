# ✈️ GetSetGoAI: Your Agentic Travel Concierge

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=render)](https://getsetgo-frontend-v4-km3t.onrender.com/)

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/rishabhkr157/GetSetGoAI)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)

Experience the future of travel planning. **GetSetGoAI** is a premium, multi-agentic travel assistant that researches, plans, and budgets your perfect trip using real-time data.

![alt text](<Screenshot (795).png>)

## 🔗 Repository
Find the latest source code and contribute here: [rishabhkr157/GetSetGoAI](https://github.com/rishabhkr157/GetSetGoAI)

## 🌟 Key Features

- **Multi-Agent Orchestration**: Powered by **LangGraph**, our agent reasons through complex requests, deciding when to search for hotels, restaurants, or weather data.
- **Cost-Managed BYOK Architecture**: Supports a "Bring Your Own Key" model where visitors can provide their own API keys via the UI, ensuring zero costs for the host.
- **High-Concurrency Backbone**: A fully non-blocking I/O layer built with **FastAPI** and **httpx** for massive throughput.
- **Deep Research Integration**: Real-time web lookups via **Tavily Research** and **Google Search (SerpAPI)**.
- **Data-Driven Itineraries**: Generates two distinct plans for every request:
  - **The Classic Route**: Must-see landmarks and tourist favorites.
  - **The Off-Beat Path**: Hidden gems and local secrets.
- **Financial Intelligence**: Automatic currency conversion (INR, USD, EUR, etc.) and line-item budget breakdowns.
- **Live Logistics**: Integration with weather services and location data for precise planning.
- **Premium PDF Export**: Generate a high-quality PDF itinerary with one click.
- **Persistence**: Remembers your conversation history across sessions using a robust threading system.
- **Comprehensive Run Tracing**: Integrated execution tracer showing token counts (prompt, completion, total), LLM provider info, and step-by-step API key source attribution (BYOK vs Host).
- **Sequential Tool Calling Guard**: Mandatory tool execution validation sequence (Weather -> Attractions -> Hotels -> Restaurants -> Budget) with a fallback guard ensuring the model never answers using stale training data.
- **Enterprise-Grade Observability (LangSmith)**: Out-of-the-box integration with LangSmith. Simply toggle the standard environment variables to stream full run-graphs, prompts, and latencies for production-grade evaluation and debugging.

---

## 🚀 Quick Start

### 1. Environment Setup
We recommend using `uv` for lightning-fast dependency management:
```powershell
# Install dependencies using uv
uv pip install -e .
# Or using traditional pip
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory and add your API keys:
```env
GOOGLE_API_KEY=your_google_key
TAVILY_API_KEY=your_tavily_key
SERPAPI_API_KEY=your_serp_key
EXCHANGE_API_KEY=your_currency_key
MODEL_PROVIDER=google # or mistralai, openai, deepseek
```

### 3. Run the Application
Start the engine and the interface:
```powershell
# Terminal 1: Start FastAPI Backend
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start Streamlit Frontend
streamlit run streamlit_app.py
```

---

## 🛠️ Architecture

GetSetGoAI follows a modular, tool-centric design:

- **Brain (`Agent/agentic_workflow.py`)**: A state-driven LangGraph orchestrator that manages the "Thinking" -> "Acting" cycle.
- **Tools (`tools/`)**: Specialized, non-blocking modules for Weather, Places, Currency, and Calculations.
- **UI (`streamlit_app.py`)**: A modern, glassmorphic chat interface for high-end user experience.
- **API (`main.py`)**: A high-performance, non-blocking RESTful gateway.
- **Tracer (`evaluation/tracer.py`)**: An execution tracing and diagnostic utility that calculates token metrics and attributes API key usage dynamically.

For a deeper dive into how the agent thinks and the underlying LangGraph architecture, see the [Technical Explanation Guide](technical_explanation.md).

---

## 🧪 Development

### Adding a New Tool
1. Create a class in `tools/` following the existing pattern.
2. Register the tool in `Agent/agentic_workflow.py`.
3. Update the `SYSTEM_PROMPT` in `prompt_library/prompt.py` if specific instructions are needed.

### Running Tests
```powershell
pytest -v
```

---

## 📜 License
Developed for elite travelers. All rights reserved. 
© 2026 [Rishabh Kumar](https://github.com/rishabhkr157)
