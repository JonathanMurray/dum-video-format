from typing import BinaryIO, Tuple, List

from common import FrameType
from io_utils import bytes_to_int, read_rgb, Color, uint8_to_bytes, uint32_to_bytes, write_rgb

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


def write_color_mapped_frame(color_map: List[Color], file: BinaryIO, pixels: List[Color]):
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

    def read_bgr():
        rgb = read_rgb(file)
        return rgb[2], rgb[1], rgb[0]

    bgr_colormap = [read_bgr() for _ in range(num_colors)]
    buf = []
    color_indices = list(file.read(resolution[0] * resolution[1]))
    for color_index in color_indices:
        buf += bgr_colormap[color_index]
    return buf
