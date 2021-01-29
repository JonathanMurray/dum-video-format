#!/usr/bin/env python3
import sys

import pygame

from format import write_frame, Quality
from header import write_header
from pygame_utils import get_surface_pixels


def convert_image(source_path: str, target_path: str, quality: Quality):
    surface = pygame.image.load(source_path)
    pixels = list(get_surface_pixels(surface))
    with open(target_path, "wb") as target_file:
        resolution = (surface.get_width(), surface.get_height())
        write_header(target_file, frame_rate=1, resolution=resolution, scaling=(1, 1), num_frames=1)
        write_frame(target_file, pixels, quality)


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
