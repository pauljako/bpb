#!/usr/bin/env python3
import argparse
import os
import json
import sys
import shutil
import tarfile
import boundaries
from urllib.request import urlretrieve

def fail(reason: str):
    print("\033[91m"+ "A critical error occoured:" + "\033[0m")
    print("=> " + reason)
    sys.exit(1)

def report_hook(block_count, block_size, file_size):
    downloaded = block_count * block_size
    percentage = round(downloaded / file_size * 100)
    if percentage > 100:
        percentage = 100
    downloaded = round(downloaded / 1000000, 1)
    size = round(file_size / 1000000, 1)
    if downloaded > size:
        downloaded = size
    print(f"=> {downloaded}MB/{size}MB ({percentage}%)", end="     \r")

def build(path: str, output: str | None, should_install: bool, should_compress: bool):
    file_path = os.path.realpath(os.path.join(os.getcwd(), path))
    
    if not os.path.exists(file_path):
        fail(f"Path not existing: {file_path}")
    if not os.path.isdir(file_path):
        fail(f"Not a directory: {file_path}")
    if (not os.path.exists(os.path.join(file_path, "bpb.json"))) or (not os.path.isfile(os.path.join(file_path, "bpb.json"))):
        fail("Could not find the bpb.json file")
        
    os.chdir(file_path)
    
    with open(os.path.join(file_path, "bpb.json"), "rb") as f:
        information = json.load(f)
        
    if not "name" in information:
        fail("The bpb.json file does not contain the 'name' field")
    if not "version" in information:
        fail("The bpb.json file does not contain the 'version' field")
    if not "build" in information:
        fail("The bpb.json file does not contain the 'build' field")
    if not "json_file" in information:
        fail("The bpb.json file does not contain the 'json_file' field")
        
    if "dependencies" in information:
        if "build_packages" in information["dependencies"]:
            for package in information["dependencies"]["build_packages"]:
                if not package in boundaries.get_packages():
                    fail(f"The boundaries package {package} could not be found and is a build dependency")
        if "build_commands" in information["dependencies"]:
            for command in information["dependencies"]["build_commands"]:
                if shutil.which(command) is None:
                    fail(f"The command {command} could not be found and is a build dependency")
        
    if "web_sources" in information and isinstance(information["web_sources"], dict) and len(information["web_sources"]) > 0:
        for org_url, org_path in information["web_sources"].items():
            url = org_url.replace("$PKG_VERSION", information["version"])
            path = org_path.replace("$PKG_VERSION", information["version"])
            print(f"Downloading source {path} from {url}")
            urlretrieve(url, path, report_hook)
            print("")
            if not os.path.exists(path):
                fail(f"Download of {path} failed")
                
    if "git_sources" in information and isinstance(information["git_sources"], dict) and len(information["git_sources"]) > 0:
        for org_url, org_path in information["git_sources"].items():
            url = org_url.replace("$PKG_VERSION", information["version"])
            path = org_path.replace("$PKG_VERSION", information["version"])
            print(f"Cloning {path} from {url}")
            os.system(f"git clone {url} {path}")
            if not os.path.exists(path):
                fail(f"Cloning of {path} failed")
                
    if os.path.exists(os.path.join(file_path, "package")):
        shutil.rmtree(os.path.join(file_path, "package"))
    os.mkdir(os.path.join(file_path, "package"))
                
    print(f"Building {information['name']}")
    build_result = os.system(f"PKG_NAME={information['name']} PKG_VERSION={information['version']} {information['build']}")
    if build_result != 0:
        fail("Build failed")
        
    print("Creating boundaries package")
    os.chdir(os.path.join(file_path, "package"))
    json_file = information["json_file"]
    json_file["name"] = information["name"]
    json_file["version"] = information["version"]
    
    with open("boundaries.json", "wt") as f:
        json.dump(json_file, f)
        
    os.chdir(file_path)
    
    if should_install:
        print("Installing package")
        boundaries.install("package")
    
    if output and not should_compress:
        if os.path.exists(os.path.join(file_path, output)):
            shutil.rmtree(os.path.join(file_path, output))
        shutil.move(os.path.join(file_path, "package"), os.path.join(file_path, output))
    elif output and should_compress:
        print("Compressing package")
        with tarfile.open(output, "w:gz") as tar:
            tar.add("package")
        shutil.rmtree("package")
    elif should_compress:
        print("Compressing package")
        with tarfile.open("package.tar.gz", "w:gz") as tar:
            tar.add("package")
        shutil.rmtree("package")
        
    print("\033[92m" + "Done! Package built" + "\033[0m")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="bpb", description="The boundaries package builder")
    parser.add_argument("--install", "-i", help="Install the package directly", action="store_true")
    parser.add_argument("--output", "-o", help="The path of the folder/archive to be created", default=None)
    parser.add_argument("--archive", "-a", help="Compress the output into a .tar.gz archive", action="store_true")
    parser.add_argument("path", help="The path to the archive or folder to build")
    
    args = parser.parse_args()
    
    build(path=args.path, output=args.output, should_install=args.install, should_compress=args.archive)
