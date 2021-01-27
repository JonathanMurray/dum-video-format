#!/usr/bin/env python3
from io import BytesIO

import pygame
from pygame import Surface
from pygame.rect import Rect

from format import write_header, write_frame
from play import play_file
from pygame_utils import get_surface_pixels

file = BytesIO()
num_frames = 100
surface = Surface((150, 100))

write_header(file, frame_rate=30, resolution=surface.get_size(), scaling=(3, 3), num_frames=num_frames)
rect = Rect(10, 30, 40, 40)
for _ in range(num_frames):
    surface.fill((100, 100, 100))
    pygame.draw.rect(surface, (250, 150, 250), rect, width=1)
    pixels = list(get_surface_pixels(surface))
    write_frame(file, pixels)
    rect.move_ip(1, 0)
play_file(file, "testing")
