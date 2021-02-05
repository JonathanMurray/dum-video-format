from enum import Enum
from typing import BinaryIO, Tuple, List

from codec.colormapped import read_color_mapped_frame, write_color_mapped_frame
from codec.quantized import read_16bit_quantized_frame, read_8bit_quantized_frame, write_8bit_quantized_frame, \
    write_16bit_quantized_frame
from codec.raw import write_raw_frame, read_raw_frame
from common import FrameType
from header import read_header, DumInfo
from io_utils import Color, bytes_to_int

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


def log(text: str):
    print(text)


class Decoder:
    def __init__(self, file: BinaryIO):
        self._file = file
        self._info = None
        self._frame_index = 0

    def read_header(self) -> DumInfo:
        self._file.seek(0)
        if self._info:
            raise Exception("Header has already been parsed!")
        self._info = read_header(self._file)
        return self._info

    def read_frame(self) -> List[int]:
        info = self.info
        try:
            frame = _read_frame(self._file, (info.width, info.height))
        except Exception as e:
            raise Exception(f"Failed to read frame {self._frame_index}") from e
        self._frame_index += 1
        debug(f"Frame {self._frame_index}/{info.num_frames}")
        debug(f"{self._file.tell()}/{info.file_size} bytes")
        return frame

    def skip_frame(self) -> Tuple[int, int]:
        frame_type, frame_size = _skip_frame(self._file)
        self._frame_index += 1
        return frame_type, frame_size

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


def _skip_frame(file: BinaryIO) -> Tuple[int, int]:
    frame_type = bytes_to_int(file.read(1))
    if frame_type not in (t.value for t in FrameType):
        raise ValueError(f"Unexpected frame_type at offset {file.tell() - 1}: {frame_type}")
    frame_size = bytes_to_int(file.read(4))
    file.seek(frame_size, 1)
    return frame_type, frame_size


def _read_frame(file: BinaryIO, resolution: Tuple[int, int]) -> List[int]:
    frame_type = bytes_to_int(file.read(1))
    frame_size = bytes_to_int(file.read(4))  # frame size
    if frame_type == FrameType.RAW.value:
        buf = read_raw_frame(file, frame_size)
    elif frame_type == FrameType.COLOR_MAPPED.value:
        buf = read_color_mapped_frame(file, resolution)
    elif frame_type == FrameType.QUANTIZED_TO_16_BIT.value:
        buf = read_16bit_quantized_frame(file, frame_size)
    elif frame_type == FrameType.QUANTIZED_TO_8_BIT.value:
        buf = read_8bit_quantized_frame(file, frame_size)
    else:
        raise ValueError(f"Read unexpected frame type: {frame_type}, offset={file.tell() - 1}")
    return buf


class Quality(Enum):
    LOW = 0
    MEDIUM = 1
    LOSSLESS = 2


def write_frame(file: BinaryIO, pixels: List[Color], quality: Quality = Quality.LOSSLESS):
    colors = list(set(pixels))

    if len(colors) < 256:
        write_color_mapped_frame(colors, file, pixels)
    else:
        if quality == Quality.LOW:
            write_8bit_quantized_frame(file, pixels)
        elif quality == Quality.MEDIUM:
            write_16bit_quantized_frame(file, pixels)
        elif quality == Quality.LOSSLESS:
            write_raw_frame(file, pixels)
        else:
            raise ValueError(f"Unhandled quality: {quality}")
