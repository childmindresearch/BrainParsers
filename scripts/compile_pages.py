#! /bin/python3

import os
from glob import glob
import subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../')
print(f'Running in: "{os.getcwd()}"')

DIR_DIST = 'dist'
BIN_KAITAI = 'kaitai-struct-compiler'
BIN_GRAPHVIZ = 'dot'

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BrainParsers</title>
    <style>
        body {{
            font-family: Helvetica, Arial, sans-serif;
        }}
        .gv-graph {{
            width: 100%;
        }}
    </style>
</head>
<body>
    <h1>BrainParsers</h1>
    {body}
</body>
</html>
'''

formats = []

for file in glob('formats/*.ksy'):
    print(f'Processing "{file}"...')

    filename = os.path.splitext(os.path.basename(file))[0]
    subprocess.call([BIN_KAITAI, '-t', 'graphviz', '-d', DIR_DIST, file], shell=True)
    subprocess.call([BIN_GRAPHVIZ, '-Gfontname=Helvetica', '-Nfontname=Helvetica', '-Efontname=Helvetica', '-Tsvg', f'{DIR_DIST}/{filename}.dot', '-o', f'{DIR_DIST}/graph_{filename}.svg'], shell=True)
    os.remove(f'{DIR_DIST}/{filename}.dot')

    formats.append({
        'file': file,
        'name': filename,
        'img': f'graph_{filename}.svg'
    })

formats.sort(key=lambda x: x['name'])
formats_html = '\n'.join([f'<h2>{x["name"]}</h2><img class="gv-graph" src="{x["img"]}">' for x in formats])
html = HTML_TEMPLATE.format(body=formats_html)

with open(f'{DIR_DIST}/index.html', 'w') as f:
    f.write(html)
