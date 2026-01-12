# build_langs.py
import os
import subprocess

# Шляхи до скачаних репо
languages = {
    'python': 'vendor/tree-sitter-python',
    'kotlin': 'vendor/tree-sitter-kotlin',
    'go': 'vendor/tree-sitter-go'
}

def build():
    print("Compiling languages... This takes 1-2 minutes.")
    
    if not os.path.exists('build'):
        os.makedirs('build')

    # Команда для компіляції всіх мов в один .so файл
    # Ми використовуємо gcc напряму, оскільки Language.build_library було видалено в нових версіях tree-sitter
    cmd = ['gcc', '-shared', '-fPIC', '-O3']
    
    for lang, path in languages.items():
        src_path = os.path.join(path, 'src')
        parser_c = os.path.join(src_path, 'parser.c')
        scanner_c = os.path.join(src_path, 'scanner.c')
        scanner_cc = os.path.join(src_path, 'scanner.cc')
        
        if not os.path.exists(parser_c):
            print(f"Warning: {parser_c} not found, skipping {lang}")
            continue
            
        cmd.extend(['-I', src_path])
        cmd.append(parser_c)
        
        if os.path.exists(scanner_c):
            cmd.append(scanner_c)
        elif os.path.exists(scanner_cc):
            # Якщо є scanner.cc, нам може знадобитися g++ або скомпілювати окремо
            # Але для більшості стандартних граматик це .c
            cmd.append(scanner_cc)

    cmd.extend(['-o', 'build/my-languages.so'])
    
    try:
        subprocess.check_call(cmd)
        print("Done! 'build/my-languages.so' created.")
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}")
        exit(1)

if __name__ == "__main__":
    build()