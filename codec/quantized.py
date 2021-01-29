from typing import Tuple, Callable, List, BinaryIO

from color_quantization import color_to_uint7, color_to_uint15, uint15_to_color, uint7_to_color
from common import FrameType
from io_utils import RGB, bytes_to_int
from io_utils import uint8_to_bytes, uint32_to_bytes, uint16_to_bytes

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


def write_8bit_quantized_frame(file: BinaryIO, pixels: List[RGB]):
    debug("Writing 8-bit quantized frame")
    _write_quantized_frame(file, pixels, quantize_color=color_to_uint7, max_run_length=127, bitsize=8,
                           to_bytes=uint8_to_bytes, frame_type=FrameType.QUANTIZED_TO_8_BIT)


def write_16bit_quantized_frame(file: BinaryIO, pixels: List[RGB]):
    debug("Writing 16-bit quantized frame")
    _write_quantized_frame(file, pixels, quantize_color=color_to_uint15, max_run_length=32_767, bitsize=16,
                           to_bytes=uint16_to_bytes, frame_type=FrameType.QUANTIZED_TO_16_BIT)


def _write_quantized_frame(file: BinaryIO, pixels: List[RGB], quantize_color: Callable[[RGB], int], max_run_length: int,
    bitsize: int, to_bytes: Callable[[int], bytes], frame_type: FrameType):
    file.write(uint8_to_bytes(frame_type.value))
    # Frame size is written at the end
    frame_size_offset = file.tell()
    file.write(uint32_to_bytes(0))
    frame_content_offset = file.tell()
    quantized_pixels = [quantize_color(p) for p in pixels]
    run_length_pixel = None
    accumulated_run_length = 0
    for p in quantized_pixels:
        if p != run_length_pixel or accumulated_run_length == max_run_length:
            if accumulated_run_length:
                debug(f"Writing accumulated run-length: {accumulated_run_length}, color {run_length_pixel}")
                file.write(to_bytes((1 << (bitsize - 1)) + accumulated_run_length))
            file.write(to_bytes(p))
            run_length_pixel = p
            accumulated_run_length = 0
        else:
            # Same pixel as last one => start counting
            accumulated_run_length += 1
    if accumulated_run_length:
        debug(f"Writing last accumulated run-length: {accumulated_run_length}, color {run_length_pixel}")
        file.write(to_bytes((1 << (bitsize - 1)) + accumulated_run_length))
    frame_size = file.tell() - frame_content_offset
    file.seek(frame_size_offset)
    file.write(uint32_to_bytes(frame_size))
    file.seek(0, 2)


def read_16bit_quantized_frame(file: BinaryIO, resolution: Tuple[int, int]):
    debug("Reading 16-bit quantized frame...")
    return read_quantized_frame(resolution, read_quantized_pixel=lambda: bytes_to_int(file.read(2)),
                                decode_pixel=uint15_to_color, flag_bitmask=0b10000000_00000000,
                                run_length_bitmask=0b01111111_11111111)


def read_8bit_quantized_frame(file: BinaryIO, resolution: Tuple[int, int]):
    debug("Reading 8-bit quantized frame...")
    return read_quantized_frame(resolution, read_quantized_pixel=lambda: bytes_to_int(file.read(1)),
                                decode_pixel=uint7_to_color, flag_bitmask=0b10000000,
                                run_length_bitmask=0b01111111)


def read_quantized_frame(resolution: Tuple[int, int], read_quantized_pixel: Callable[[], int],
    decode_pixel: Callable[[int], RGB], flag_bitmask: int, run_length_bitmask: int) -> List[int]:
    buf = []
    color = None
    while len(buf) < resolution[0] * resolution[1] * 3:
        q = read_quantized_pixel()
        if not q & flag_bitmask:
            color = decode_pixel(q)
            buf += color
        else:
            run_length = q & run_length_bitmask
            buf += color * run_length
    return buf
