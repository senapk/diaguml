#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import tempfile
import os
import shutil
import subprocess



urm_core = "/home/tiger/dev/uml/urm-core.jar"

class Mount:
    def __init__(self):
        self.atributes = []
        self.private = []
        self.public = []
        self.protected = []
        self.toString = False

    def add(self, line):
        if line.startswith("    ") and not "(" in line:
            self.atributes.append(line)
            return True
        elif "toString(" in line:
            self.toString = True
            return True
        elif line.startswith("    ~"):
            self.protected.append(line)
            return True
        elif line.startswith("    -"):
            self.private.append(line)
            return True
        elif line.startswith("    +"):
            self.public.append(line)
            return True
        return False

    def clear(self):
        self.public.clear()
        self.private.clear()
        self.protected.clear()
        self.atributes.clear()

    def process(self):
        if self.toString:
            self.public.append("    + toString() : String")
        self.atributes = sorted(self.atributes)
        mount = [self.atributes] + [self.private] + [self.public] + [self.protected]
        mount = ["\n".join(l) + "\n" for l in mount if len(l) != 0]
        return "    __\n".join(mount)

def sort_classes(file_path: str):
    with open(file_path) as f:
        content = f.read()
    output: List[str] = []
    lines = content.split("\n")
    mount = Mount()
    for line in lines:
        if line.startswith("    ..") or line.startswith("    __"):
            pass
        elif line.startswith("  }"):
            output.append(mount.process())
            mount.clear()
            output.append("  }")
        elif not mount.add(line):
            output.append(line)
    result = "\n".join(output)
    result = result.replace("abstract ~class", "~abstract class")
    with open(file_path, "w") as f:
        f.write(result)


def build_project(folder, content):
    os.mkdir(folder + os.sep + "build")
    src_path = [folder, "src", "com", "qxcode"]
    for i in range(1, len(src_path)):
        os.mkdir(os.sep.join(src_path[0:(i + 1)]))
    src_solver = os.sep.join(src_path + ["Solver.java"])
    with open(folder + os.sep + "myManifest", "w") as f:
        f.write("Main-Class: com.qxcode.Solver\n")
    with open(src_solver, "w") as f:
        f.write("package com.qxcode;\n" + content)
    return src_solver

def make_jar(folder, src_solver):
    cmd = ["javac", "-g", "-sourcepath", 
            folder + os.sep + "src", "-d", 
            folder + os.sep + "build", src_solver]
    subprocess.run(cmd)
    dest_jar = folder + os.sep + "qxcode.jar"
    cmd = ["jar", "cfm", dest_jar, 
            folder + os.sep + "myManifest", "-C", 
            folder + os.sep + "build", "."]
    subprocess.run(cmd)
    print(folder)
    return dest_jar

def make_png(folder, dest_jar, target_folder, puml_only):
    puml_file = folder + os.sep + "diagrama.puml"
    cmd = ["java", "-cp", 
            urm_core + ":" + dest_jar, 
            "com.iluwatar.urm.DomainMapperCli", "-p", "com.qxcode", 
            "-i", "com.qxcode.Solver,com.qxcode.Manual", 
            "-f", puml_file]
    subprocess.run(cmd)
    sort_classes(puml_file)
    if puml_only:
        shutil.copy(puml_file, 
                target_folder + os.sep + "diagrama.puml")
    else:
        cmd = ["plantuml", puml_file]
        subprocess.run(cmd)
        shutil.copy(folder + os.sep + "diagrama.png", 
                    target_folder + os.sep + "diagrama.png")


def main():
    parse = argparse.ArgumentParser()
    parse.addargument("urm-core", help="urm-core.jar path")
    parse.add_argument("target", help="file with all java classes")
    parse.add_argument("--puml", action='store_true', help="")
    args = parse.parse_args()
    target_full_path = os.path.abspath(args.target)
    target_folder = os.sep.join(target_full_path.split(os.sep)[:-1])
    content = open(args.target).read()
    folder = tempfile.mkdtemp()
    src_solver = build_project(folder, content)
    dest_jar = make_jar(folder, src_solver)
    make_png(folder, dest_jar, target_folder, args.puml)

    # cmd = "java -cp /home/tiger/dev/uml/urm-core.jar:qxcode.jar com.iluwatar.urm.DomainMapperCli -p com.qxcode -i com.qxcode.Solver,com.qxcode.Manual -f diagrama.puml"
    # subprocess.run(cmd.split(" "))
    # sort_classes("diagrama.puml")
if __name__ == '__main__':
    main()