from fastapi import Request
from services.wiki import WikiService


def get_wiki(request: Request) -> WikiService:
    """Dependency to inject WikiService from app state."""
    return request.app.state.wiki
