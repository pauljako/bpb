#!/usr/bin/env python3
import argparse
import os
import json
import sys
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
        print(f"{downloaded}MB/{size}MB ({percentage}%)", end="     \r")

def build(path: str, output: str, should_install: bool, should_compress: bool):
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
        
    if "web_sources" in information and isinstance(information["web_sources"], dict) and len(information["web_sources"]) > 0:
        for url, path in information["web_sources"].items():
            print(f"Downloading source {path} from {url}")
            urlretrieve(url, path, report_hook)
            if not os.path.exists(path):
                fail(f"Download of {path} failed")
                
    if "git_sources" in information and isinstance(information["git_sources"], dict) and len(information["git_sources"]) > 0:
        for url, path in information["git_sources"].items():
            print(f"Cloning {path} from {url}")
            os.system(f"git clone {url} {path}")
            if not os.path.exists(path):
                fail(f"Cloning of {path} failed")
                
    os.mkdir(os.path.join(file_path, "package"))
                
    print(f"Building {information['name']}")
    build_result = os.system(information["build"])
    if build_result != 0:
        fail("Build failed")
        
    print("Creating boundaries package")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="bpb", description="The boundaries package builder")
    parser.add_argument("--install", help="Install the package directly", action="store_true")
    parser.add_argument("--output", help="The path of the folder/archive to be created")
    parser.add_argument("--archive", help="Compress the output into a .tar.gz archive", action="store_true")
    parser.add_argument("path", help="The path to the archive or folder to build")
    
    args = parser.parse_args()
    
    build(path=args.path, output=args.output, should_install=args.install, should_compress=args.archive)