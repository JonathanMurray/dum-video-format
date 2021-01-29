#!/usr/bin/env python3
from format import write_frame
from header import write_header

with open("simple.dum", "wb") as file:
    red = (255, 0, 0)
    black = (0, 0, 0)
    frames = [
        [red, black,
         black, black],

        [black, red,
         black, black],

        [black, black,
         black, red],

        [black, black,
         red, black]
    ]

    write_header(file, frame_rate=4, resolution=(2, 2), scaling=(150, 150), num_frames=len(frames))
    for frame in frames:
        write_frame(file, frame)
