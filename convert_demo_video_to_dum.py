#!/usr/bin/env python3
from io import BytesIO
from time import time
from typing import BinaryIO, Tuple

import av

from format import write_frame, Quality
from header import write_header
from play import play_file

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


def convert(outfile: BinaryIO, resolution: Tuple[int, int], scaling: Tuple[int, int], num_frames: int,
    quality: Quality):
    with open("night-sky.h264", "rb") as file:
        codec = av.CodecContext.create("h264", "r")

        write_header(outfile, 25, resolution, scaling, num_frames)
        frame_i = 0
        while frame_i < num_frames:

            chunk = file.read(1 << 16)

            packets = codec.parse(chunk)
            debug("Parsed {} packets from {} bytes:".format(len(packets), len(chunk)))

            for packet in packets:
                debug(f"   {packet}")
                frames = codec.decode(packet)
                for frame in frames:
                    debug(f"       {frame}")
                    frame = frame.reformat(resolution[0], resolution[1])
                    image_data = list(frame.to_image().getdata())
                    before = time()
                    offset_before = outfile.tell()
                    write_frame(outfile, image_data, quality=quality)
                    print(
                        f"        It took {round(time() - before, 2)}s to write frame ({outfile.tell() - offset_before}B)")
                    frame_i += 1


def convert_to_file(filename: str):
    with open(filename, "wb") as outfile:
        convert(outfile, resolution=(640, 360), scaling=(1, 1), num_frames=10, quality=Quality.LOW)


def convert_and_play_in_memory():
    outfile = BytesIO()
    quality = Quality.LOW
    convert(outfile, resolution=(640, 360), scaling=(1, 1), num_frames=10, quality=quality)
    play_file(outfile, f"Night sky ({quality.name})")


def main():
    convert_and_play_in_memory()


if __name__ == '__main__':
    main()
