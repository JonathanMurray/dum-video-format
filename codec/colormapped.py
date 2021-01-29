from typing import BinaryIO, Tuple, List

from common import FrameType
from io_utils import bytes_to_int, read_rgb, RGB, uint8_to_bytes, uint32_to_bytes, write_rgb

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


def write_color_mapped_frame(color_map: List[RGB], file: BinaryIO, pixels: List[RGB]):
    debug("Writing color-mapped frame")
    # Frame type
    file.write(uint8_to_bytes(FrameType.COLOR_MAPPED.value))
    # Frame size
    file.write(uint32_to_bytes(1 + len(color_map) * 3 + len(pixels)))
    file.write(uint8_to_bytes(len(color_map)))
    for key_color in color_map:
        write_rgb(file, key_color)
    for i, pixel in enumerate(pixels):
        file.write(uint8_to_bytes(color_map.index(pixel)))


def read_color_mapped_frame(file: BinaryIO, resolution: Tuple[int, int]) -> List[int]:
    debug("Reading color-mapped frame...")
    num_colors = bytes_to_int(file.read(1))
    color_map = [read_rgb(file) for _ in range(num_colors)]
    buf = []
    for i in range(resolution[0] * resolution[1]):
        color_index = bytes_to_int(file.read(1))
        color = color_map[color_index]
        buf.append(color[0])
        buf.append(color[1])
        buf.append(color[2])
    return buf

