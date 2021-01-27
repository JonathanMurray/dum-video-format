#!/usr/bin/env python3
import sys

import pygame

from format import write_header, write_frame, Quality


def convert_image(source_path: str, target_path: str, quality: Quality):
    surface = pygame.image.load(source_path)
    frame = []
    w = surface.get_width()
    h = surface.get_height()
    for y in range(h):
        for x in range(w):
            pixel = surface.get_at((x, y))
            frame.append((pixel[0], pixel[1], pixel[2]))
    with open(target_path, "wb") as target_file:
        write_header(target_file, frame_rate=1, resolution=(w, h), scaling=(1, 1), num_frames=1)
        write_frame(target_file, frame, quality)


def main():
    args = sys.argv[1:]
    if len(args) not in [2, 3]:
        print(f"Usage: {sys.argv[0]} SOURCEFILE TARGETFILE [QUALITY]")
        return
    source_path = args[0]
    target_path = args[1]
    quality = Quality[args[2]] if len(args) == 3 else Quality.LOSSLESS
    convert_image(source_path, target_path, quality)


if __name__ == '__main__':
    main()
