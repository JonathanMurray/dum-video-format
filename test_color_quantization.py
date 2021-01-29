from color_quantization import color_to_uint16, uint16_to_color, color_to_uint7, uint7_to_color


def uint16_roundtrip(color):
    return uint16_to_color(color_to_uint16(color))


def uint7_roundtrip(color):
    return uint7_to_color(color_to_uint7(color))


def test_color_quantization_fits_in_uint16():
    assert color_to_uint16((255, 255, 255)) < 2 ** 16


def test_color_quantization_16():
    assert uint16_roundtrip((0, 0, 0)) == (0, 0, 0)
    assert uint16_roundtrip((255, 0, 0)) == (252, 0, 0)
    assert uint16_roundtrip((100, 100, 100)) == (98, 98, 98)
    assert uint16_roundtrip((75, 150, 225)) == (70, 147, 224)


def test_color_quantization_fits_in_uint7():
    assert color_to_uint7((255, 255, 255)) < 2 ** 7


def test_color_quantization_7():
    assert uint7_roundtrip((0, 0, 0)) == (0, 0, 0)
    assert uint7_roundtrip((255, 0, 0)) == (224, 0, 0)
    assert uint7_roundtrip((100, 100, 100)) == (96, 64, 64)
    assert uint7_roundtrip((75, 150, 225)) == (64, 128, 192)
