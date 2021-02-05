import struct
from typing import Callable, List, BinaryIO

from color_quantization import rgb_to_uint7, rgb_to_uint15, uint7_to_bgr, \
    uint15_to_bgr
from common import FrameType
from io_utils import Color
from io_utils import uint8_to_bytes, uint32_to_bytes, uint16_to_bytes

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


def write_8bit_quantized_frame(file: BinaryIO, pixels: List[Color]):
    debug("Writing 8-bit quantized frame")
    _write_quantized_frame(file, pixels, quantize_color=rgb_to_uint7, max_run_length=127, bitsize=8,
                           to_bytes=uint8_to_bytes, frame_type=FrameType.QUANTIZED_TO_8_BIT)


def write_16bit_quantized_frame(file: BinaryIO, pixels: List[Color]):
    debug("Writing 16-bit quantized frame")
    _write_quantized_frame(file, pixels, quantize_color=rgb_to_uint15, max_run_length=32_767, bitsize=16,
                           to_bytes=uint16_to_bytes, frame_type=FrameType.QUANTIZED_TO_16_BIT)


def _write_quantized_frame(file: BinaryIO, pixels: List[Color], quantize_color: Callable[[Color], int],
    max_run_length: int,
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


def read_16bit_quantized_frame(file: BinaryIO, frame_size: int):
    debug("Reading 16-bit quantized frame...")
    format = f">{frame_size // 2}H"
    read_pixels = list(struct.unpack(format, file.read(frame_size)))
    return _read_quantized_frame(decode_pixel=uint15_to_bgr, flag_bitmask=0b10000000_00000000,
                                 run_length_bitmask=0b01111111_11111111, read_pixels=read_pixels)


def read_8bit_quantized_frame(file: BinaryIO, frame_size: int):
    debug("Reading 8-bit quantized frame...")
    read_pixels = list(file.read(frame_size))
    return _read_quantized_frame(decode_pixel=uint7_to_bgr, flag_bitmask=0b10000000,
                                 run_length_bitmask=0b01111111, read_pixels=read_pixels)


def _read_quantized_frame(decode_pixel: Callable[[int], Color], flag_bitmask: int, run_length_bitmask: int,
    read_pixels: List[int]) -> List[int]:
    buf = []
    color = None
    for i, q in enumerate(read_pixels):
        if not q & flag_bitmask:
            color = decode_pixel(q)
            buf += color
        else:
            run_length = q & run_length_bitmask
            buf += color * run_length
    return buf
