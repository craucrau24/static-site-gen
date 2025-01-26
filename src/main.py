from webgen.fs import copy_files

def main():
    copy_files("static", "public")

if __name__ == "__main__":
    main()