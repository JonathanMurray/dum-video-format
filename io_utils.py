from typing import Tuple, BinaryIO

Color = Tuple[int, int, int]


def uint8_to_bytes(n: int) -> bytes:
    return n.to_bytes(1, byteorder="big")


def uint16_to_bytes(n: int) -> bytes:
    return n.to_bytes(2, byteorder="big")


def uint32_to_bytes(n: int) -> bytes:
    return n.to_bytes(4, byteorder="big")


def bytes_to_int(b: bytes) -> int:
    if len(b) == 0:
        raise ReadError(f"Can't read int from empty byte array")
    return int.from_bytes(b, byteorder="big")


class ReadError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def write_rgb(file: BinaryIO, rgb: Color):
    file.write(bytes(rgb))


def write_bgr(file: BinaryIO, rgb: Color):
    file.write(bytes((rgb[2], rgb[1], rgb[0])))


def read_rgb(file: BinaryIO) -> Color:
    buf = file.read(3)
    if len(buf) != 3:
        raise ReadError(f"Expected 3 bytes but only got {len(buf)}")
    return buf[0], buf[1], buf[2]
