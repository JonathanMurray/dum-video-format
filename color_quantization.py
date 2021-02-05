from typing import List, Dict

from io_utils import Color


def uint15_to_rgb(n: int) -> Color:
    return (
        ((n & 0b0_11111_00000_00000) >> 7) + 4,
        ((n & 0b0_00000_11111_00000) >> 2) + 4,
        ((n & 0b0_00000_00000_11111) << 3) + 4,
    )


uint15_color_cache: List[Color] = [None] * (2 ** 16)


def uint15_to_bgr(n: int) -> Color:
    if not uint15_color_cache[n]:
        uint15_color_cache[n] = (
            ((n & 0b0_00000_00000_11111) << 3) + 4,
            ((n & 0b0_00000_11111_00000) >> 2) + 4,
            ((n & 0b0_11111_00000_00000) >> 7) + 4,
        )
    return uint15_color_cache[n]


color_uint15_cache: Dict[Color, int] = {}


# returns 2-byte int
def rgb_to_uint15(color: Color) -> int:
    # _ RRRRR GGGGG BBBBB
    if not color in color_uint15_cache:
        color_uint15_cache[color] = (color[0] >> 3 << 10) \
                                    + (color[1] >> 3 << 5) \
                                    + (color[2] >> 3)
    return color_uint15_cache[color]


def rgb_to_uint7(color: Color) -> int:
    # _ R R R G G B B
    return (color[0] >> 5 << 4) \
           + (color[1] >> 6 << 2) \
           + (color[2] >> 6)


def uint7_to_rgb(n: int) -> Color:
    return (
        ((n & 0b01110000) << 1) + 16,
        ((n & 0b00001100) << 4) + 16,
        ((n & 0b00000011) << 6) + 16,
    )


def uint7_to_bgr(n: int) -> Color:
    return (
        ((n & 0b00000011) << 6) + 16,
        ((n & 0b00001100) << 4) + 16,
        ((n & 0b01110000) << 1) + 16,
    )
