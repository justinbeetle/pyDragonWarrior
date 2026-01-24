#!/usr/bin/env python

"""Module defining LoadingScreen class."""

from typing import Optional

import pygame

from generic_utils.point import Point
from pydw.game_dialog import GameDialog
from pygame_utils.audio_player import AudioPlayer


class LoadingScreen:
    """Loading screen to display while the game info and state is loaded"""

    def __init__(
        self,
        title_image: Optional[pygame.Surface] = None,
        title_music: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.title_image = title_image
        self.title_music = title_music
        self.background_text = "Loading..."

    def set_background_text(self, background_text: str) -> None:
        """Set the text for the bottom of the loading screen."""
        self.background_text = background_text

    def draw(self, flip_buffer: bool = True) -> None:
        """Draw the title image and text message while playing the title music."""

        # Play title music
        if self.title_music:
            AudioPlayer().play_music(self.title_music)

        # Display the title image
        screen = pygame.display.get_surface()
        if screen is None:
            raise ValueError("No screen")
        win_size_pixels = Point(screen.get_size())
        screen.fill("black")
        if self.title_image:
            # Scale to up to 90% of the display width and/or 40% of the height
            title_image_size_px = Point(self.title_image.get_size())
            title_scaling_factor = min(
                0.9 * win_size_pixels.w / title_image_size_px.w,
                0.4 * win_size_pixels.h / title_image_size_px.h,
            )
            if title_image_size_px.w > win_size_pixels.w or title_image_size_px.h > win_size_pixels.h:
                # Scale down for small window sizes
                title_image_size_px *= title_scaling_factor
            else:
                # Scale up for large window sizes
                title_image_size_px *= max(
                    1,
                    int(title_scaling_factor),
                )
            scaled_title_image = pygame.transform.scale(self.title_image, title_image_size_px.get_as_int_tuple())
            title_image_dest_px = Point(
                (win_size_pixels.w - title_image_size_px.w) / 2,
                win_size_pixels.h / 2 - title_image_size_px.h,
            )

            screen.blit(scaled_title_image, title_image_dest_px)

        # Display the text message
        if self.background_text:
            background_text_image = GameDialog.font.render(
                self.background_text,
                GameDialog.anti_alias,
                pygame.Color("white"),
                pygame.Color("black"),
            )
            title_image_dest_px = Point(
                (win_size_pixels.w - background_text_image.get_width()) / 2,
                3 * win_size_pixels.h / 4,
            )
            screen.blit(background_text_image, title_image_dest_px)

        if flip_buffer:
            pygame.display.flip()
