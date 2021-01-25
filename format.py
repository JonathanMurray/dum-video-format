from dataclasses import dataclass
from enum import Enum
from typing import BinaryIO, Tuple, List

from io_utils import uint8_to_bytes, RGB, uint32_to_bytes, bytes_to_int, write_rgb, read_rgb

DEBUG = True


def debug(text: str):
    if DEBUG:
        print(text)


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


class Decoder:
    def __init__(self, file: BinaryIO):
        self._file = file
        self._info = None
        self._frame_index = 0

    def read_header(self):
        if self._info:
            raise Exception("Header has already been parsed!")
        self._info = _read_header(self._file)

    def read_frame(self) -> List[int]:
        if not self._info:
            raise Exception("Must parse header before reading frames!")
        frame = _read_frame(self._file, self._info)
        self._frame_index += 1
        debug(f"Frame {self._frame_index}/{self._info.num_frames}")
        debug(f"{self._file.tell()}/{self._info.file_size} bytes")
        return frame

    def seek_to_beginning(self):
        if not self._info:
            raise Exception("Must parse header before seeking!")
        self._file.seek(self._info.header_size)
        self._frame_index = 0

    @property
    def info(self):
        return self._info


def _read_header(file: BinaryIO) -> DumInfo:
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
    width = read(1)
    height = read(1)
    hor_scaling = read(1)
    ver_scaling = read(1)

    num_frames = read(4)

    return DumInfo(frame_rate, width, height, hor_scaling, ver_scaling, header_size, num_frames, file_size)


def _read_frame(file: BinaryIO, info: DumInfo) -> List[int]:
    frame_type = bytes_to_int(file.read(1))
    if frame_type == FrameType.RAW.value:
        debug("Reading raw frame...")
        frame_size = info.height * info.width * 3
        buf = file.read(frame_size)
        if len(buf) < frame_size:
            print(f"WARN: Read {len(buf)} bytes - not enough for a full frame!")
    elif frame_type == FrameType.COMPRESSED.value:
        debug("Reading compressed frame...")
        num_colors = bytes_to_int(file.read(1))
        colors = [read_rgb(file) for _ in range(num_colors)]
        buf = []
        for i in range(info.width * info.height):
            color_index = bytes_to_int(file.read(1))
            color = colors[color_index]
            buf.append(color[0])
            buf.append(color[1])
            buf.append(color[2])
    else:
        raise ValueError(f"Read unexpected frame type: {frame_type}, offset={file.tell() - 1}")
    return buf


class FrameType(Enum):
    RAW = 0
    COMPRESSED = 1


def write_header(file: BinaryIO, frame_rate: int, resolution: Tuple[int, int], scaling: Tuple[int, int],
    num_frames: int):
    # magic string
    file.write(b'dumv')
    file.write(uint8_to_bytes(frame_rate))

    # width
    file.write(uint8_to_bytes(resolution[0]))

    # height
    file.write(uint8_to_bytes(resolution[1]))

    # horizontal scale
    file.write(uint8_to_bytes(scaling[0]))

    # vertical scale
    file.write(uint8_to_bytes(scaling[1]))

    file.write(uint32_to_bytes(num_frames))


def write_frame(file: BinaryIO, pixels: List[RGB]):
    colors = list(set(pixels))
    if len(colors) <= 256:
        debug(f"Frame only contains {len(colors)} colors. Will compress.")
        file.write(uint8_to_bytes(FrameType.COMPRESSED.value))
        file.write(uint8_to_bytes(len(colors)))
        for color in colors:
            write_rgb(file, color)
        for pixel in pixels:
            color_index = colors.index(pixel)
            file.write(uint8_to_bytes(color_index))
    else:
        debug(f"Frame contains {len(colors)} colors. Will write raw frame.")
        file.write(uint8_to_bytes(FrameType.RAW.value))
        for pixel in pixels:
            write_rgb(file, pixel)
