from io import BytesIO
from time import time

from format import write_frame, Quality, _read_frame


def test_write_read_large_frame():
    file = BytesIO()
    pixels = []
    w = 1000
    h = 1000
    for y in range(h):
        for x in range(w):
            pixels.append((x % 255, ((x * y) + 1) % 255, ((x * y) + 2) % 255))
    start = time()
    write_frame(file, pixels, Quality.LOSSLESS)
    print(f"It took {round(time() - start, 2)}s to write frame")

    file.seek(0)

    start = time()
    _read_frame(file, (w, h))
    print(f"It took {round(time() - start, 2)}s to read frame")
