#!/usr/bin/env python3
from io import BytesIO

import pygame
from pygame import Surface
from pygame.rect import Rect

from format import write_frame
from header import write_header
from play import play_file
from pygame_utils import get_surface_pixels

file = BytesIO()
num_frames = 300
surface = Surface((150, 30))

write_header(file, frame_rate=30, resolution=surface.get_size(), scaling=(3, 3), num_frames=num_frames)
rect = Rect(5, 5, 20, 20)
print("Writing frames to IO buffer...")
for i in range(num_frames):
    surface.fill((100, 100, 100))
    pygame.draw.rect(surface, (250, 250, 250), rect)
    pixels = list(get_surface_pixels(surface))
    write_frame(file, pixels)
    if i < num_frames // 2:
        rect.move_ip(1, 0)
    else:
        rect.move_ip(-1, 0)
print("Done creating video.")
play_file(file, "testing")
