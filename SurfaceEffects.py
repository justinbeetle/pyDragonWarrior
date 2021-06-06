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
    water_color = pygame.transform.average_color(water_tile, None)
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
