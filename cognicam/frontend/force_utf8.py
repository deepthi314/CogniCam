import os

def force_utf8(filepath):
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
            
        # Try various decodings
        decoded_text = None
        for enc in ['utf-8', 'utf-16le', 'utf-16be', 'latin-1']:
            try:
                decoded_text = raw.decode(enc)
                print(f"Successfully decoded {filepath} with {enc}")
                break
            except UnicodeDecodeError:
                pass
                
        if decoded_text is None:
            decoded_text = raw.decode('utf-8', errors='ignore')
            print(f"Fallback decoded {filepath} ignoring errors")
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(decoded_text)
            print(f"Wrote {filepath} as utf-8")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

force_utf8('F:/CogniCAM/cognicam/frontend/app.js')
force_utf8('F:/CogniCAM/cognicam/frontend/index.html')
force_utf8('F:/CogniCAM/cognicam/frontend/style.css')
