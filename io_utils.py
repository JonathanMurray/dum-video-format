def int_to_bytes(n: int) -> bytes:
    return n.to_bytes(4, byteorder="big")


def bytes_to_int(b: bytes) -> int:
    if not b:
        raise NothingToRead("Cannot convert empty byte sequence to integer")
    return int.from_bytes(b, byteorder="big")


class NothingToRead(Exception):
    def __init__(self, message: str):
        super().__init__(message)
