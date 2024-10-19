#!/usr/bin/env python3
import argparse
import os
import json
import sys

def fail(reason: str):
    print("\033[91m"+ "A critical error occoured:" + "\033[0m")
    print(reason)
    sys.exit(1)


def build(path: str, output: str, should_install: bool, should_compress: bool):
    file_path = os.path.realpath(os.path.join(os.getcwd(), path))
    if not os.path.exists(file_path):
        fail(f"Path not existing: {file_path}")
    if not os.path.isdir(file_path):
        fail(f"Not a directory: {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="bpb", description="The boundaries package builder")
    parser.add_argument("--install", help="Install the package directly", action="store_true")
    parser.add_argument("--output", help="The path of the folder/archive to be created")
    parser.add_argument("--archive", help="Compress the output into a .tar.gz archive", action="store_true")
    parser.add_argument("path", help="The path to the archive or folder to build")
    
    args = parser.parse_args()
    
    build(path=args.path, output=args.output, should_install=args.install, should_compress=args.archive)