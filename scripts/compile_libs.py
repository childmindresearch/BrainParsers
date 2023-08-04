#! /bin/python3

import os
from glob import glob
import subprocess
import yaml
import shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../")
print(f'Running in: "{os.getcwd()}"')

DIR_DIST = "build"
BIN_KAITAI = "kaitai-struct-compiler"

formats = []

for file in glob("formats/*.ksy"):
    print(f'Processing "{file}"...')

    filename = os.path.splitext(os.path.basename(file))[0]
    
    subprocess.call(
        [BIN_KAITAI, "--target", "all", "--outdir", DIR_DIST, file],
        shell=os.name == 'nt'
    )

    with open(file, "r") as f:
        ksy = yaml.safe_load(f)

    formats.append({"file": file, "name": filename, "img": f"graph_{filename}.svg", "ksy": ksy})

formats.sort(key=lambda x: x["name"])


languages = []

for folder in glob(f"{DIR_DIST}/*"):
    if os.path.isdir(folder):
        languages.append(os.path.basename(folder))
        shutil.make_archive(folder, 'zip', folder)

languages.sort()

langs_text = ', '.join([f'{lang}' for lang in languages])
formats_text = '\n'.join([f'- {format["name"]}: {"" if "title" not in format["ksy"]["meta"] else format["ksy"]["meta"]["title"]}' for format in formats])

kaitai_version = subprocess.check_output([BIN_KAITAI, '--version'], shell=os.name == 'nt').decode('utf-8').strip()

body_text = f"""

Compiled with `{kaitai_version}`.

## Languages:

{langs_text}

## Formats:

{formats_text}
""".strip()

with open(f'{DIR_DIST}/README.md', 'w', encoding='utf-8') as f:
    f.write(body_text)

