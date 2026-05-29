import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from services.wiki import WikiService
from routers import chat, calculator, location, language, whatsapp, health
from config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Starting DriveLegal API...")
    app.state.wiki = WikiService()
    app.state.wiki.load()
    logger.info(f"Wiki: {len(app.state.wiki.articles)} articles loaded")
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down DriveLegal API.")


app = FastAPI(
    title="DriveLegal API",
    description="Indian traffic law assistant — fines, challans, MV Act 2019",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat.router,        prefix="/chat",       tags=["Chat"])
app.include_router(calculator.router,  prefix="/calculator", tags=["Fine Calculator"])
app.include_router(location.router,    prefix="/location",   tags=["Location"])
app.include_router(language.router,    prefix="/language",   tags=["Language"])
app.include_router(whatsapp.router,    prefix="/whatsapp",   tags=["WhatsApp"])
app.include_router(health.router,                            tags=["Health"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "DriveLegal API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
