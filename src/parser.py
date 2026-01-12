import os
import ctypes
from tree_sitter import Language, Parser
from .schema import CodeEntity, EntitySummary

class CodeParser:
    def __init__(self):
        # Шлях до скомпільованого файлу (абсолютний, відносно кореня проекту)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        lib_path = os.path.join(base_dir, 'build', 'my-languages.so')
        
        if not os.path.exists(lib_path):
            raise FileNotFoundError("Run 'python3 build_langs.py' first!")

        # Завантажуємо спільну бібліотеку
        try:
            self.lib = ctypes.CDLL(lib_path)
        except Exception as e:
            print(f"Error loading {lib_path}: {e}")
            raise

        # Налаштовуємо типи повернення для функцій мов
        self.lib.tree_sitter_python.restype = ctypes.c_void_p
        self.lib.tree_sitter_kotlin.restype = ctypes.c_void_p
        self.lib.tree_sitter_go.restype = ctypes.c_void_p

        # Завантажуємо мови
        self.LANGUAGES = {
            ".py": Language(self.lib.tree_sitter_python()),
            ".kt": Language(self.lib.tree_sitter_kotlin()),
            ".go": Language(self.lib.tree_sitter_go())
        }

        # S-Expressions (запити) для пошуку функцій
        self.QUERIES = {
            ".py": """
                (function_definition name: (identifier) @name) @def
                (class_definition name: (identifier) @name) @def
            """,
            ".kt": """
                (function_declaration name: (simple_identifier) @name) @def
                (class_declaration name: (type_identifier) @name) @def
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
        parser = Parser()
        parser.set_language(lang)

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
        
        query = lang.query(query_scm)
        captures = query.captures(tree.root_node)

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