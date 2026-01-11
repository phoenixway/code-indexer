import os
import hashlib
from tree_sitter_languages import get_language, get_parser
from .config import LANGUAGE_MAP
from .schema import CodeEntity, EntitySummary

class CodeParser:
    def __init__(self):
        self.parsers = {}
        self.queries_scm = {
            "python": """(function_definition name: (identifier) @name) @def 
                         (class_definition name: (identifier) @name) @def""",
            "javascript": """(function_declaration name: (identifier) @name) @def 
                             (class_declaration name: (identifier) @name) @def""",
            "go": """(function_declaration name: (identifier) @name) @def"""
        }

    def _get_parser(self, ext):
        lang = LANGUAGE_MAP.get(ext)
        if not lang or lang not in self.queries_scm: return None, None
        if lang not in self.parsers: self.parsers[lang] = get_parser(lang)
        return self.parsers[lang], lang

    def _parse_contract_from_docstring(self, code_text):
        """
        Парсить людський контракт з коментарів.
        Повертає: (summary_text, responsibility, side_effects)
        """
        lines = code_text.split('\n')
        responsibility = None
        side_effects = []
        summary_text = None

        for line in lines:
            line = line.strip().strip('/*').strip('*/').strip('#').strip()
            
            if "@responsibility" in line.lower() or line.lower().startswith("responsibility:"):
                responsibility = line.split(':', 1)[1].strip()
            elif "@side-effect" in line.lower() or line.lower().startswith("side effect:"):
                side_effects.append(line.split(':', 1)[1].strip())
            
        # Якщо є явна відповідальність, вона стає summary
        if responsibility:
            summary_text = responsibility
            
        return summary_text, responsibility, side_effects

    def parse_file(self, filepath) -> list[CodeEntity]:
        ext = os.path.splitext(filepath)[1]
        parser, lang_name = self._get_parser(ext)
        if not parser: return []

        with open(filepath, "rb") as f:
            code_bytes = f.read()

        tree = parser.parse(code_bytes)
        query = get_language(lang_name).query(self.queries_scm[lang_name])
        captures = query.captures(tree.root_node)
        
        entities = []
        processed = set()

        for node, capture_name in captures:
            if capture_name == "def":
                if node.start_byte in processed: continue
                processed.add(node.start_byte)

                name_node = node.child_by_field_name("name")
                symbol = name_node.text.decode("utf8") if name_node else "anon"
                entity_id = f"{filepath}:{symbol}"
                
                # Отримуємо повний текст блоку для аналізу коментарів
                full_text = node.text.decode("utf8")
                
                # Спроба витягти контракт
                sum_text, resp, effects = self._parse_contract_from_docstring(full_text)
                
                summary_obj = None
                if sum_text:
                    summary_obj = EntitySummary(text=sum_text, source="human")

                entity = CodeEntity(
                    id=entity_id,
                    type="function", # Спрощено
                    path=filepath,
                    symbol=symbol,
                    summary=summary_obj,
                    responsibility=resp,
                    side_effects=effects,
                    confidence="low" # Буде оновлено в update_confidence
                )
                entity.update_confidence()
                entities.append(entity)
                
        return entities
