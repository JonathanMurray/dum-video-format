#!/usr/bin/env python3
import sys
from dataclasses import dataclass
from typing import BinaryIO

from io_utils import bytes_to_int


@dataclass
class DumInfo:
    frame_rate: int
    width: int
    height: int
    hor_scaling: int
    ver_scaling: int
    header_size: int
    num_frames: int
    file_size: int


def parse_file(path: str):
    with open(path, "rb") as file:
        header = parse_header(file)
        print(f"{header}")


def parse_header(file: BinaryIO) -> DumInfo:
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0, 0)

    header_size = 0

    magic_string = file.read(3)
    if magic_string != b'dum':
        raise Exception(f"Invalid DUM file! Expected magic string 'dum' but found {magic_string}.")

    header_size += 3

    def read_int() -> int:
        nonlocal header_size
        n = bytes_to_int(file.read(4))
        header_size += 4
        return n

    frame_rate = read_int()
    width = read_int()
    height = read_int()
    hor_scaling = read_int()
    ver_scaling = read_int()

    remaining_bytes = file_size - header_size
    num_frames = int(remaining_bytes / width / height / 3)

    return DumInfo(frame_rate, width, height, hor_scaling, ver_scaling, header_size, num_frames, file_size)


def main():
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} FILE")
        return
    parse_file(args[0])


if __name__ == '__main__':
    main()
