from io_utils import RGB

# 256 // 7 = 36
# 36 is the max-value of R, G and B when downsized. So we need 37 as a base when combining into int.
# 36 * 37^2 + 36 * 37 + 36 = 50_652 which fits in 2 bytes (65_536)
divisor_16 = 7
base_16 = 37

# 256 // 51 = 5
# 5 is the max-value of R, G and B when downsized. So we need 6 as a base when combining into int.
# 5 * 6^2 + 5 * 6 + 5 = 215 which fits in 1 byte (256)
divisor_8 = 51
base_8 = 6


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


def uint8_to_color(color_index: int) -> RGB:
    r = color_index // (base_8 ** 2)
    color_index -= r * base_8 ** 2
    g = color_index // base_8
    color_index -= g * base_8
    b = color_index
    return r * divisor_8, g * divisor_8, b * divisor_8


# returns 1-byte int
def color_to_uint8(color: RGB) -> int:
    (r, g, b) = color

    r //= divisor_8
    g //= divisor_8
    b //= divisor_8

    return r * base_8 ** 2 + g * base_8 + b
