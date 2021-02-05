#!/usr/bin/env python3
import sys

from common import FrameType
from format import Decoder
from header import read_header


def parse_file(path: str):
    with open(path, "rb") as file:
        info = read_header(file)
        decoder = Decoder(file, info)
        print(f"{info}")
        for _ in range(info.num_frames):
            frame_type, frame_size = decoder.skip_frame()
            print(f"{FrameType(frame_type)} ({frame_size}B)")
        print(f"Seeked through all {info.num_frames} frames.")


def main():
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} FILE")
        return
    parse_file(args[0])


if __name__ == '__main__':
    main()
