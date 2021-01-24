#!/usr/bin/env python3
import sys
from typing import BinaryIO

import pygame
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.time import Clock

from io_utils import bytes_to_int, NothingToRead
from parse import parse_header, DumInfo

DEBUG = False


def debug(text: str):
    if DEBUG:
        print(text)


class Seekbar:
    def __init__(self, surface: Surface):
        self.surface = surface
        self._progress = 0

    def set_progress(self, progress: float):
        self._progress = progress

    def redraw(self):
        self.surface.fill((120, 80, 150))
        border_color = (255, 255, 255)
        pygame.draw.rect(self.surface, border_color, (0, 0, self.surface.get_width(), self.surface.get_height()), 1)
        cursor_color = (255, 255, 255)
        cursor_rect = (self.surface.get_width() * self._progress, 0, 4, self.surface.get_height())
        pygame.draw.rect(self.surface, cursor_color, cursor_rect)


def play_file(path: str):
    with open(path, "rb") as file:

        info = parse_header(file)

        debug(f"Total {info.num_frames} frames")
        pygame.init()
        screen_size = (max(info.width * info.hor_scaling, 256), max(info.height * info.ver_scaling, 256))
        screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(path)

        pixel_rect = Rect(0, 0, info.hor_scaling, info.ver_scaling)
        margin = 4
        seekbar_height = 20
        seekbar_pos = (margin, screen.get_height() - seekbar_height - margin)
        seekbar = Seekbar(Surface((screen.get_width() - margin * 2, seekbar_height)))

        running = True
        clock = Clock()
        frame = 0
        while True:
            clock.tick(info.frame_rate)
            if running:
                debug(f"Frame {frame}/{info.num_frames}")
                debug(f"{file.tell()}/{info.file_size} bytes")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_program()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    exit_program()

            screen.fill((0, 0, 0))

            running = draw_frame(file, info, pixel_rect, screen)
            seekbar.set_progress(frame / info.num_frames)
            seekbar.redraw()
            screen.blit(seekbar.surface, seekbar_pos)
            pygame.display.update()
            frame += 1


def draw_frame(file: BinaryIO, header: DumInfo, rect: Rect, screen: Surface) -> bool:
    for y in range(header.height):
        for x in range(header.width):
            try:
                color = (bytes_to_int(file.read(1)), bytes_to_int(file.read(1)), bytes_to_int(file.read(1)))
            except NothingToRead:
                return False
            rect.x = x * header.hor_scaling
            rect.y = y * header.ver_scaling
            pygame.draw.rect(screen, color, rect)
    return True


def exit_program():
    debug("Exiting program.")
    pygame.quit()
    sys.exit(0)


def main():
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} FILE")
        return
    play_file(args[0])


if __name__ == '__main__':
    main()
