from io import BytesIO

from format import Decoder, write_frame, _read_frame, write_8bit_quantized_frame
from header import write_header, DumInfo


def test_write_header():
    io = BytesIO()
    write_header(io, frame_rate=10, resolution=(20, 32), scaling=(40, 50), num_frames=60)


def test_write_and_read_header():
    io = BytesIO()
    write_header(io, 10, (20, 32), (40, 50), 60)
    decoder = Decoder(io)
    decoder.read_header()
    assert decoder.info == DumInfo(frame_rate=10, width=20, height=32, hor_scaling=40, ver_scaling=50,
                                   num_frames=60, header_size=15, file_size=15)


def test_write_full_file():
    io = BytesIO()
    write_header(io, frame_rate=1, resolution=(4, 4), scaling=(4, 5), num_frames=2)
    write_frame(io, [(0, 0, 0), (100, 100, 100)] + [(0, 0, 0)] * 14)
    write_frame(io, [(150, 150, 150), (250, 250, 250)] + [(0, 0, 0)] * 14)


def test_write_and_read_full_file():
    io = BytesIO()
    write_header(io, frame_rate=1, resolution=(4, 4), scaling=(4, 5), num_frames=2)
    write_frame(io, [(0, 0, 0), (100, 100, 100)] + [(0, 0, 0)] * 14)
    write_frame(io, [(150, 150, 150), (250, 250, 250)] + [(0, 0, 0)] * 14)
    decoder = Decoder(io)

    decoder.read_header()
    assert decoder.info == DumInfo(frame_rate=1, width=4, height=4, hor_scaling=4, ver_scaling=5,
                                   num_frames=2, header_size=15, file_size=74)
    assert decoder.read_frame() == [0, 0, 0, 100, 100, 100] + [0, 0, 0] * 14
    assert decoder.read_frame() == [150, 150, 150, 250, 250, 250] + [0, 0, 0] * 14


def test_run_length_frame():
    io = BytesIO()
    pixels = [(255, 255, 255)] * 100
    write_8bit_quantized_frame(io, pixels)
    assert list(io.getbuffer()) == [
        4,  # frame type
        0, 0, 0, 2,  # frame size = 2 bytes
        0b01111111,  # "white" encoded as 1 byte
        0b10000000 + 99,  # repeated 99 additional times
    ]


def test_write_and_read_run_length_frame():
    io = BytesIO()
    w = 100
    h = 100
    pixels = []
    for i in range(100):
        pixels.append((0, 80, 130))
    for i in range(9900):
        pixels.append((150, 200, 255))
    write_8bit_quantized_frame(io, pixels)

    io.seek(0)

    decoded_pixels = _read_frame(io, (w, h))

    assert decoded_pixels[:300] == [144, 80, 16] * 100
    assert decoded_pixels[300:] == [208, 208, 144] * 9900
