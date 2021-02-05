from io import BytesIO
from time import time

from format import write_frame, Quality, Decoder
from header import DumInfo


def test_write_read_large_frame():
    file = BytesIO()
    pixels = []
    w = 1000
    h = 1000
    for y in range(h):
        for x in range(w):
            pixels.append((x % 255, ((x * y) + 1) % 255, ((x * y) + 2) % 255))
    start = time()
    write_frame(file, pixels, Quality.MEDIUM)
    print(f"It took {round(time() - start, 2)}s to write frame")

    file_size = file.tell()
    file.seek(0)

    decoder = Decoder(file, DumInfo(1, w, h, 1, 1, 1, 0, file_size))

    start = time()
    decoder.read_frame()
    print(f"It took {round(time() - start, 2)}s to read frame")
