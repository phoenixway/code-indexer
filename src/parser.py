import os
from tree_sitter import Language, Parser, Query, QueryCursor
from .schema import CodeEntity, EntitySummary

class CodeParser:
    def __init__(self):
        import tree_sitter_python
        import tree_sitter_kotlin
        import tree_sitter_go
        
        # Завантажуємо мови через офіційні пакети
        self.LANGUAGES = {
            ".py": Language(tree_sitter_python.language()),
            ".kt": Language(tree_sitter_kotlin.language()),
            ".go": Language(tree_sitter_go.language())
        }

        # S-Expressions (запити) для пошуку функцій
        self.QUERIES = {
            ".py": """
                (function_definition name: (identifier) @name) @def
                (class_definition name: (identifier) @name) @def
            """,
            ".kt": """
                (function_declaration name: (identifier) @name) @def
                (class_declaration name: (identifier) @name) @def
            """,
            ".go": """
                (function_declaration name: (identifier) @name) @def
                (method_declaration name: (field_identifier) @name) @def
            """
        }

    def parse_file(self, filepath) -> list[CodeEntity]:
        ext = os.path.splitext(filepath)[1]
        lang = self.LANGUAGES.get(ext)
        if not lang: return []

        # 1. Ініціалізуємо парсер
        parser = Parser(lang)

        # 2. Читаємо файл
        try:
            with open(filepath, "rb") as f:
                code_bytes = f.read()
        except Exception as e:
            print(f"Read error {filepath}: {e}")
            return []

        # 3. Парсимо
        tree = parser.parse(code_bytes)
        
        # 4. Виконуємо запит
        query_scm = self.QUERIES.get(ext)
        if not query_scm: return []
        
        query = Query(lang, query_scm)
        cursor = QueryCursor(query)
        captures_dict = cursor.captures(tree.root_node)
        
        # Flatten for compatibility
        captures = []
        for name, nodes in captures_dict.items():
            for node in nodes:
                captures.append((node, name))

        entities = []
        processed = set()

        for node, capture_name in captures:
             if capture_name == "def":
                    # Уникаємо дублікатів (бо capture повертає і @name і @def)
                if node.start_byte in processed: continue
                processed.add(node.start_byte)

                # Знаходимо ім'я
                name_node = node.child_by_field_name("name")
                symbol = name_node.text.decode("utf8") if name_node else "anon"
                
                # Код і контракт
                full_code = node.text.decode("utf8")
                summary_text, resp, effects = self._parse_contract(full_code)

                summary_obj = None
                if summary_text:
                    summary_obj = EntitySummary(text=summary_text, source="human")

                entity = CodeEntity(
                    id=f"{filepath}:{symbol}",
                    type="function", 
                    path=filepath,
                    symbol=symbol,
                    summary=summary_obj,
                    responsibility=resp,
                    side_effects=effects,
                    confidence="low"
                )
                entity.update_confidence()
                entities.append(entity)
        
        return entities

    def _parse_contract(self, text):
        """Парсинг коментарів"""
        lines = text.split('\n')
        responsibility = None
        side_effects = []
        summary_text = None

        for line in lines:
            clean = line.replace("//", "").replace("#", "").replace("/*", "").strip()
            if "responsibility:" in clean.lower() or "@responsibility" in clean.lower():
                parts = clean.split(':', 1)
                if len(parts) > 1: responsibility = parts[1].strip()
            elif "side effect:" in clean.lower() or "@side-effect" in clean.lower():
                parts = clean.split(':', 1)
                if len(parts) > 1: side_effects.append(parts[1].strip())

        if responsibility: summary_text = responsibility
        return summary_text, responsibility, side_effects