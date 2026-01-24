#!/usr/bin/env python

import numpy as np
import pygame

# TODO: Factor these out of this module
from pydw.game_dialog import GameDialog
from pydw.game_state_interface import GameStateInterface


def fade_to_black_and_back(screen: pygame.surface.Surface) -> None:
    fade_to_color_and_back(screen, pygame.Color("black"))


def fade_out_to_black(screen: pygame.surface.Surface) -> None:
    fade_out_to_color(screen, pygame.Color("black"))


def fade_in_from_black(screen: pygame.surface.Surface) -> None:
    fade_in_from_color(screen, pygame.Color("black"))


def fade_to_color_and_back(screen: pygame.surface.Surface, fade_color: pygame.Color) -> None:
    background_surface = screen.copy()
    color_surface = pygame.surface.Surface(screen.get_size())
    color_surface.fill(fade_color)
    fade_out(screen, background_surface, color_surface)
    fade_out(screen, color_surface, background_surface)


def fade_out_to_color(screen: pygame.surface.Surface, fade_color: pygame.Color) -> None:
    background_surface = screen.copy()
    color_surface = pygame.surface.Surface(screen.get_size())
    color_surface.fill(fade_color)
    fade_out(screen, background_surface, color_surface)


def fade_in_from_color(screen: pygame.surface.Surface, fade_color: pygame.Color) -> None:
    background_surface = screen.copy()
    color_surface = pygame.surface.Surface(screen.get_size())
    color_surface.fill(fade_color)
    fade_out(screen, color_surface, background_surface)


def fade_out(
    screen: pygame.surface.Surface,
    fade_out_from_image: pygame.surface.Surface,
    fade_in_to_image: pygame.surface.Surface,
) -> None:
    clock = pygame.time.Clock()
    for i in range(15, 256, 16):
        fade_in_to_image.set_alpha(i)
        screen.blit(fade_out_from_image, (0, 0))
        screen.blit(fade_in_to_image, (0, 0))
        clock.tick(20)
        pygame.display.flip()


def flickering(screen: pygame.surface.Surface) -> None:
    background_surface = screen.copy()
    flicker_surface = pygame.surface.Surface(screen.get_size())
    flicker_surface.fill("white")
    flicker_surface.set_alpha(128)

    clock = pygame.time.Clock()
    for _ in range(10):
        screen.blit(flicker_surface, (0, 0))
        clock.tick(30)
        pygame.display.flip()

        screen.blit(background_surface, (0, 0))
        clock.tick(30)
        pygame.display.flip()


def pink_tinge(screen: pygame.surface.Surface, flip_buffer: bool = True) -> None:
    color_tinge(screen, pygame.Color(252, 116, 96), flip_buffer)


def color_tinge(screen: pygame.surface.Surface, tinge_color: pygame.Color, flip_buffer: bool = True) -> None:
    pygame.transform.threshold(
        screen,
        screen,
        search_color=pygame.Color("white"),
        threshold=pygame.Color(3, 3, 3),
        set_color=tinge_color,
        inverse_set=True,
    )
    if flip_buffer:
        pygame.display.flip()


def black_red_monochrome_effect(screen: pygame.surface.Surface, flip_buffer: bool = True) -> None:
    red = pygame.Color(255, 62, 24)
    pygame.transform.threshold(
        screen,
        screen,
        search_color=pygame.Color("white"),
        threshold=pygame.Color(3, 3, 3),
        set_color=red,
        inverse_set=True,
    )
    pygame.transform.threshold(
        screen,
        screen,
        search_color=red,
        set_color=pygame.Color("black"),
        inverse_set=False,
    )
    if flip_buffer:
        pygame.display.flip()


rainbow_colors = [
    pygame.Color("red"),
    pygame.Color("orange"),
    pygame.Color("yellow"),
    pygame.Color("green"),
    pygame.Color("blue"),
    pygame.Color("indigo"),
    pygame.Color("violet"),
]


def rainbow_effect(game_state: GameStateInterface) -> None:
    game_info = game_state.get_game_info()

    if game_info.maps[game_state.get_map_name()].tiled_filename is None:
        # On a legacy map, use the original effect
        rainbow_effect_on_water(game_state.screen, game_info.tiles["water"].images[0][0])
    else:
        # On a tiled map, use the new effect
        rainbow_effect_across_background(game_state)


