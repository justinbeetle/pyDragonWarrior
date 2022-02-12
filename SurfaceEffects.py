#!/usr/bin/env python

import pygame

from GameDialog import GameDialog
from GameStateInterface import GameStateInterface


def fade_to_black_and_back(screen: pygame.surface.Surface) -> None:
    fade_to_color_and_back(screen, pygame.Color('black'))


def fade_out_to_black(screen: pygame.surface.Surface) -> None:
    fade_out_to_color(screen, pygame.Color('black'))


def fade_in_from_black(screen: pygame.surface.Surface) -> None:
    fade_in_from_color(screen, pygame.Color('black'))


def fade_to_color_and_back(screen: pygame.surface.Surface, fade_color: pygame.Color) -> None:
    background_surface = screen.copy()
    fade_surface = pygame.surface.Surface(screen.get_size())
    fade_surface.fill(fade_color)
    fade_out(screen, background_surface, fade_surface)
    fade_out(screen, fade_surface, background_surface)


def fade_out_to_color(screen: pygame.surface.Surface, fade_color: pygame.Color) -> None:
    background_surface = screen.copy()
    fade_surface = pygame.surface.Surface(screen.get_size())
    fade_surface.fill(fade_color)
    fade_out(screen, background_surface, fade_surface)


def fade_in_from_color(screen: pygame.surface.Surface, fade_color: pygame.Color) -> None:
    background_surface = screen.copy()
    fade_surface = pygame.surface.Surface(screen.get_size())
    fade_surface.fill(fade_color)
    fade_out(screen, fade_surface, background_surface)


def fade_out(screen: pygame.surface.Surface,
             background_surface: pygame.surface.Surface,
             fade_surface: pygame.surface.Surface) -> None:
    clock = pygame.time.Clock()
    for i in range(15, 256, 16):
        fade_surface.set_alpha(i)
        screen.blit(background_surface, (0, 0))
        screen.blit(fade_surface, (0, 0))
        clock.tick(20)
        pygame.display.flip()


def flickering(screen: pygame.surface.Surface) -> None:
    background_surface = screen.copy()
    flicker_surface = pygame.surface.Surface(screen.get_size())
    flicker_surface.fill('white')
    flicker_surface.set_alpha(128)

    clock = pygame.time.Clock()
    for flicker_times in range(10):
        screen.blit(flicker_surface, (0, 0))
        clock.tick(30)
        pygame.display.flip()

        screen.blit(background_surface, (0, 0))
        clock.tick(30)
        pygame.display.flip()


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


rainbow_colors = [pygame.Color('red'),
                  pygame.Color('orange'),
                  pygame.Color('yellow'),
                  pygame.Color('green'),
                  pygame.Color('blue'),
                  #pygame.Color('blueviolet'),  # pygame.Color('indigo'),
                  pygame.Color('violet')]


def rainbow_effect(game_state: GameStateInterface, message_dialog: GameDialog) -> None:
    game_info = game_state.get_game_info()

    if game_info.maps[game_state.get_map_name()].tiled_filename is None:
        # On a legacy map, use the original effect
        rainbow_effect_on_water(game_state.screen, game_info.tiles['water'].images[0][0])
    else:
        # On a tiled map, use the new effect
        rainbow_effect_across_map(game_state, message_dialog)


def rainbow_effect_across_map(game_state: GameStateInterface, message_dialog: GameDialog) -> None:
    game_state.draw_map(flip_buffer=False, draw_status=False)
    background_surface = game_state.screen.copy()

    # Cycle through the rainbow colors
    clock = pygame.time.Clock()
    for i in range(2):
        for rainbow_color in rainbow_colors:
            fade_surface = pygame.surface.Surface(game_state.screen.get_size())
            fade_surface.fill(rainbow_color)

            def fade_step(alpha: int) -> None:
                fade_surface.set_alpha(alpha)
                game_state.screen.blit(background_surface, (0, 0))
                game_state.screen.blit(fade_surface, (0, 0))

                # Overlay the dialogs
                game_state.draw_map(flip_buffer=False, draw_background=False, draw_status=True)
                if not message_dialog.is_empty():
                    message_dialog.blit(game_state.screen)

                # Advance a tick
                clock.tick(15)
                pygame.display.flip()

            for j in range(63, 196, 64):
                fade_step(j)

            for j in range(63, 196, 64):
                fade_step(196 - j)


def rainbow_effect_on_water(screen: pygame.surface.Surface,
                            water_tile: pygame.surface.Surface) -> None:
    orig_screen = screen.copy()
    water_color = pygame.transform.average_color(water_tile, water_tile.get_rect())

    # Cycle through the rainbow colors
    clock = pygame.time.Clock()
    for i in range(4):
        for rainbow_color in rainbow_colors:
            try:
                pygame.transform.threshold(screen,
                                           orig_screen,
                                           search_color=water_color,
                                           threshold=pygame.Color(50, 50, 50),
                                           set_color=rainbow_color,
                                           inverse_set=True)
                clock.tick(5)
                pygame.display.flip()
            except:
                print('Color not found: ', rainbow_color, flush=True)

    # Restore original screen
    screen.blit(orig_screen, (0, 0))
    pygame.display.flip()
