#!/usr/bin/env python3
import sys
from random import randint
from typing import List

from format import write_header, write_frame, Quality
from io_utils import RGB

content = [
    "",
    " X   X   XXXXX   X       X       XXXXX      W           W   XXXXX   XXXX    X       XXXX            ",
    " X   X   X       X       X       X   X       W         W    X   X   X   X   X       X   X           ",
    " XXXXX   XXXXX   X       X       X   X        W   W   W     X   X   XXXX    X       X   X           ",
    " X   X   X       X       X       X   X         W W W W      X   X   X  X    X       X   X           ",
    " X   X   XXXXX   XXXXX   XXXXX   XXXXX          W   W       XXXXX   X   X   XXXXX   XXXX            ",
    "",
]

CONTENT_WIDTH = max([len(line) for line in content])
WIDTH = 50
HEIGHT = len(content)


def create_file(path: str):
    with open(path, "wb") as file:

        num_frames = 100
        write_header(file, frame_rate=30, resolution=(WIDTH, HEIGHT), scaling=(16, 20), num_frames=num_frames)

        for frame in range(num_frames):
            frame_pixels: List[RGB] = []
            for y, line in enumerate(content):
                for x in range(WIDTH):
                    xx = (x + frame) % CONTENT_WIDTH
                    if xx < len(line) and line[xx] != ' ':
                        if xx < 40:
                            # Color for HELLO
                            frame_pixels.append((randint(150, 255), randint(100, 150), randint(0, 150)))
                        else:
                            # Color for WORLD
                            frame_pixels.append((randint(0, 150), randint(100, 150), randint(150, 255)))
                    else:
                        if xx % 2 == 0 and y % 2 == 0:
                            frame_pixels.append((randint(25, 50), randint(25, 50), randint(25, 50)))
                        else:
                            frame_pixels.append((randint(40, 60), randint(40, 60), randint(40, 60)))
            write_frame(file, frame_pixels, Quality.LOW)


def main():
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} FILE")
        return
    create_file(args[0])


if __name__ == '__main__':
    main()
