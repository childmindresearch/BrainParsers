#! /bin/python3

import os
from glob import glob
import subprocess
import yaml

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../")
print(f'Running in: "{os.getcwd()}"')

DIR_DIST = "dist"
BIN_KAITAI = "kaitai-struct-compiler"
BIN_GRAPHVIZ = "dot"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BrainParsers</title>
    <style>
        body {{
            font-family: Helvetica, Arial, sans-serif;
        }}
        main {{
            width: 768px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
        }}
        h2 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        a {{
            text-decoration: none;
            color: black;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .entry-id-link {{
            text-decoration: none;
            color: black;
        }}
        .entry-id-link:hover {{
            text-decoration: underline;
        }}
        .entry-doc {{
            margin-top: 0.5em;
            margin-bottom: 0.5em;
        }}
        .entry-doc ul {{
            margin-top: 0.5em;
            margin-bottom: 0.5em;
        }}
        .entry-doc li {{
            margin-top: 0.5em;
            margin-bottom: 0.5em;
        }}
        .entry-doc p {{
            margin-top: 0.5em;
            margin-bottom: 0.5em;
        }}
        @media (max-width: 768px) {{
            main {{
                width: 100%;
            }}
        }}
        .entry-ext {{
            color: #888;
            font-size: 0.8em;
        }}
        .entry-github {{
            font-size: 0.8em;
        }}
        .entry-ref {{
            float: right;
        }}
        .gv-graph {{
            width: 100%;
        }}
    </style>
</head>
<body>
    <main>
    <a href="https://github.com/cmi-dair/BrainParsers"><h1>BrainParsers</h1></a>
    {body}
    </main>
</body>
</html>
"""

HTML_TEMPLATE_ENTRY = """
<a class="entry-id-link" href="#{id}"><h2 id="{id}">{title} <span class="entry-ext">({extension})</span></h2></a>
<a class="entry-github" href="https://github.com/cmi-dair/BrainParsers/tree/main/{file}">
<svg style="margin-bottom: -0.3em" height="1.4em" viewBox="0 0 98 96"><path fill-rule="evenodd" clip-rule="evenodd" d="M48.854 0C21.839 0 0 22 0 49.217c0 21.756 13.993 40.172 33.405 46.69 2.427.49 3.316-1.059 3.316-2.362 0-1.141-.08-5.052-.08-9.127-13.59 2.934-16.42-5.867-16.42-5.867-2.184-5.704-5.42-7.17-5.42-7.17-4.448-3.015.324-3.015.324-3.015 4.934.326 7.523 5.052 7.523 5.052 4.367 7.496 11.404 5.378 14.235 4.074.404-3.178 1.699-5.378 3.074-6.6-10.839-1.141-22.243-5.378-22.243-24.283 0-5.378 1.94-9.778 5.014-13.2-.485-1.222-2.184-6.275.486-13.038 0 0 4.125-1.304 13.426 5.052a46.97 46.97 0 0 1 12.214-1.63c4.125 0 8.33.571 12.213 1.63 9.302-6.356 13.427-5.052 13.427-5.052 2.67 6.763.97 11.816.485 13.038 3.155 3.422 5.015 7.822 5.015 13.2 0 18.905-11.404 23.06-22.324 24.283 1.78 1.548 3.316 4.481 3.316 9.126 0 6.6-.08 11.897-.08 13.526 0 1.304.89 2.853 3.316 2.364 19.412-6.52 33.405-24.935 33.405-46.691C97.707 22 75.788 0 48.854 0z" fill="#24292f"/></svg>
Show on GitHub</a>
<p class="entry-doc">{doc}</p>
<a class="entry-ref" href="{doc_ref}">(Reference)</a>
<a href="{img}"><img class="gv-graph" src="{img}"></a>
"""

formats = []

for file in glob("formats/*.ksy"):
    print(f'Processing "{file}"...')

    filename = os.path.splitext(os.path.basename(file))[0]
    if (
        subprocess.call(
            [BIN_KAITAI, "--target", "graphviz", "--outdir", DIR_DIST, file],
            shell=os.name == 'nt'
        )
        == 0
    ):
        subprocess.call(
            [
                BIN_GRAPHVIZ,
                "-Gfontname=Helvetica",
                "-Nfontname=Helvetica",
                "-Efontname=Helvetica",
                "-Tsvg",
                f"{DIR_DIST}/{filename}.dot",
                "-o",
                f"{DIR_DIST}/graph_{filename}.svg",
            ]
        )
    try:
        os.remove(f"{DIR_DIST}/{filename}.dot")
    except OSError:  # File not found
        pass

    with open(file, "r") as f:
        ksy = yaml.safe_load(f)

    formats.append({"file": file, "name": filename, "img": f"graph_{filename}.svg", "ksy": ksy})


# convert all lines starting with '* ' to <li>
def format_doc(text):
    lines = []
    ul_open = False
    for line in text.split("\n"):
        if line.startswith("* "):
            if not ul_open:
                lines.append("<ul>")
                ul_open = True
            lines.append(f'<li>{line[2:]}</li>')
        else:
            if ul_open:
                lines.append("</ul>")
                ul_open = False
            lines.append(line)

    return "\n".join(lines)


formats.sort(key=lambda x: x["name"])
formats_html = "\n".join(
    [
        HTML_TEMPLATE_ENTRY.format(
            id=x["name"],
            title=x["name"] if "title" not in x["ksy"]["meta"] else x["ksy"]["meta"]["title"],
            extension='.' + x["ksy"]["meta"]["file-extension"],
            file=x["file"],
            doc=format_doc("[Description]" if "doc" not in x["ksy"] else x["ksy"]["doc"]),
            doc_ref="#" if "doc-ref" not in x["ksy"] else x["ksy"]["doc-ref"],
            img=x["img"],
        )
     for x in formats]
)
html = HTML_TEMPLATE.format(body=formats_html)

with open(f"{DIR_DIST}/index.html", "w") as f:
    f.write(html)
