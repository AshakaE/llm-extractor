# 🧠 LLM Knowledge Extractor

A prototype system that extracts structured insights from unstructured text using AI-powered analysis, featuring intelligent mock fallbacks and a modern web interface.

## 🚀 Setup and Run Instructions

### Prerequisites

-   **Python 3.11+**
-   **Node.js 18+** with npm
-   **OpenAI API key** (optional - system works without it)

### Quick Setup

1. **Run the setup script**:

    ```bash
    ./setup.sh
    ```

2. **Add OpenAI API key** (optional):

    ```bash
    echo "OPENAI_API_KEY=sk-your-key-here" > backend/.env
    ```

3. **Start the backend**:

    ```bash
    cd backend
    source venv/bin/activate
    python main.py
    ```

4. **Start the frontend** (in a new terminal):

    ```bash
    cd frontend
    npm run dev
    ```

5. **Access the application**: http://localhost:8081

## ⚡ Design Choices

I went with FastAPI for the backend because, honestly, it just makes life easier. The automatic API documentation is a huge time-saver, and since I knew I'd be calling out to LLM APIs, the built-in async support was perfect. For the frontend, Vue.js 3 felt like the right choice - it's reactive without being overly complex, and I could build components that actually make sense.
SQLite was a no-brainer for this project. No setup headaches, no server configuration - it just works. And since this was meant to be a prototype that anyone could run immediately, simplicity won out over fancy database features.
The thing I'm most proud of is the mock LLM service. I knew not everyone would have an OpenAPI key lying around, so I built something that actually gives you useful results using NLTK and some basic sentiment analysis. It's not GPT-4, but it'll show you what the system can do.

## ⏰ Time Trade-offs

With just 90 minutes on the clock, I had to make some tough calls. The search functionality is pretty basic - just substring matching instead of proper full-text search. The database schema is intentionally simple (no fancy relationships that would eat up time). And instead of pulling in a whole UI library, I just wrote the CSS myself. Sometimes the scrappy approach is the right approach.
The mock mode was actually where I spent extra time, because I wanted people to see real value even without connecting to external APIs. It had to feel intelligent, not like a placeholder.

## 🎯 Core Features

Real text analysis - summaries, topics, sentiment, the works
Everything saves - SQLite keeps your analyses searchable
Works offline - no API key? No problem, the mock mode has you covered
Clean interface - responsive Vue.js that doesn't get in your way
Proper API - RESTful endpoints if you want to build on top of it
Handles failures gracefully - because things break, and that's okay

## 📊 API Endpoints

-   `POST /analyze` - Analyze text and extract structured data
-   `GET /search?topic=X&keyword=Y` - Search past analyses
-   `GET /analyses` - Retrieve all stored analyses
-   `GET /` - API health check

## 🛠️ Architecture

```
Backend (Python FastAPI)     Frontend (Vue.js)
├── main.py                  ├── src/App.vue
├── llm_service.py          ├── index.html
├── database.py             └── vite.config.js
└── requirements.txt
```

## 🔧 Development

Run with auto-reload for development:

```bash
# Backend
cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev
```
