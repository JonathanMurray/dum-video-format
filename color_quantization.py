from io_utils import RGB


def uint15_to_color(n: int) -> RGB:
    return (
        (n & 0b0_11111_00000_00000) >> 7,
        (n & 0b0_00000_11111_00000) >> 2,
        (n & 0b0_00000_00000_11111) << 3
    )


# returns 2-byte int
def color_to_uint15(color: RGB) -> int:
    # _ RRRRR GGGGG BBBBB
    return (color[0] >> 3 << 10) \
           + (color[1] >> 3 << 5) \
           + (color[2] >> 3)


def color_to_uint7(color: RGB) -> int:
    # _ R R R G G B B
    return (color[0] >> 5 << 4) \
           + (color[1] >> 6 << 2) \
           + (color[2] >> 6)


def uint7_to_color(n: int) -> RGB:
    return (
        (n & 0b01110000) << 1,
        (n & 0b00001100) << 4,
        (n & 0b00000011) << 6
    )
