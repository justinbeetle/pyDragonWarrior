#!/usr/bin/env python

import math
import pygame

from GameTypes import Direction


def fade_to_black_and_back(screen: pygame.surface.Surface) -> None:
    background_surface = screen.copy()
    fade_surface = pygame.surface.Surface(screen.get_size())
    fade_surface.fill(pygame.Color('black'))
    fade_out(screen, background_surface, fade_surface)
    fade_out(screen, fade_surface, background_surface)


def fade_out_to_black(screen: pygame.surface.Surface) -> None:
    background_surface = screen.copy()
    fade_surface = pygame.surface.Surface(screen.get_size())
    fade_surface.fill(pygame.Color('black'))
    fade_out(screen, background_surface, fade_surface)


def fade_in_from_black(screen: pygame.surface.Surface) -> None:
    background_surface = screen.copy()
    fade_surface = pygame.surface.Surface(screen.get_size())
    fade_surface.fill(pygame.Color('black'))
    fade_out(screen, fade_surface, background_surface)


def fade_out(screen: pygame.surface.Surface,
             background_surface: pygame.surface.Surface,
             fade_surface: pygame.surface.Surface) -> None:
    for i in range(15, 256, 16):
        fade_surface.set_alpha(i)
        screen.blit(background_surface, (0, 0))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(30)


'''def fade_in(screen: pygame.surface.Surface,
            background_surface: pygame.surface.Surface,
            fade_surface: pygame.surface.Surface) -> None:
    for i in range(240, -1, -16):
        fade_surface.set_alpha(i)
        screen.blit(background_surface, (0, 0))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(30)
'''


def flickering(screen: pygame.surface.Surface) -> None:
    background_surface = screen.copy()
    flicker_surface = pygame.surface.Surface(screen.get_size())
    flicker_surface.fill(pygame.Color('white'))
    flicker_surface.set_alpha(128)

    for flicker_times in range(10):
        screen.blit(background_surface, (0, 0))
        screen.blit(flicker_surface, (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(30)

        screen.blit(background_surface, (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(30)


def pink_tinge(screen: pygame.surface.Surface,
               flip_buffer: bool = True) -> None:
    color_tinge(screen, pygame.Color(252, 116, 96), flip_buffer)


def color_tinge(screen: pygame.surface.Surface,
                tinge_color: pygame.Color,
                flip_buffer: bool = True) -> None:
    pygame.transform.threshold(screen,
                               screen,
                               search_color=pygame.Color('white'),
                               threshold=pygame.Color(3, 3, 3),
                               set_color=tinge_color,
                               inverse_set=True)
    if flip_buffer:
        pygame.display.flip()


def black_red_monochrome_effect(screen: pygame.surface.Surface,
                                flip_buffer: bool = True) -> None:
    red = pygame.Color(255, 62, 24)
    pygame.transform.threshold(screen,
                               screen,
                               search_color=pygame.Color('white'),
                               threshold=pygame.Color(3, 3, 3),
                               set_color=red,
                               inverse_set=True)
    pygame.transform.threshold(screen,
                               screen,
                               search_color=red,
                               set_color=pygame.Color('black'),
                               inverse_set=False)
    if flip_buffer:
        pygame.display.flip()


def rainbow_effect(screen: pygame.surface.Surface,
                   water_tile: pygame.surface.Surface) -> None:
    orig_screen = screen.copy()
    water_color = pygame.transform.average_color(water_tile)
    rainbow_colors = [pygame.Color('red'),
                      pygame.Color('orange'),
                      pygame.Color('yellow'),
                      pygame.Color('green'),
                      pygame.Color('blue'),
                      pygame.Color('green'),
                      pygame.Color(75, 0, 130),  # pygame.Color('indigo'),
                      pygame.Color('violet')]

    # Cycle through the rainbow colors
    for i in range(4):
        for rainbow_color in rainbow_colors:
            try:
                pygame.transform.threshold(screen,
                                           orig_screen,
                                           search_color=water_color,
                                           threshold=pygame.Color(50, 50, 50),
                                           set_color=rainbow_color,
                                           inverse_set=True)
                pygame.display.flip()
                pygame.time.Clock().tick(15)
            except:
                print('Color not found: ', rainbow_color, flush=True)

    # Restore original screen
    screen.blit(orig_screen, (0, 0))
    pygame.display.flip()


def scroll_view(screen: pygame.surface.Surface,
                image: pygame.surface.Surface,
                direction: Direction,
                view_rect: pygame.Rect,
                zoom_factor: float,
                image_px_step_size: int,
                update: bool = False) -> None:
    src_rect = None
    dst_rect = None
    zoom_view_rect = screen.get_clip()
    image_w, image_h = image.get_size()
    dst_image_px_step_size = math.ceil(image_px_step_size * zoom_factor)

    if direction == Direction.NORTH:
        if view_rect.top >= image_px_step_size:
            screen.scroll(dy=dst_image_px_step_size)
            view_rect.move_ip(0, -image_px_step_size)
            src_rect = view_rect.copy()
            src_rect.h = image_px_step_size
            dst_rect = zoom_view_rect.copy()
            dst_rect.h = dst_image_px_step_size
    elif direction == Direction.SOUTH:
        if view_rect.bottom <= image_h - image_px_step_size:
            screen.scroll(dy=-dst_image_px_step_size)
            view_rect.move_ip(0, image_px_step_size)
            src_rect = view_rect.copy()
            src_rect.h = image_px_step_size
            src_rect.bottom = view_rect.bottom
            dst_rect = zoom_view_rect.copy()
            dst_rect.h = dst_image_px_step_size
            dst_rect.bottom = zoom_view_rect.bottom
    elif direction == Direction.WEST:
        if view_rect.left >= image_px_step_size:
            screen.scroll(dx=dst_image_px_step_size)
            view_rect.move_ip(-image_px_step_size, 0)
            src_rect = view_rect.copy()
            src_rect.w = image_px_step_size
            dst_rect = zoom_view_rect.copy()
            dst_rect.w = dst_image_px_step_size
    elif direction == Direction.EAST:
        if view_rect.right <= image_w - image_px_step_size:
            screen.scroll(dx=-dst_image_px_step_size)
            view_rect.move_ip(image_px_step_size, 0)
            src_rect = view_rect.copy()
            src_rect.w = image_px_step_size
            src_rect.right = view_rect.right
            dst_rect = zoom_view_rect.copy()
            dst_rect.w = dst_image_px_step_size
            dst_rect.right = zoom_view_rect.right
    if src_rect is not None and dst_rect is not None:
        src = image.subsurface(src_rect)
        pygame.transform.scale(src,
                               dst_rect.size,
                               screen.subsurface(dst_rect))
        if update:
            pygame.display.update(zoom_view_rect)
