<h1 align="center">
  <br>
  🚗 DriveLegal
  <br>
</h1>

<h4 align="center">An AI-powered Indian traffic law assistant — fines, challans & MV Act 2019</h4>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black"/>
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white"/>
  <img alt="Android" src="https://img.shields.io/badge/Android-APK-3DDC84?style=for-the-badge&logo=android&logoColor=white"/>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-environment-variables">Environment</a> •
  <a href="#-deployment">Deployment</a>
</p>

---

## 📖 Overview

**DriveLegal** is a multilingual, AI-powered chatbot assistant built for Indian drivers. It helps users understand their rights and obligations under the **Motor Vehicles (Amendment) Act 2019**, look up traffic fines by violation type and state, check challans on Parivahan, and get localized legal guidance — all via a sleek web app or a native **Android APK**.

> Built at IIT Hackathon 🏆

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Chat** | Conversational interface powered by LLMs (Grok / Llama / Groq / Ollama) |
| 🧮 **Fine Calculator** | Instant fine lookup by violation, vehicle type, state & offense count |
| 🗺️ **Location-Aware** | Provides state-specific fines and legal notes |
| 🌐 **Multilingual** | Supports Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali & more |
| 📲 **WhatsApp Bot** | Integrates with Twilio or Meta WhatsApp API |
| 🔗 **Parivahan Links** | Auto-links to echallan.parivahan.gov.in for challan payment |
| 📱 **Android APK** | Capacitor-wrapped native Android app |
| ⚡ **Session Memory** | Per-user chat history via Redis (Upstash) or in-memory |
| 📚 **Wiki RAG** | Retrieval-Augmented Generation from a curated traffic law knowledge base |

---

