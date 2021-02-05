from color_quantization import rgb_to_uint15, uint15_to_rgb, rgb_to_uint7, uint7_to_rgb


def uint15_roundtrip(color):
    return uint15_to_rgb(rgb_to_uint15(color))


def uint7_rgb_roundtrip(color):
    return uint7_to_rgb(rgb_to_uint7(color))






def test_color_quantization_fits_in_uint15():
    assert rgb_to_uint15((255, 255, 255)) < 2 ** 16


def test_color_quantization_15():
    assert uint15_roundtrip((0, 0, 0)) == (4, 4, 4)
    assert uint15_roundtrip((255, 0, 0)) == (252, 4, 4)
    assert uint15_roundtrip((100, 100, 100)) == (100, 100, 100)
    assert uint15_roundtrip((75, 150, 225)) == (76, 148, 228)


def test_color_quantization_fits_in_uint7():
    assert rgb_to_uint7((255, 255, 255)) < 2 ** 7


def test_color_quantization_7():
    assert uint7_rgb_roundtrip((0, 0, 0)) == (16, 16, 16)
    assert uint7_rgb_roundtrip((255, 0, 0)) == (240, 16, 16)
    assert uint7_rgb_roundtrip((100, 100, 100)) == (112, 80, 80)
    assert uint7_rgb_roundtrip((75, 150, 225)) == (80, 144, 208)
