#!/usr/bin/env python

import pygame

from GameTypes import Direction


def fade_to_black_and_back(screen: pygame.Surface) -> None:
    background_surface = screen.copy()
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill(pygame.Color('black'))
    fade_out(screen, background_surface, fade_surface)
    fade_in(screen, background_surface, fade_surface)


def fade_to_black(screen: pygame.Surface) -> None:
    background_surface = screen.copy()
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill(pygame.Color('black'))
    fade_out(screen, background_surface, fade_surface)


def fade_out(screen: pygame.Surface,
             background_surface: pygame.Surface,
             fade_surface: pygame.Surface) -> None:
    for i in range(15, 256, 16):
        fade_surface.set_alpha(i)
        screen.blit(background_surface, (0, 0))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(30)


def fade_in(screen: pygame.Surface,
            background_surface: pygame.Surface,
            fade_surface: pygame.Surface) -> None:
    for i in range(240, -1, -16):
        fade_surface.set_alpha(i)
        screen.blit(background_surface, (0, 0))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(30)


def flickering(screen: pygame.Surface) -> None:
    background_surface = screen.copy()
    flicker_surface = pygame.Surface(screen.get_size())
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


def pink_tinge(screen: pygame.Surface) -> None:
    pygame.transform.threshold(screen,
                               screen,
                               search_color=pygame.Color('white'),
                               threshold=pygame.Color(3, 3, 3),
                               set_color=pygame.Color(252, 116, 96),
                               inverse_set=True)
    pygame.display.flip()


def rainbow_effect(screen: pygame.Surface,
                   water_tile: pygame.Surface) -> None:
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


def scroll_view(screen: pygame.Surface,
                image: pygame.Surface,
                direction: Direction,
                view_rect: pygame.Rect,
                zoom_factor: int,
                image_px_step_size: int,
                update: bool = False) -> None:
    src_rect = None
    dst_rect = None
    zoom_view_rect = screen.get_clip()
    image_w, image_h = image.get_size()

    if direction == Direction.NORTH:
        if view_rect.top > 0:
            screen.scroll(dy=image_px_step_size * zoom_factor)
            view_rect.move_ip(0, -image_px_step_size)
            src_rect = view_rect.copy()
            src_rect.h = image_px_step_size
            dst_rect = zoom_view_rect.copy()
            dst_rect.h = image_px_step_size * zoom_factor
    elif direction == Direction.SOUTH:
        if view_rect.bottom < image_h:
            screen.scroll(dy=-image_px_step_size * zoom_factor)
            view_rect.move_ip(0, image_px_step_size)
            src_rect = view_rect.copy()
            src_rect.h = image_px_step_size
            src_rect.bottom = view_rect.bottom
            dst_rect = zoom_view_rect.copy()
            dst_rect.h = image_px_step_size * zoom_factor
            dst_rect.bottom = zoom_view_rect.bottom
    elif direction == Direction.WEST:
        if view_rect.left > 0:
            screen.scroll(dx=image_px_step_size * zoom_factor)
            view_rect.move_ip(-image_px_step_size, 0)
            src_rect = view_rect.copy()
            src_rect.w = image_px_step_size
            dst_rect = zoom_view_rect.copy()
            dst_rect.w = image_px_step_size * zoom_factor
    elif direction == Direction.EAST:
        if view_rect.right < image_w:
            screen.scroll(dx=-image_px_step_size * zoom_factor)
            view_rect.move_ip(image_px_step_size, 0)
            src_rect = view_rect.copy()
            src_rect.w = image_px_step_size
            src_rect.right = view_rect.right
            dst_rect = zoom_view_rect.copy()
            dst_rect.w = image_px_step_size * zoom_factor
            dst_rect.right = zoom_view_rect.right
    if src_rect is not None and dst_rect is not None:
        pygame.transform.scale(image.subsurface(src_rect),
                               dst_rect.size,
                               screen.subsurface(dst_rect))
        if update:
            pygame.display.update(zoom_view_rect)