## 🛠 Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance Python API framework
- **[Pydantic v2](https://docs.pydantic.dev/)** — Data validation and settings management
- **[HTTPX](https://www.python-httpx.org/) / [aiohttp](https://docs.aiohttp.org/)** — Async HTTP clients for LLM APIs
- **[Upstash Redis](https://upstash.com/)** — Serverless Redis for session persistence
- **[Geopy](https://geopy.readthedocs.io/)** — Location extraction and geocoding
- **LLM Providers** — xAI (Grok), OpenRouter, Groq, Ollama (local)

### Frontend
- **[React 19](https://react.dev/)** — UI framework
- **[TypeScript 6](https://www.typescriptlang.org/)** — Type-safe development
- **[Vite 8](https://vitejs.dev/)** — Lightning-fast build tool
- **[Tailwind CSS 4](https://tailwindcss.com/)** — Utility-first CSS framework
- **[Framer Motion](https://www.framer.com/motion/)** — Smooth animations
- **[Lucide React](https://lucide.dev/)** — Icon library
- **[Capacitor](https://capacitorjs.com/)** — Cross-platform native Android app wrapper

### DevOps
- **[Render](https://render.com/)** — Cloud deployment (via `render.yaml`)

---

## 📁 Project Structure

```
drive-legal/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # App entry point, CORS, router registration
│   ├── config.py               # Pydantic settings (all env vars)
│   ├── dependencies.py         # FastAPI dependency injection
│   ├── requirements.txt        # Python dependencies
│   ├── Procfile                # Process definition for deployment
│   ├── runtime.txt             # Python version pin
│   ├── .env.example            # Environment variable template
│   ├── routers/
│   │   ├── chat.py             # /chat — main AI conversation endpoint
│   │   ├── calculator.py       # /calculator — traffic fine calculator
│   │   ├── location.py         # /location — location parsing
│   │   ├── language.py         # /language — language detection
│   │   ├── whatsapp.py         # /whatsapp — WhatsApp webhook handler
│   │   └── health.py           # /health — health check
│   ├── models/                 # Pydantic request/response models
│   ├── services/               # Business logic
│   │   ├── llm.py              # LLM provider abstraction
│   │   ├── session.py          # Session management (Redis / in-memory)
│   │   ├── wiki.py             # Wiki search & RAG
│   │   ├── calculator.py       # Fine lookup logic
│   │   ├── language.py         # Multilingual support
│   │   └── location.py         # Location extraction
│   ├── utils/                  # Utility helpers
│   ├── prompts/                # LLM system prompt templates
│   └── wiki/                   # Curated traffic law knowledge base (Markdown)
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── App.tsx             # Root component with chat + calculator layout
│   │   ├── components/
│   │   │   ├── demo.tsx        # Main chat UI component
│   │   │   └── FineCalculator.tsx  # Fine calculator sidebar
│   │   └── lib/
│   │       └── utils.ts        # Utility functions (cn, etc.)
│   ├── android/                # Capacitor Android project
│   ├── capacitor.config.ts     # Capacitor app config (appId, webDir)
│   ├── vite.config.ts          # Vite build config
│   └── package.json            # Frontend dependencies
│
├── render.yaml                 # Render cloud deployment config
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- At least one LLM API key (Groq, OpenRouter, or xAI)

---

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and configure environment variables
cp .env.example .env
# Edit .env and add at least one LLM API key

# 5. Start the development server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Configure the backend URL (optional — defaults to localhost)
# Edit .env.production or create a .env.local

# 4. Start the development server
npm run dev
```

The web app will be available at `http://localhost:5173`.

---

### Building the Android APK

```bash
cd frontend

# 1. Build the web app
npm run build

# 2. Sync with Capacitor
npx cap sync android

# 3. Open in Android Studio and build the APK
npx cap open android
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check |
| `POST` | `/chat` | AI conversation |
| `POST` | `/calculator` | Fine calculation |
| `GET` | `/location` | Location parsing |
| `GET` | `/language` | Language detection |
| `POST` | `/whatsapp` | WhatsApp webhook |

### POST `/chat`

```json
{
  "session_id": "user-123",
  "message": "What is the fine for not wearing a helmet in Maharashtra?",
  "language": "English",
  "state": "Maharashtra",
  "city": "Mumbai"
}
```

**Response:**
```json
{
  "reply": "The fine for not wearing a helmet in Maharashtra under Section 129...",
  "language": "English",
  "session_id": "user-123",
  "parivahan_link": "https://echallan.parivahan.gov.in/..."
}
```

### POST `/calculator`

```json
{
  "violation": "helmet",
  "vehicle_type": "two-wheeler",
  "state": "Maharashtra",
  "offense_count": 1
}
```

**Response:**
```json
{
  "violation": "helmet",
  "section": "Section 129, MV Act 2019",
  "vehicle_type": "two-wheeler",
  "state": "Maharashtra",
  "offense": 1,
  "fine_min": 1000,
  "fine_max": 1000,
  "fine_display": "₹1,000",
  "state_note": null,
  "parivahan_link": "https://echallan.parivahan.gov.in/..."
}
```

---

## 🔐 Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

### LLM Providers (set at least one)

| Variable | Description | Default |
|---|---|---|
| `XAI_API_KEY` | xAI (Grok) API key | — |
| `XAI_MODEL` | Grok model to use | `grok-3` |
| `OPENROUTER_API_KEY` | OpenRouter API key | — |
| `OPENROUTER_MODEL` | OpenRouter model | `meta-llama/llama-3.3-70b-instruct:free` |
| `GROQ_API_KEY` | Groq API key | — |
| `GROQ_MODEL` | Groq model | `llama-3.3-70b-versatile` |
| `OLLAMA_BASE_URL` | Local Ollama base URL | — |
| `OLLAMA_MODEL` | Ollama model | `gemma2:9b` |

### Redis / Sessions

| Variable | Description | Default |
|---|---|---|
| `UPSTASH_REDIS_REST_URL` | Upstash Redis REST URL | in-memory (dev only) |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash Redis token | — |
| `SESSION_TTL_SECONDS` | Session expiry in seconds | `86400` (24 h) |

### WhatsApp (Optional)

| Variable | Description |
|---|---|
| `WHATSAPP_PROVIDER` | `twilio` or `meta` |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `META_VERIFY_TOKEN` | Meta webhook verify token |
| `META_ACCESS_TOKEN` | Meta permanent access token |

### App Settings

| Variable | Description | Default |
|---|---|---|
| `WIKI_DIR` | Path to wiki knowledge base | `wiki` |
| `MAX_HISTORY_TURNS` | Chat history turns kept in context | `6` |
| `MAX_WIKI_ARTICLES` | Max RAG articles injected per query | `3` |
| `PARIVAHAN_BASE_URL` | Parivahan e-challan base URL | `https://echallan.parivahan.gov.in` |
| `DEBUG` | Enable debug logging | `false` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit per session | `30` |

---

## ☁️ Deployment

### Render (recommended)

The repo includes a `render.yaml` for one-click deployment on [Render](https://render.com/):

```bash
# Connect your GitHub repo to Render
# Render will auto-detect render.yaml and deploy the backend
```

Set the following secrets manually in the Render dashboard:
- `XAI_API_KEY` / `OPENROUTER_API_KEY` / `GROQ_API_KEY`
- `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`

### Manual (Docker / VPS)

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🌍 Supported Languages

DriveLegal auto-detects and responds in:

- 🇮🇳 English
- 🇮🇳 Hindi (हिन्दी)
- 🇮🇳 Tamil (தமிழ்)
- 🇮🇳 Telugu (తెలుగు)
- 🇮🇳 Kannada (ಕನ್ನಡ)
- 🇮🇳 Malayalam (മലയാളം)
- 🇮🇳 Bengali (বাংলা)

---

## 📜 License

This project was created for an IIT Hackathon. All rights reserved.

---

<p align="center">Made with ❤️ for Indian drivers</p>
