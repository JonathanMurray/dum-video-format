from color_quantization import color_to_uint16, uint16_to_color, color_to_uint8, uint8_to_color


def test_color_quantization_fits_in_uint16():
    assert color_to_uint16((255, 255, 255)) < 2 ** 16


def test_color_quantization_fits_in_uint8():
    assert color_to_uint8((255, 255, 255)) < 2 ** 8


def test_color_quantization_16():
    assert uint16_roundtrip((0, 0, 0)) == (0, 0, 0)
    assert uint16_roundtrip((255, 0, 0)) == (252, 0, 0)
    assert uint16_roundtrip((100, 100, 100)) == (98, 98, 98)
    assert uint16_roundtrip((75, 150, 225)) == (70, 147, 224)


def test_color_quantization_8():
    assert uint8_roundtrip((0, 0, 0)) == (0, 0, 0)
    assert uint8_roundtrip((255, 0, 0)) == (255, 0, 0)
    assert uint8_roundtrip((100, 100, 100)) == (51, 51, 51)
    assert uint8_roundtrip((75, 150, 225)) == (51, 102, 204)


def uint16_roundtrip(color):
    return uint16_to_color(color_to_uint16(color))


def uint8_roundtrip(color):
    return uint8_to_color(color_to_uint8(color))
