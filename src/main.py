from webgen.fs import copy_files
from webgen.gen import generate_page


def main():
    copy_files("static", "public")
    generate_page("content/index.md", "template.html", "public/index.html")

if __name__ == "__main__":
    main()