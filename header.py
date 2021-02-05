from dataclasses import dataclass
from typing import BinaryIO, Tuple

from io_utils import uint8_to_bytes, uint16_to_bytes, uint32_to_bytes, bytes_to_int


@dataclass
class DumInfo:
    frame_rate: int
    width: int
    height: int
    hor_scaling: int
    ver_scaling: int
    num_frames: int
    header_size: int
    file_size: int


def write_header(file: BinaryIO, frame_rate: int, resolution: Tuple[int, int], scaling: Tuple[int, int],
    num_frames: int):

    if resolution[0] % 4 != 0 or resolution[1] % 4 != 0:
        raise ValueError(f"Width and height must be multiples of 4! (Got: {resolution})")

    # magic string
    file.write(b'dumv')
    file.write(uint8_to_bytes(frame_rate))

    # width
    file.write(uint16_to_bytes(resolution[0]))

    # height
    file.write(uint16_to_bytes(resolution[1]))

    # horizontal scale
    file.write(uint8_to_bytes(scaling[0]))

    # vertical scale
    file.write(uint8_to_bytes(scaling[1]))

    file.write(uint32_to_bytes(num_frames))


def read_header(file: BinaryIO) -> DumInfo:
    offset = file.tell()
    if offset != 0:
        raise Exception(f"You must be at the file beginning to read header. Offset={offset}")
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0, 0)

    header_size = 0

    magic_string = file.read(4)
    if magic_string != b'dumv':
        raise Exception(f"Invalid DUM file! Expected magic string 'dumv' but found {magic_string}.")
    header_size += 4

    def read(size: int) -> int:
        nonlocal header_size
        n = bytes_to_int(file.read(size))
        header_size += size
        return n

    frame_rate = read(1)
    width = read(2)
    height = read(2)
    hor_scaling = read(1)
    ver_scaling = read(1)

    num_frames = read(4)

    return DumInfo(frame_rate, width, height, hor_scaling, ver_scaling, num_frames, header_size, file_size)
