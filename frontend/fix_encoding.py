import pathlib
import sys

def fix_file(filename):
    try:
        content = pathlib.Path(filename).read_text(encoding='utf-16le')
        pathlib.Path(f"{filename.replace('.js', '_utf8.js').replace('.html', '_utf8.html').replace('.css', '_utf8.css')}").write_text(content, encoding='utf-8')
        print(f"Fixed {filename}")
    except Exception as e:
        print(f"Error on {filename}: {e}")

fix_file('app.js')
fix_file('index.html')
fix_file('style.css')
