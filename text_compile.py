"""
Usage:
 
Call with a single argument of either a folder (to pack) or a file (to unpack). It's essentially a poor
man's .zip file for a situation where a .zip file wasn't an option.
 
If targeted at a folder it will pack all items within the folder with an extension matching the below list.
 
If target at a file it will assume it is the result of a tc.py run and attempt to reverse the process into
a folder as defined by the "out_folder" variable.
 
"""
 
import argparse
import os
from os.path import isfile, join
import re
 
out_folder = "tc_unpack"
splitter = ">>>>FILE>>>>"
root_folder = __file__.replace("tc.py", "")
 
allowed_extensions = ["py", "pt", "txt", "html", "js", "css", "sql", "sh", "hs", "ini"]
ex_search = re.compile(r"\.([a-zA-Z0-9_-]+)$")
name_search = re.compile(r"/?([a-zA-Z0-9-_ ]+\.[a-zA-Z0-9_-]+)$")
 
found_extensions = set()
 
def iter_tree(folder_path, filter_f=None):
    result = []
   
    file_list = os.listdir(folder_path)
   
    for f in file_list:
        if not isfile(join(folder_path, f)):
            result.extend(iter_tree(join(folder_path, f), filter_f))
            continue
       
        if filter_f is None or filter_f(f):
            result.append((folder_path, f))
   
    return result
 
def build_file(filepath):
    ext = ex_search.search(filepath)
   
    if ext is None:
        return ""
   
    ext = ext.groups()[0]
   
    if ext in allowed_extensions:
        with open(filepath, encoding="utf-8") as f:
            return "{}\n{}\n{}".format(
                splitter,
                filepath,
                f.read(),
            )
    else:
        found_extensions.add(ext)
   
    return ""
 
def pack(args):
    contents = []
   
    for p, f in iter_tree(args.d, lambda f: f != "tc.py"):
        path = join(p,f)
       
        try:
            result = build_file(path)
        except Exception as e:
            print("Error with file {}".format(path))
            pass
       
        
        contents.append(result)
   
    with open('tc_out.txt', "w", encoding="utf-8") as f:
        f.write("")
   
    with open('tc_out.txt', "w", encoding="utf-8") as f:
        f.write("".join(contents))
   
    print("Compiled file created as tc_out.txt")
   
    if len(found_extensions) > 0:
        print("Found {} extension{} not accepted: {}".format(
            len(found_extensions),
            "s" if len(found_extensions) > 1 else "",
            ", ".join(list(found_extensions))
        ))
 
 
def write_file(file_path, content):
    while file_path[0] in (".", "/"):
        file_path = file_path[1:]
   
    name = name_search.search(file_path).groups()[0]
    folder_path = join(out_folder, file_path.replace(name, ""))
   
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
   
    with open(join(folder_path, name), "w") as f:
        f.write(content)
   
def unpack(args):
    with open(args.d, encoding="utf-8") as f:
        parts = f.read().split(splitter)
   
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
   
    for p in parts:
        if p == "": continue
       
        lines = p.split("\n")
        path = lines[1]
        content = "\n".join(lines[2:])
       
        write_file(path, content)
 
 
def main():
    parser = argparse.ArgumentParser(description='Text compiler', prog="tc")
    parser.add_argument('d', help='The directory the program will be compiling or the file the program will decompile')
   
    args = parser.parse_args()
   
    if os.path.isfile(args.d):
        unpack(args)
    else:
        pack(args)
 
if __name__ == '__main__':
    main()
