#!/usr/bin/env python3
import sys

from format import parse_header


def parse_file(path: str):
    with open(path, "rb") as file:
        header = parse_header(file)
        print(f"{header}")


def main():
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} FILE")
        return
    parse_file(args[0])


if __name__ == '__main__':
    main()
