#!/usr/bin/env python3

from format import write_frame, Quality
from header import write_header

WIDTH = 20
HEIGHT = 20

PIXELS = {
    "red": [(255-i, 0, 10) for i in range(WIDTH * HEIGHT // 2)] +
           [(255 - (WIDTH * HEIGHT // 2) - 1 + i, 10, 0) for i in range(WIDTH * HEIGHT // 2)],
    "green": [(0, 255 - i, 10) for i in range(WIDTH * HEIGHT // 2)] +
             [(10, 255 - (WIDTH * HEIGHT // 2) - 1 + i, 0) for i in range(WIDTH * HEIGHT // 2)],
    "blue": [(0, 10, 255 - i) for i in range(WIDTH * HEIGHT // 2)] +
            [(10, 0, 255 - (WIDTH * HEIGHT // 2) - 1 + i) for i in range(WIDTH * HEIGHT // 2)],
}

QUALITIES = {
    "low": Quality.LOW,
    "medium": Quality.MEDIUM,
    "lossless": Quality.LOSSLESS
}


def create_files():
    for color_name, pixels in PIXELS.items():
        for quality_name, quality in QUALITIES.items():
            with open(f"samples/{color_name}_{quality_name}.dum", "wb") as file:
                write_header(file, frame_rate=30, resolution=(WIDTH, HEIGHT), scaling=(32, 32), num_frames=1)
                write_frame(file, pixels, quality)


def main():
    create_files()


if __name__ == '__main__':
    main()
