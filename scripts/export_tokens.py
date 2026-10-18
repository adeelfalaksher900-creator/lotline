from pathlib import Path
import re
text=Path('DESIGN.md').read_text()
colors=re.search(r'colors:\n(.*?)typography:',text,re.S).group(1)
pairs=re.findall(r"  ([a-z]+): '([^']+)'",colors)
Path('web/src/tokens.css').write_text(':root {\n'+''.join(f'  --color-{k}: {v};\n' for k,v in pairs)+'  --font-sans: Manrope, Arial, sans-serif;\n  --font-mono: "IBM Plex Mono", monospace;\n}\n')
