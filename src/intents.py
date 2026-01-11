import os
import glob
from .config import DOCS_INTENTS_DIR
from .schema import Intent

class IntentParser:
    def parse_all(self) -> list[Intent]:
        intents = []
        if not os.path.exists(DOCS_INTENTS_DIR):
            print(f"Warning: {DOCS_INTENTS_DIR} not found.")
            return []

        # Читаємо всі .md файли
        files = glob.glob(os.path.join(DOCS_INTENTS_DIR, "*.md"))
        
        for fpath in files:
            intent = self._parse_md_file(fpath)
            if intent:
                intents.append(intent)
        return intents

    def _parse_md_file(self, fpath) -> Intent:
        """
        Формат MD:
        # intent.user_login
        Description of logic.
        
        ## Mapped Entities
        - pkg/auth/login.go:Login
        """
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        intent_id = None
        description = []
        mapped = []
        parsing_entities = False

        for line in lines:
            line = line.strip()
            if not line: continue

            if line.startswith("# intent."):
                intent_id = line.lstrip("# ").strip()
            elif line.startswith("## Mapped Entities"):
                parsing_entities = True
            elif line.startswith("-") and parsing_entities:
                mapped.append(line.lstrip("- ").strip())
            elif not parsing_entities and not line.startswith("#"):
                description.append(line)

        if not intent_id:
            print(f"Skipping {fpath}: No ID found (must start with '# intent.')")
            return None

        return Intent(
            id=intent_id,
            description=" ".join(description),
            mapped_entities=mapped
        )