def rainbow_effect_across_background(game_state: GameStateInterface) -> None:
    game_mode = game_state.get_game_mode()

    # Cycle through the rainbow colors
    fade_surface = pygame.surface.Surface(game_state.screen.get_size())
    for _ in range(2):
        for rainbow_color in rainbow_colors:
            fade_surface.fill(rainbow_color)

            def fade_step(fade_surface: pygame.surface.Surface, alpha: int) -> None:
                fade_surface.set_alpha(alpha)
                game_mode.advance_state()
                game_mode.draw_background(flip_buffer=False)
                game_state.screen.blit(fade_surface, (0, 0))

                # Overlay the dialogs
                game_mode.draw_dialogs(flip_buffer=False)

                # Advance a tick
                game_mode.advance_time(flip_buffer=True)

            for j in range(63, 196, 32):
                fade_step(fade_surface, j)

            for j in range(63, 196, 32):
                fade_step(fade_surface, 196 - j)


def rainbow_effect_on_water(screen: pygame.surface.Surface, water_tile: pygame.surface.Surface) -> None:
    orig_screen = screen.copy()
    water_color = pygame.transform.average_color(water_tile, water_tile.get_rect())

    # Cycle through the rainbow colors
    clock = pygame.time.Clock()
    for _ in range(4):
        for rainbow_color in rainbow_colors:
            pygame.transform.threshold(
                screen,
                orig_screen,
                search_color=water_color,
                threshold=pygame.Color(50, 50, 50),
                set_color=rainbow_color,
                inverse_set=True,
            )
            clock.tick(5)
            pygame.display.flip()

    # Restore original screen
    screen.blit(orig_screen, (0, 0))
    pygame.display.flip()


def alter_lighting(
    surface: pygame.surface.Surface,
    saturation_factor: float = 1.0,
    blue_factor: float = 0.0,
    darken_factor: float = 0.0,
) -> pygame.surface.Surface:
    """Return a surface where the saturation is decreased, the blue level is increased, and it is darkened.

    :param saturation_factor: Adjusts the saturation of a pygame.Surface using numpy.
        1.0 for original, 0.0 for grayscale, <1.0 for reduced saturation.
    :param blue_factor: Blue is blit over the unsaturated output with this opacity
        0.0 for original, 1.0 for blue
    :param darken_factor: Black is blit over the blue shifted output with this opacity
        0.0 for original, 1.0 for black
    """
    if saturation_factor == 1.0 and blue_factor == 0.0 and darken_factor == 0.0:
        # In the no-op case return the source surface
        return surface

    # Convert the Surface to a NumPy array for efficient pixel manipulation
    pixels = pygame.surfarray.array3d(surface)

    # TODO: Consider using pygame.transform.hsl(surface, saturation=saturation_factor, lightness=1-darken_factor)

    # Desaturate the image
    if saturation_factor != 1.0:
        # Convert RGB to HSL color space (using a simple approximation or standard formula)
        # Note: A full HSL conversion is complex, this is a simplified method using existing color logic.

        # A common, simpler way to reduce saturation in RGB space is blending with grayscale
        # Create a grayscale version of the image
        grayscale_pixels = np.dot(pixels[..., :3], [0.2989, 0.5870, 0.1140])  # Standard luminosity weights
        grayscale_pixels = np.stack([grayscale_pixels, grayscale_pixels, grayscale_pixels], axis=-1)

        # Blend the original and grayscale versions based on the saturation factor
        # new_color = original * saturation_factor + grayscale * (1 - saturation_factor)
        pixels = (pixels * saturation_factor + grayscale_pixels * (1.0 - saturation_factor)).astype(np.uint8)

    def blend_with_color(pixels: np.typing.NDArray[np.uint8], color: pygame.Color, blend_factor: float) -> None:
        """Perform a blend using the numpy array (could alternately blit) since we've already created it
        for desaturation."""
        if blend_factor != 0.0:
            color_pixels = np.zeros(pixels.shape)
            if color.r != 0 or color.g != 0 or color.b != 0:
                color_pixels[:] = color.r, color.g, color.b
            pixels += ((color_pixels - pixels) * blend_factor).astype(np.uint8)

    # Increase the blue level in the image
    blend_with_color(pixels, pygame.Color("blue"), blue_factor)

    # Darken the image
    blend_with_color(pixels, pygame.Color("black"), darken_factor)

    # Convert the numpy array back to a surface
    altered_surface = pygame.surfarray.make_surface(pixels)

    # Restore alpha channel
    altered_surface.set_alpha(surface.get_alpha())

    # Restore per pixel alphas
    try:
        src_alpha_array = pygame.surfarray.pixels_alpha(surface)
        altered_surface = altered_surface.convert_alpha()
        pygame.surfarray.pixels_alpha(altered_surface)[:] = src_alpha_array[:]
    except ValueError:
        pass

    return altered_surface
