from typing import BinaryIO

from common import FrameType
from io_utils import uint8_to_bytes, uint32_to_bytes

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


def write_repeated_frame(file: BinaryIO):
    debug("Writing repeated frame")
    # Frame type
    file.write(uint8_to_bytes(FrameType.REPEATED.value))
    # Frame size
    file.write(uint32_to_bytes(0))
