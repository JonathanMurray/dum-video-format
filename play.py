#!/usr/bin/env python3
import sys
from typing import List, Tuple, BinaryIO

import pygame
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.time import Clock

from format import Decoder

DEBUG = False
LOOP = True


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


def play_file_at_path(path: str):
    debug(f"Opening file {path}...")
    with open(path, "rb") as file:
        play_file(file, path)


def play_file(file: BinaryIO, caption: str):
    decoder = Decoder(file)
    decoder.read_header()
    info = decoder.info

    debug(f"Parsed header. Video consists of {info.num_frames} frames")
    pygame.init()
    screen_size = (max(info.width * info.hor_scaling, 256), max(info.height * info.ver_scaling, 256))
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption(caption)
    screen.fill((0, 0, 0))
    pygame.display.update()

    pixel_rect = Rect(0, 0, info.hor_scaling, info.ver_scaling)
    margin = 4
    seekbar_size = (screen.get_width() - margin * 2, 20)
    seekbar_pos = (margin, screen.get_height() - seekbar_size[1] - margin)
    seekbar_rect = Rect(seekbar_pos, seekbar_size)
    seekbar = Seekbar(Surface(seekbar_size))

    clock = Clock()
    frame_i = 0
    while True:

        if LOOP and frame_i == info.num_frames:
            decoder.seek_to_beginning()
            frame_i = 0

        clock.tick(info.frame_rate)
        pygame.display.set_caption(f"{caption} ({(int(clock.get_fps()))})")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_program()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit_program()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if seekbar_rect.collidepoint(event.pos):
                    mouse_x = event.pos[0]
                    progress = (mouse_x - seekbar_rect.x) / seekbar_rect.w
                    debug(f"Seeking to progress: {progress}")
                    frame_i = decoder.seek(progress)

        screen.fill((0, 0, 0))

        frame = decoder.read_frame()

        debug(f"Time: {round(frame_i / info.frame_rate, 2)}s")

        # draw_frame(screen, pixel_rect, frame, (info.width, info.height))
        fast_draw_bgr_frame(screen, frame, (info.width, info.height), (info.hor_scaling, info.ver_scaling))
        seekbar.set_progress(frame_i / info.num_frames)
        seekbar.redraw()
        screen.blit(seekbar.surface, seekbar_pos)
        pygame.display.update()
        frame_i += 1


def draw_frame(screen: Surface, rect: Rect, frame: List[int], frame_resolution: Tuple[int, int]):
    for y in range(frame_resolution[1]):
        for x in range(frame_resolution[0]):
            offset = 3 * (x + y * frame_resolution[0])
            r = frame[offset]
            g = frame[offset + 1]
            b = frame[offset + 2]
            rect.x = x * rect.w
            rect.y = y * rect.h
            pygame.draw.rect(screen, (r, g, b), rect)


def fast_draw_bgr_frame(screen: Surface, frame: List[int], resolution: Tuple[int, int], scale: Tuple[int, int]):

    frame_surface = Surface(resolution, depth=24)
    view = frame_surface.get_view()
    view.write(bytes(frame))
    del view
    frame_surface = pygame.transform.scale(frame_surface, (resolution[0] * scale[0], resolution[1] * scale[1]))
    screen.blit(frame_surface, (0, 0))


def exit_program():
    debug("Exiting program.")
    pygame.quit()
    sys.exit(0)


def main():
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} FILE")
        return
    play_file_at_path(args[0])


if __name__ == '__main__':
    main()
