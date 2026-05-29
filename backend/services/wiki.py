import json
from pathlib import Path
from typing import List
from config import settings


class WikiService:
    def __init__(self):
        self.articles: dict[str, str] = {}   # stem → content
        self.index: dict[str, list] = {}     # keyword → [stems]

    def load(self):
        wiki_dir = Path(settings.WIKI_DIR)

        if not wiki_dir.exists():
            print(f"[WARN] Wiki directory '{wiki_dir}' not found -- no articles loaded.")
            return

        # Load all .md files into memory
        for md_file in sorted(wiki_dir.glob("*.md")):
            self.articles[md_file.stem] = md_file.read_text(encoding="utf-8")

        # Load keyword index
        index_path = wiki_dir / "index.json"
        if index_path.exists():
            raw = index_path.read_text(encoding="utf-8").strip()
            if raw:
                self.index = json.loads(raw)

        print(f"[OK] Wiki loaded: {len(self.articles)} articles")

    def search(self, query: str, state: str = None) -> List[str]:
        """
        Returns top MAX_WIKI_ARTICLES article contents for a query.
        State-specific articles are boosted if state is provided.
        """
        query_lower = query.lower()
        tokens = [t for t in query_lower.split() if len(t) > 2]
        scores: dict[str, int] = {}

        for name, content in self.articles.items():
            score = 0
            content_lower = content.lower()

            # Keyword index boost
            for keyword, article_names in self.index.items():
                if keyword in query_lower and name in article_names:
                    score += 5

            # Token match score
            for token in tokens:
                if token in content_lower:
                    score += 1

            # Boost state-specific articles
            if state:
                state_key = f"state_{state.lower().replace(' ', '_')}"
                if name == state_key:
                    score += 10
                elif state.lower() in content_lower:
                    score += 3

            if score > 0:
                scores[name] = score

        top_names = sorted(scores, key=scores.get, reverse=True)
        top_names = top_names[:settings.MAX_WIKI_ARTICLES]

        return [self.articles[n] for n in top_names]

    def get_article(self, name: str) -> str | None:
        return self.articles.get(name)
