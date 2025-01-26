from webgen.fs import copy_files
from webgen.gen import generate_pages_recursively


def main():
    copy_files("static", "public")
    generate_pages_recursively("content", "template.html", "public")

if __name__ == "__main__":
    main()