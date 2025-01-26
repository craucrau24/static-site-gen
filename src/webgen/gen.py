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

def generate_pages_recursively(dir_path_content, template_path, dest_dir_path, path=""):
    dest_dir = os.path.join(dest_dir_path, path)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    with os.scandir(os.path.join(dir_path_content, path)) as it:
        for entry in it:
            if entry.is_dir():
                generate_pages_recursively(dir_path_content, template_path, dest_dir_path, os.path.join(path, entry.name))
            elif entry.is_file():
                new_file = entry.name.rsplit(".", maxsplit=1)[0] + ".html"
                generate_page(os.path.join(dir_path_content, path, entry.name), template_path, os.path.join(dest_dir, new_file))