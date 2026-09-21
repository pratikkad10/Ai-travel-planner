# 🌍 AI Travel Planner

A modern full-stack AI travel companion that understands your trip requests, searches for live travel data, converts currencies, calculates budgets, and crafts personalized itineraries in real time.

Built with **LangGraph**, **FastAPI**, **React 19**, and **Tailwind CSS v4**.

---

## ✨ Features

- 🧠 **LangGraph Agent**: Autonomous agent equipped with real-time tools for flight search, hotel accommodations, weather forecasts, currency conversions, and arithmetic.
- ⚡ **FastAPI Streaming Backend**: Real-time token streaming (`/api/chat/stream`) and standard JSON chat endpoints (`/api/chat`).
- 🎨 **Modern Spotify Dark & Light Themes**: Sleek, distraction-free UI featuring Spotify's signature `#121212` deep gray dark mode and clean white light mode with smooth transitions.
- 💬 **Trip Session History**: Automatically saves conversations to `localStorage` with a collapsible sidebar for seamless trip switching.
- 📊 **Rich Markdown & Table Formatting**: Cleanly renders itineraries, price comparison tables, bold highlights, and bullet lists.
- 🚀 **Production Ready**: Configured with `vercel.json` and modular architecture for deployment on **Railway** (backend) and **Vercel** (frontend).

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite, Tailwind CSS v4, Lucide Icons, TypeScript |
| **Backend** | FastAPI, Uvicorn, Pydantic, Python 3.11+ |
| **AI & Agents** | LangGraph, LangChain, ChatMistralAI (`ministral-3b-latest`) |
| **Tools & Data** | Tavily Search, BeautifulSoup4, Requests |

---

## 🚀 Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-travel-planner.git
cd ai-travel-planner
```

---

### 2. Backend Setup (`ai-service`)

```bash
cd ai-service

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file inside `ai-service/`:
```env
MISTRAL_API_KEY=your_mistral_api_key
TAVILY_API_KEY=your_tavily_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
FLIGHT_MCP_API_KEY=your_flight_mcp_api_key
GEOAPIFY_API_KEY=your_geoapify_api_key
```

Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```
API Documentation will be live at `http://localhost:8000/docs`.

---

### 3. Frontend Setup (`frontend`)

In a new terminal:
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🔌 API Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health-check endpoint |
| `POST` | `/api/chat` | Synchronous agent invocation with `thread_id` session memory |
| `POST` | `/api/chat/stream` | Server-Sent real-time token stream |

---

## 🚢 Deployment

- **Backend (FastAPI)**: Deploy to [Railway.app](https://railway.app)
  - Root directory: `/ai-service`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Add required environment variables in Railway settings:
    - `MISTRAL_API_KEY`
    - `TAVILY_API_KEY`
    - `LANGSMITH_API_KEY`
    - `FLIGHT_MCP_API_KEY`
    - `GEOAPIFY_API_KEY`
- **Frontend (Vite)**: Deploy to [Vercel](https://vercel.com)
  - Root directory: `frontend`
  - Build command: `npm run build`
  - Output directory: `dist`
  - Environment variable: `VITE_API_BASE_URL` = `https://your-backend-url.up.railway.app`

---

## 📄 License

MIT License. Feel free to use and customize for your own projects!
