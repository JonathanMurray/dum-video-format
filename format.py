from dataclasses import dataclass
from enum import Enum
from typing import BinaryIO, Tuple, List, Callable

from color_quantization import uint15_to_color, color_to_uint7, uint7_to_color, color_to_uint15
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


def _skip_frame(file: BinaryIO) -> Tuple[int, int]:
    frame_type = bytes_to_int(file.read(1))
    if frame_type not in (t.value for t in FrameType):
        raise ValueError(f"Unexpected frame_type at offset {file.tell() - 1}: {frame_type}")
    frame_size = bytes_to_int(file.read(4))
    file.seek(frame_size, 1)
    return frame_type, frame_size


def _read_frame(file: BinaryIO, resolution: Tuple[int, int]) -> List[int]:
    frame_type = bytes_to_int(file.read(1))
    file.read(4)  # frame size
    if frame_type == FrameType.RAW.value:
        debug("Reading raw frame...")
        frame_size = resolution[0] * resolution[1] * 3
        buf = file.read(frame_size)
        if len(buf) < frame_size:
            print(f"WARN: Read {len(buf)} bytes - not enough for a full frame!")
    elif frame_type == FrameType.COLOR_MAPPED.value:
        debug("Reading color-mapped frame...")
        num_colors = bytes_to_int(file.read(1))
        color_map = [read_rgb(file) for _ in range(num_colors)]
        buf = []
        for i in range(resolution[0] * resolution[1]):
            color_index = bytes_to_int(file.read(1))
            color = color_map[color_index]
            buf.append(color[0])
            buf.append(color[1])
            buf.append(color[2])
    elif frame_type == FrameType.QUANTIZED_TO_16_BIT.value:
        debug("Reading 16-bit quantized frame...")
        buf = _read_quantized_frame(resolution, read_quantized_pixel=lambda: bytes_to_int(file.read(2)),
                                    decode_pixel=uint15_to_color, flag_bitmask=0b10000000_00000000,
                                    run_length_bitmask=0b01111111_11111111)
    elif frame_type == FrameType.QUANTIZED_TO_8_BIT.value:
        debug("Reading 8-bit quantized frame...")
        buf = _read_quantized_frame(resolution, read_quantized_pixel=lambda: bytes_to_int(file.read(1)),
                                    decode_pixel=uint7_to_color, flag_bitmask=0b10000000, run_length_bitmask=0b01111111)
    else:
        raise ValueError(f"Read unexpected frame type: {frame_type}, offset={file.tell() - 1}")
    return buf


def _read_quantized_frame(resolution: Tuple[int, int], read_quantized_pixel: Callable[[], int],
    decode_pixel: Callable[[int], RGB], flag_bitmask: int, run_length_bitmask: int) -> List[int]:
    buf = []
    run_length_color = None
    while len(buf) < resolution[0] * resolution[1] * 3:
        q = read_quantized_pixel()
        if not q & flag_bitmask:
            color = decode_pixel(q)
            buf.append(color[0])
            buf.append(color[1])
            buf.append(color[2])
            run_length_color = color
        else:
            run_length = q & run_length_bitmask
            for j in range(run_length):
                buf.append(run_length_color[0])
                buf.append(run_length_color[1])
                buf.append(run_length_color[2])
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
        debug("Writing color-mapped frame")
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
            write_8bit_quantized_frame(file, pixels)
        elif quality == Quality.MEDIUM:
            write_16bit_quantized_frame(file, pixels)
        elif quality == Quality.LOSSLESS:
            debug("Writing raw frame")
            # Frame type
            file.write(uint8_to_bytes(FrameType.RAW.value))
            # Frame size
            file.write(uint32_to_bytes(len(pixels) * 3))
            for pixel in pixels:
                write_rgb(file, pixel)
        else:
            raise ValueError(f"Unhandled quality: {quality}")


def write_8bit_quantized_frame(file: BinaryIO, pixels: List[RGB]):
    debug("Writing 8-bit quantized frame")
    _write_quantized_frame(file, pixels, quantize_color=color_to_uint7, max_run_length=127, bitsize=8,
                           to_bytes=uint8_to_bytes, frame_type=FrameType.QUANTIZED_TO_8_BIT)


def write_16bit_quantized_frame(file: BinaryIO, pixels: List[RGB]):
    debug("Writing 16-bit quantized frame")
    _write_quantized_frame(file, pixels, quantize_color=color_to_uint15, max_run_length=32_767, bitsize=16,
                           to_bytes=uint16_to_bytes, frame_type=FrameType.QUANTIZED_TO_16_BIT)


def _write_quantized_frame(file: BinaryIO, pixels: List[RGB], quantize_color: Callable[[RGB], int], max_run_length: int,
    bitsize: int, to_bytes: Callable[[int], bytes], frame_type: FrameType):
    file.write(uint8_to_bytes(frame_type.value))
    # Frame size is written at the end
    frame_size_offset = file.tell()
    file.write(uint32_to_bytes(0))
    frame_content_offset = file.tell()
    quantized_pixels = [quantize_color(p) for p in pixels]
    run_length_pixel = None
    accumulated_run_length = 0
    for p in quantized_pixels:
        if p != run_length_pixel or accumulated_run_length == max_run_length:
            if accumulated_run_length:
                debug(f"Writing accumulated run-length: {accumulated_run_length}, color {run_length_pixel}")
                file.write(to_bytes((1 << (bitsize - 1)) + accumulated_run_length))
            file.write(to_bytes(p))
            run_length_pixel = p
            accumulated_run_length = 0
        else:
            # Same pixel as last one => start counting
            accumulated_run_length += 1
    if accumulated_run_length:
        debug(f"Writing last accumulated run-length: {accumulated_run_length}, color {run_length_pixel}")
        file.write(to_bytes((1 << (bitsize - 1)) + accumulated_run_length))
    frame_size = file.tell() - frame_content_offset
    file.seek(frame_size_offset)
    file.write(uint32_to_bytes(frame_size))
    file.seek(0, 2)
