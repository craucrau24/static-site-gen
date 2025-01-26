import os

from data.highlevel import markdown_to_html_node


def extract_title(text):
    for line in text.splitlines():
        if line.lstrip().startswith("# "):
            return line.lstrip()[2:].strip()
    raise Exception("no header found")

def generate_page(from_path, template_path, dest_path):
    print(f"Generate page from {from_path} to {dest_path} using {template_path}")
    with open(from_path) as f:
        md_file = f.read()

    with open(template_path) as f:
        template_file = f.read()
    
    html = markdown_to_html_node(md_file).to_html()
    title = extract_title(md_file)

    html_content = template_file.replace("{{ Title }}", title).replace("{{ Content }}", html)

    base_dir = os.path.dirname(dest_path)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    with open(dest_path, "w") as f:
        f.write(html_content)