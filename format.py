from dataclasses import dataclass
from enum import Enum
from typing import BinaryIO, Tuple, List

from color_quantization import color_to_uint16, uint16_to_color, uint8_to_color, color_to_uint8
from io_utils import uint8_to_bytes, RGB, uint32_to_bytes, bytes_to_int, write_rgb, read_rgb, uint16_to_bytes

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


def log(text: str):
    print(text)


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


class Decoder:
    def __init__(self, file: BinaryIO):
        self._file = file
        self._info = None
        self._frame_index = 0

    def read_header(self) -> DumInfo:
        if self._info:
            raise Exception("Header has already been parsed!")
        self._info = _read_header(self._file)
        return self._info

    def read_frame(self) -> List[int]:
        info = self.info
        frame = _read_frame(self._file, info)
        self._frame_index += 1
        debug(f"Frame {self._frame_index}/{info.num_frames}")
        debug(f"{self._file.tell()}/{info.file_size} bytes")
        return frame

    def skip_frame(self):
        _skip_frame(self._file)
        self._frame_index += 1

    def seek(self, progress: float) -> int:
        target_frame = int(self.info.num_frames * progress)
        if target_frame < self._frame_index:
            log(f"Seeking {target_frame} frames from beginning. ({self._frame_index} --> {target_frame})")
            self.seek_to_beginning()
            for _ in range(target_frame):
                self.skip_frame()
        else:
            diff = target_frame - self._frame_index
            log(f"Seeking forward {diff} frames. ({self._frame_index} --> {target_frame})")
            for _ in range(diff):
                self.skip_frame()
        return target_frame

    def seek_to_beginning(self):
        self._file.seek(self.info.header_size)
        self._frame_index = 0

    @property
    def info(self) -> DumInfo:
        if not self._info:
            raise Exception("Must parse header before getting info!")
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
    width = read(2)
    height = read(2)
    hor_scaling = read(1)
    ver_scaling = read(1)

    num_frames = read(4)

    return DumInfo(frame_rate, width, height, hor_scaling, ver_scaling, num_frames, header_size, file_size)


def _skip_frame(file: BinaryIO):
    frame_type = bytes_to_int(file.read(1))
    if frame_type not in (t.value for t in FrameType):
        raise ValueError(f"Unexpected frame_type at offset {file.tell() - 1}: {frame_type}")
    frame_size = bytes_to_int(file.read(4))
    file.seek(frame_size, 1)


def _read_frame(file: BinaryIO, info: DumInfo) -> List[int]:
    frame_type = bytes_to_int(file.read(1))
    file.read(4)  # frame size
    if frame_type == FrameType.RAW.value:
        debug("Reading raw frame...")
        frame_size = info.height * info.width * 3
        buf = file.read(frame_size)
        if len(buf) < frame_size:
            print(f"WARN: Read {len(buf)} bytes - not enough for a full frame!")
    elif frame_type == FrameType.COLOR_MAPPED.value:
        debug("Reading color-mapped frame...")
        num_colors = bytes_to_int(file.read(1))
        color_map = [read_rgb(file) for _ in range(num_colors)]
        buf = []
        for i in range(info.width * info.height):
            color_index = bytes_to_int(file.read(1))
            color = color_map[color_index]
            buf.append(color[0])
            buf.append(color[1])
            buf.append(color[2])
    elif frame_type == FrameType.QUANTIZED_TO_16_BIT.value:
        buf = []
        for i in range(info.width * info.height):
            color = uint16_to_color(bytes_to_int(file.read(2)))
            buf.append(color[0])
            buf.append(color[1])
            buf.append(color[2])
    elif frame_type == FrameType.QUANTIZED_TO_8_BIT.value:
        buf = []
        for i in range(info.width * info.height):
            color = uint8_to_color(bytes_to_int(file.read(1)))
            buf.append(color[0])
            buf.append(color[1])
            buf.append(color[2])
    else:
        raise ValueError(f"Read unexpected frame type: {frame_type}, offset={file.tell() - 1}")
    return buf


class FrameType(Enum):
    RAW = 1
    COLOR_MAPPED = 2
    QUANTIZED_TO_16_BIT = 3
    QUANTIZED_TO_8_BIT = 4


class Quality(Enum):
    LOW = 0
    MEDIUM = 1
    LOSSLESS = 2


def write_header(file: BinaryIO, frame_rate: int, resolution: Tuple[int, int], scaling: Tuple[int, int],
    num_frames: int):
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


def write_frame(file: BinaryIO, pixels: List[RGB], quality: Quality = Quality.LOSSLESS):
    colors = list(set(pixels))

    if len(colors) < 256:
        # Frame type
        file.write(uint8_to_bytes(FrameType.COLOR_MAPPED.value))
        # Frame size
        file.write(uint32_to_bytes(1 + len(colors) * 3 + len(pixels)))
        file.write(uint8_to_bytes(len(colors)))
        for key_color in colors:
            write_rgb(file, key_color)
        for i, pixel in enumerate(pixels):
            file.write(uint8_to_bytes(colors.index(pixel)))
    else:
        if quality == Quality.LOW:
            # Frame type
            file.write(uint8_to_bytes(FrameType.QUANTIZED_TO_8_BIT.value))
            # Frame size
            file.write(uint32_to_bytes(len(pixels)))
            for pixel in pixels:
                file.write(uint8_to_bytes(color_to_uint8(pixel)))
        elif quality == Quality.MEDIUM:
            # Frame type
            file.write(uint8_to_bytes(FrameType.QUANTIZED_TO_16_BIT.value))
            # Frame size
            file.write(uint32_to_bytes(len(pixels) * 2))
            for pixel in pixels:
                file.write(uint16_to_bytes(color_to_uint16(pixel)))
        elif quality == Quality.LOSSLESS:
            # Frame type
            file.write(uint8_to_bytes(FrameType.RAW.value))
            # Frame size
            file.write(uint32_to_bytes(len(pixels) * 3))
            for pixel in pixels:
                write_rgb(file, pixel)
        else:
            raise ValueError(f"Unhandled quality: {quality}")
