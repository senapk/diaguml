#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import tempfile
import os
import shutil
import subprocess
from typing import List


#urm_core = "/home/tiger/dev/uml/urm-core.jar"

class Mount:
    def __init__(self):
        self.atributes = []
        self.private = []
        self.public = []
        self.protected = []
        self.getsets = []
        self.toString = False

    def add(self, line):
        if line.startswith("    ") and not "(" in line:
            self.atributes.append(line)
            return True
        elif "toString" in line:
            self.toString = True
            return True
        elif line.startswith("    ~ get") or line.startswith("    + get") or line.startswith("    ~ set") or line.startswith("    + set"):
            line = line.replace("    ~", "    +")
            self.getsets.append(line)
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
        self.getsets.clear();

    def process(self):
        if self.toString:
            self.public.append("    + toString() : String")
        self.atributes = sorted(self.atributes)
        mount = [self.atributes] + [self.private] + [self.public] + [self.getsets] + [self.protected]
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


def build_project(temp_folder, content):
    os.mkdir(temp_folder + os.sep + "build")
    src_path = [temp_folder, "src", "com", "qxcode"]
    for i in range(1, len(src_path)):
        os.mkdir(os.sep.join(src_path[0:(i + 1)]))
    src_solver = os.sep.join(src_path + ["Solver.java"])
    with open(temp_folder + os.sep + "myManifest", "w") as f:
        f.write("Main-Class: com.qxcode.Solver\n")
    with open(src_solver, "w") as f:
        f.write("package com.qxcode;\n" + content)
    return src_solver

def make_jar(temp_folder, src_solver):
    cmd = ["javac", "-g", "-sourcepath", 
            temp_folder + os.sep + "src", "-d", 
            temp_folder + os.sep + "build", src_solver]
    subprocess.run(cmd)
    dest_jar = temp_folder + os.sep + "qxcode.jar"
    cmd = ["jar", "cfm", dest_jar, 
            temp_folder + os.sep + "myManifest", "-C", 
            temp_folder + os.sep + "build", "."]
    subprocess.run(cmd)
    print(temp_folder)
    return dest_jar

def make_puml(temp_folder, dest_jar, urmcore):
    puml_file = temp_folder + os.sep + "diagrama.puml"
    cmd = ["java", "-cp", 
            urmcore + ":" + dest_jar, 
            "com.iluwatar.urm.DomainMapperCli", "-p", "com.qxcode", 
            "-i", "com.qxcode.Solver,com.qxcode.Manual", 
            "-f", puml_file]
    subprocess.run(cmd)
    return puml_file


    # sort_classes(puml_file)
    # if puml_only:
    #     shutil.copy(puml_file, 
    #             target_folder + os.sep + "diagrama.puml")

def make_image(puml_file, temp_folder, target_folder):
        cmd = ["plantuml", puml_file]
        subprocess.run(cmd)
        shutil.copy(temp_folder + os.sep + "diagrama.png", target_folder + os.sep + "diagrama.png")


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("urmcore", help="urm-core.jar path")
    parse.add_argument("target", help="file with java classes")
    parse.add_argument("--puml", "-p", action='store_true', help="generate puml file")
    parse.add_argument("--sort", "-s", action='store_true', help="sort puml using access modifiers")
    parse.add_argument("--image", "-i", action='store_true', help="make png image from puml")
    args = parse.parse_args()
    target_full_path = os.path.abspath(args.target)
    target_folder = os.sep.join(target_full_path.split(os.sep)[:-1])
    content = open(args.target).read()
    temp_folder = tempfile.mkdtemp()

    src_solver = build_project(temp_folder, content)
    
    dest_jar = make_jar(temp_folder, src_solver)
    
    puml_file = make_puml(temp_folder, dest_jar, args.urmcore)
    
    if args.sort:
        sort_classes(puml_file)

    if args.puml:
        shutil.copy(puml_file, target_folder + os.sep + "diagrama.puml")
    
    if args.image:
        make_image(puml_file, temp_folder, target_folder)

    # cmd = "java -cp /home/tiger/dev/uml/urm-core.jar:qxcode.jar com.iluwatar.urm.DomainMapperCli -p com.qxcode -i com.qxcode.Solver,com.qxcode.Manual -f diagrama.puml"
    # subprocess.run(cmd.split(" "))
    # sort_classes("diagrama.puml")
if __name__ == '__main__':
    main()