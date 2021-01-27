from typing import Iterator

from pygame import Surface

from io_utils import RGB


def get_surface_pixels(surface: Surface) -> Iterator[RGB]:
    w = surface.get_width()
    h = surface.get_height()
    for y in range(h):
        for x in range(w):
            pixel = surface.get_at((x, y))
            yield pixel[0], pixel[1], pixel[2]
