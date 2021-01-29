from color_quantization import color_to_uint15, uint15_to_color, color_to_uint7, uint7_to_color


def uint15_roundtrip(color):
    return uint15_to_color(color_to_uint15(color))


def uint7_roundtrip(color):
    return uint7_to_color(color_to_uint7(color))


def test_color_quantization_fits_in_uint15():
    assert color_to_uint15((255, 255, 255)) < 2 ** 16


def test_color_quantization_15():
    assert uint15_roundtrip((0, 0, 0)) == (0, 0, 0)
    assert uint15_roundtrip((255, 0, 0)) == (248, 0, 0)
    assert uint15_roundtrip((100, 100, 100)) == (96, 96, 96)
    assert uint15_roundtrip((75, 150, 225)) == (72, 144, 224)


def test_color_quantization_fits_in_uint7():
    assert color_to_uint7((255, 255, 255)) < 2 ** 7


def test_color_quantization_7():
    assert uint7_roundtrip((0, 0, 0)) == (0, 0, 0)
    assert uint7_roundtrip((255, 0, 0)) == (224, 0, 0)
    assert uint7_roundtrip((100, 100, 100)) == (96, 64, 64)
    assert uint7_roundtrip((75, 150, 225)) == (64, 128, 192)
