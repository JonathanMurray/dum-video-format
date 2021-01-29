from enum import Enum


class FrameType(Enum):
    RAW = 1
    COLOR_MAPPED = 2
    QUANTIZED_TO_16_BIT = 3
    QUANTIZED_TO_8_BIT = 4