from dataclasses import dataclass
from typing import BinaryIO, Tuple, List

from io_utils import bytes_to_int, int_to_bytes


@dataclass
class DumInfo:
    frame_rate: int
    width: int
    height: int
    hor_scaling: int
    ver_scaling: int
    header_size: int
    num_frames: int
    file_size: int


def parse_header(file: BinaryIO) -> DumInfo:
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0, 0)

    header_size = 0

    magic_string = file.read(3)
    if magic_string != b'dum':
        raise Exception(f"Invalid DUM file! Expected magic string 'dum' but found {magic_string}.")

    header_size += 3

    def read_int() -> int:
        nonlocal header_size
        n = bytes_to_int(file.read(4))
        header_size += 4
        return n

    frame_rate = read_int()
    width = read_int()
    height = read_int()
    hor_scaling = read_int()
    ver_scaling = read_int()

    remaining_bytes = file_size - header_size
    num_frames = int(remaining_bytes / width / height / 3)

    return DumInfo(frame_rate, width, height, hor_scaling, ver_scaling, header_size, num_frames, file_size)


def write_header(file: BinaryIO, frame_rate: int, resolution: Tuple[int, int], scaling: Tuple[int, int]):
    # magic string
    file.write(b'dum')
    file.write(int_to_bytes(frame_rate))

    # width
    file.write(int_to_bytes(resolution[0]))

    # height
    file.write(int_to_bytes(resolution[1]))

    # horizontal scale
    file.write(int_to_bytes(scaling[0]))

    # vertical scale
    file.write(int_to_bytes(scaling[1]))


def write_frame(file: BinaryIO, rows: List[List[Tuple[int, int, int]]]):
    for row in rows:
        for (r, g, b) in row:
            write_pixel(file, r, g, b)


def write_pixel(file: BinaryIO, r: int, g: int, b: int):
    file.write(r.to_bytes(1, byteorder="big"))
    file.write(g.to_bytes(1, byteorder="big"))
    file.write(b.to_bytes(1, byteorder="big"))