from typing import Tuple, BinaryIO

RGB = Tuple[int, int, int]


def uint32_to_bytes(n: int) -> bytes:
    return n.to_bytes(4, byteorder="big")


def bytes_to_int(b: bytes) -> int:
    if len(b) == 0:
        raise NothingToRead(f"Can't read int from empty byte array")
    return int.from_bytes(b, byteorder="big")


def uint8_to_bytes(n: int) -> bytes:
    return n.to_bytes(1, byteorder="big")


class NothingToRead(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def write_rgb(file: BinaryIO, rgb: RGB):
    file.write(uint8_to_bytes(rgb[0]))
    file.write(uint8_to_bytes(rgb[1]))
    file.write(uint8_to_bytes(rgb[2]))


def read_rgb(file: BinaryIO) -> RGB:
    buf = file.read(3)
    return buf[0], buf[1], buf[2]
