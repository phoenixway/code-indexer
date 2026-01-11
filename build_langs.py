# build_langs.py
from tree_sitter import Language

# Вказуємо шляхи до скачаних репо
paths = [
    'vendor/tree-sitter-python',
    'vendor/tree-sitter-kotlin',
    'vendor/tree-sitter-go'
]

print("Compiling languages... This takes 1-2 minutes on phone.")

# Ця команда компілює все в один файл .so
Language.build_library(
    'build/my-languages.so', # Результат
    paths                    # Джерела
)

print("Done! 'build/my-languages.so' created.")
