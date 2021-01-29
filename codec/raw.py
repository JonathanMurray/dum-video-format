from typing import BinaryIO, List, Tuple

from common import FrameType
from io_utils import RGB, uint8_to_bytes, uint32_to_bytes, write_rgb

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


def write_raw_frame(file: BinaryIO, pixels: List[RGB]):
    debug("Writing raw frame")
    # Frame type
    file.write(uint8_to_bytes(FrameType.RAW.value))
    # Frame size
    file.write(uint32_to_bytes(len(pixels) * 3))
    for pixel in pixels:
        write_rgb(file, pixel)


def read_raw_frame(file: BinaryIO, frame_size: int) -> List[int]:
    debug("Reading raw frame...")
    buf = file.read(frame_size)
    if len(buf) < frame_size:
        print(f"WARN: Read {len(buf)} bytes - not enough for a full frame!")
    return list(buf)
