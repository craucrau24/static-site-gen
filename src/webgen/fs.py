import os
import shutil

def copy_src_dir_to_dest_dir(src, dest, path=""):
    dest_dir = os.path.join(dest, path)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    with os.scandir(os.path.join(src, path)) as it:
        for entry in it:
            if entry.is_dir():
                copy_src_dir_to_dest_dir(src, dest, os.path.join(path, entry.name))
            elif entry.is_file():
                shutil.copy(os.path.join(src, path, entry.name), dest_dir)

def copy_files(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    copy_src_dir_to_dest_dir(src, dest)
            
