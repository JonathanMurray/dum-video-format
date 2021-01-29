from io_utils import RGB

# 256 // 7 = 36
# 36 is the max-value of R, G and B when downsized. So we need 37 as a base when combining into int.
# 36 * 37^2 + 36 * 37 + 36 = 50_652 which fits in 2 bytes (65_536)
divisor_16 = 7
base_16 = 37


def uint16_to_color(color_index: int) -> RGB:
    r = color_index // (base_16 ** 2)
    color_index -= r * base_16 ** 2
    g = color_index // base_16
    color_index -= g * base_16
    b = color_index
    return r * divisor_16, g * divisor_16, b * divisor_16


# returns 2-byte int
def color_to_uint16(color: RGB) -> int:
    (r, g, b) = color

    r //= divisor_16
    g //= divisor_16
    b //= divisor_16

    return r * base_16 ** 2 + g * base_16 + b


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
