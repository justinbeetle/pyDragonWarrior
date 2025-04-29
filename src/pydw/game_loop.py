#!/usr/bin/env python

from typing import cast, List, Optional

# import datetime
import glob
import os
import random

import pygame

from generic_utils.point import Point

from pygame_utils import game_events

from pydw.exploring import Exploring
from pydw.game_dialog import GameDialog
from pydw.game_info import GameInfo
from pydw.game_mode import GameMode
from pydw.game_state import GameState

from pydw.loading_screen import LoadingScreen
from pydw.main_menu import MainMenu


class GameLoop:
    def __init__(
        self,
        saves_path: str,
        base_path: str,
        game_xml_path: str,
        desired_win_size_pixels: Optional[Point],
        unscaled_tile_size_pixels: int,
        desired_tile_scaling_factor: int,
        verbose: bool = False,
    ) -> None:
        self.saves_path = saves_path
        self.base_path = base_path
        self.game_xml_path = game_xml_path
        self.desired_win_size_pixels = desired_win_size_pixels
        self.unscaled_tile_size_pixels = unscaled_tile_size_pixels
        self.desired_tile_scaling_factor = desired_tile_scaling_factor
        self.verbose = verbose
        self.current_game_mode: Optional[GameMode] = None

        # Setup state needed for call to determine_tile_size, which also initializes the display
        self.tile_scaling_factor = self.desired_tile_scaling_factor
        self.tile_size_pixels = (
            self.unscaled_tile_size_pixels * self.tile_scaling_factor
        )
        self.initialize_display()
        self.win_size_tiles = Point(
            0, 0
        )  # Gets set meaningfully in determine_window_sizing
        self.determine_tile_size()

        # Load the minimum amount of game info to launch the loading screen
        title_image, title_music = GameInfo.static_init(
            self.base_path,
            self.game_xml_path,
            self.win_size_tiles,
            self.tile_size_pixels,
        )
        self.loading_screen: Optional[LoadingScreen] = LoadingScreen(
            title_image, title_music
        )
        self.loading_screen.render()

    def initialize_display(self) -> None:
        """Initialize the pygame display"""
        if self.desired_win_size_pixels is None:
            # Find index of largest display
            largest_display_index = largest_display_size = 0
            for display_index, (display_x_size, display_y_size) in enumerate(
                pygame.display.get_desktop_sizes()
            ):
                current_display_size = display_x_size * display_y_size
                if current_display_size > largest_display_size:
                    largest_display_index = display_index
                    largest_display_size = current_display_size

            # Launch fullscreen on the largest display
            pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA,
                display=largest_display_index,
            )
        else:
            win_size_pixels = (
                self.desired_win_size_pixels
                // self.tile_size_pixels
                * self.tile_size_pixels
            )
            pygame.display.set_mode(
                win_size_pixels.get_as_int_tuple(),
                pygame.RESIZABLE | pygame.SRCALPHA,
            )

    def determine_tile_size(self) -> None:
        """Determine the tile size and window size in tiles."""
        win_size_pixels = Point(pygame.display.get_surface().get_size())
        self.win_size_tiles = win_size_pixels / self.tile_size_pixels

        # Determine if the tile scaling factor should be reduced
        # Base this decision on the size of the message dialog
        dialog_size_tiles = GameDialog.get_message_dialog_size_tiles(
            self.win_size_tiles
        )
        while self.tile_scaling_factor > 1 and (
            dialog_size_tiles.x < 10 or dialog_size_tiles.y < 5
        ):
            self.tile_scaling_factor -= 1

            # Recompute the sizes after reducing tile_scaling_factor
            self.tile_size_pixels = (
                self.unscaled_tile_size_pixels * self.tile_scaling_factor
            )
            self.win_size_tiles = win_size_pixels / self.tile_size_pixels
            dialog_size_tiles = GameDialog.get_message_dialog_size_tiles(
                self.win_size_tiles
            )

        if self.verbose and self.tile_scaling_factor < self.desired_tile_scaling_factor:
            print(
                f"Reduced tile scaling factor to {self.tile_scaling_factor}", flush=True
            )

    def run(self, pc_name_or_file_name: Optional[str] = None) -> None:
        # Register the focus gain handler - needed so that we don't end up with an empty black screen after losing focus
        game_events.set_focus_gain_handler(self.focus_gain_handlder)
        game_events.set_window_resize_handler(self.window_resize_handlder)

        # Load the full game state
        game_state = GameState(
            self.saves_path,
            self.base_path,
            self.game_xml_path,
            self.win_size_tiles,
            self.tile_size_pixels,
        )

        # Transition from the loading screen to the main menu
        self.loading_screen = None
        self.current_game_mode = MainMenu(game_state, pc_name_or_file_name)
        self.current_game_mode.game_mode_loop()

        # Transition from the main menu to exploring
        if game_state.is_running:
            self.current_game_mode = Exploring(game_state, self.verbose)
            self.current_game_mode.game_mode_loop()

    def focus_gain_handlder(self) -> None:
        print("Rendering due to invocation of focus_gain_handlder", flush=True)
        if self.current_game_mode:
            self.current_game_mode.render()
        elif self.loading_screen:
            self.loading_screen.render()

    def window_resize_handlder(self) -> None:
        print("Rendering due to invocation of window_resize_handlder", flush=True)
        # TODO: What needs to be done to resize things on the fly?
        # self.determine_tile_size()
        if self.current_game_mode:
            self.current_game_mode.resize()
        elif self.loading_screen:
            self.loading_screen.render()
