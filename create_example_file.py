#!/usr/bin/env python3
import sys
from random import randint

from format import write_header

content = [
    "",
    " X   X   XXXXX   X       X       XXXXX      W           W   XXXXX   XXXX    X       XXXX   ",
    " X   X   X       X       X       X   X       W         W    X   X   X   X   X       X   X  ",
    " XXXXX   XXXXX   X       X       X   X        W   W   W     X   X   XXXX    X       X   X  ",
    " X   X   X       X       X       X   X         W W W W      X   X   X  X    X       X   X  ",
    " X   X   XXXXX   XXXXX   XXXXX   XXXXX          W   W       XXXXX   X   X   XXXXX   XXXX   ",
    "",
]

WIDTH = max([len(line) for line in content])
HEIGHT = len(content)


def create_file(path: str):
    with open(path, "wb") as file:

        write_header(file, frame_rate=10, resolution=(WIDTH, HEIGHT), scaling=(8, 10))

        num_frames = 50
        for _ in range(num_frames):
            for line in content:
                for x in range(WIDTH):
                    if x < len(line) and line[x] != ' ':
                        r = randint(100, 255)
                        file.write(r.to_bytes(1, byteorder="big"))
                        g = randint(50, 200)
                        file.write(g.to_bytes(1, byteorder="big"))
                        b = randint(0, 150)
                        file.write(b.to_bytes(1, byteorder="big"))
                    else:
                        file.write(b'\x00\x00\x00')


def main():
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} FILE")
        return
    create_file(args[0])


if __name__ == '__main__':
    main()
