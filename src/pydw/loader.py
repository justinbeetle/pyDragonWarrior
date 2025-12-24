#!/usr/bin/env python

"""Module defining the Loader class."""

from typing import Optional

from argparse import Namespace
import os
import tarfile
import traceback

import pygame

from generic_utils.point import Point

from pygame_utils.audio_player import AudioPlayer
from pygame_utils import game_events

from pydw.game_dialog import GameDialog
from pydw.game_info import GameInfo
from pydw.game_state import GameState
from pydw.launcher import Launcher
from pydw.loading_screen import LoadingScreen


class Loader:
    """The Loader class handles pygame initialization and termination and loads the game assets.  With both licensed
    and unlicensed assets, it may make several attempts to load the game assets.  If the game assets are successfully
    loaded, Loader then runs the game."""

    # FUTURE: Push these into the configuration?
    unscaled_tile_size_pixels = 16
    desired_tile_scaling_factor = 3

    def __init__(self, args: Namespace, base_path: str, saves_path: str) -> None:
        self.args = args
        self.verbose = args.verbose
        self.base_path = base_path
        self.saves_path = saves_path

        GameDialog.force_use_menus_for_text_entry = args.gamepad

        # The tile size becomes fixed in determine_tile_size, which meaningfully sets these members.
        self.tile_size_pixels = Loader.unscaled_tile_size_pixels * Loader.desired_tile_scaling_factor
        self.win_size_tiles = Point(0, 0)

        self.loading_screen: Optional[LoadingScreen] = None

    def run(self) -> int:
        """Attempt to initialize pygame, load the game assets, and run the game.  Returns an exit code."""

        # Register the focus gain handler - needed so that we don't end up with an empty black screen after losing focus
        game_events.set_focus_gain_handler(self.focus_gain_handlder)
        game_events.set_window_resize_handler(self.window_resize_handlder)

        try:
            self.initialize_pygame()
            self.determine_tile_size()
            game_state = self.load_game_assets()
            if game_state:
                return game_state.run(self.args.save)
        finally:
            self.terminate_pygame()

        return 1

    def initialize_pygame(self) -> None:
        """Initialize pygame"""
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption(Launcher.application_name)
        icon_image_filename = os.path.join(self.base_path, "data", "images", "icon.png")
        if os.path.exists(icon_image_filename):
            try:
                icon_image = pygame.image.load(icon_image_filename)
                pygame.display.set_icon(icon_image)
            except Exception:
                print("ERROR: Failed to load", icon_image_filename, flush=True)
        self.initialize_pygame_display()

    def initialize_pygame_display(self) -> None:
        """Initialize the pygame display"""
        if self.args.width and self.args.height:
            # Initialize in a window with an Integer number of vertical and horizontal tiles
            desired_win_size_pixels = Point(self.args.width, self.args.height)
            win_size_pixels = desired_win_size_pixels // self.tile_size_pixels * self.tile_size_pixels
            pygame.display.set_mode(win_size_pixels.get_as_int_tuple(), pygame.RESIZABLE | pygame.SRCALPHA)
        else:
            # Find index of largest display by total pixels
            largest_display_index = largest_display_size = 0
            for display_index, (display_x_size, display_y_size) in enumerate(pygame.display.get_desktop_sizes()):
                current_display_size = display_x_size * display_y_size
                if current_display_size > largest_display_size:
                    largest_display_index = display_index
                    largest_display_size = current_display_size

            # Initialize fullscreen on the largest display
            pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA,
                display=largest_display_index,
            )

    def determine_tile_size(self) -> None:
        """Determine the tile size and window size in tiles.  Sets self.tile_size_pixels and self.win_size_tiles."""

        screen = pygame.display.get_surface()
        if screen is None:
            raise ValueError("No screen")
        tile_scaling_factor = Loader.desired_tile_scaling_factor
        win_size_pixels = Point(screen.get_size())
        self.win_size_tiles = win_size_pixels / self.tile_size_pixels

        # Determine if the tile scaling factor should be reduced
        # Base this decision on the size of the message dialog
        dialog_size_tiles = GameDialog.get_message_dialog_size_tiles(self.win_size_tiles)
        while tile_scaling_factor > 1 and (dialog_size_tiles.x < 10 or dialog_size_tiles.y < 5):
            tile_scaling_factor -= 1

            # Recompute the sizes after reducing tile_scaling_factor
            self.tile_size_pixels = self.unscaled_tile_size_pixels * tile_scaling_factor
            self.win_size_tiles = win_size_pixels / self.tile_size_pixels
            dialog_size_tiles = GameDialog.get_message_dialog_size_tiles(self.win_size_tiles)

        if self.verbose and tile_scaling_factor < self.desired_tile_scaling_factor:
            print(f"Reduced tile scaling factor to {tile_scaling_factor}", flush=True)

    def load_game_assets(self) -> Optional[GameState]:
        """Attempt to load the game assets, returning a GameState on success."""

        if self.args.config:
            return self.load_from_game_xml(self.args.config)

        # Attempt to load game using the licensed assets
        if not self.args.force_use_unlicensed_assets:
            game_xml_path = os.path.join(self.base_path, "data", "game_licensed_assets.xml")
            game_state = self.load_from_game_xml(game_xml_path, "Failed to load using licensed assets")
            if game_state:
                return game_state

            # If failed to load, retry after extracting asset pack (if present)
            asset_pack_path = os.path.join(self.base_path, "licensed_assets.tgz")
            if os.path.exists(asset_pack_path):
                self.extract_asset_pack(asset_pack_path)

                # Retry loading using the licensed assets
                game_state = self.load_from_game_xml(
                    game_xml_path, "Failed to load licensed assets after extracting from asset pack"
                )
            if game_state:
                return game_state

        # Fallback to using unlicensed assets if the licensed weren't present or didn't work
        game_xml_path = os.path.join(self.base_path, "data", "game.xml")
        return self.load_from_game_xml(game_xml_path, "ERROR: Failed to load unlicensed assets")

    def load_from_game_xml(self, game_xml_path: str, error_msg: Optional[str] = None) -> Optional[GameState]:
        """Load the game resources based on the specified xml file."""
        try:
            # Load the minimum amount of game info to launch the loading screen
            title_image, title_music = GameInfo.static_init(
                self.base_path,
                game_xml_path,
                self.win_size_tiles,
                self.tile_size_pixels,
            )
            self.loading_screen = LoadingScreen(title_image, title_music)
            self.loading_screen.draw()

            # Load the full game state
            return GameState(
                self.saves_path, self.base_path, game_xml_path, self.win_size_tiles, self.tile_size_pixels, self.verbose
            )
        except Exception:
            if self.verbose:
                if error_msg is None:
                    error_msg = f"Failed to load game using {game_xml_path}"
                print(f"ERROR: {error_msg}", flush=True)
                traceback.print_exc()

        return None

    def extract_asset_pack(self, asset_pack_path: str) -> None:
        """Extract asset pack without overwriting existing files."""
        with tarfile.open(asset_pack_path) as asset_pack_file:
            if self.verbose:
                print("Extracting assets...", flush=True)
            for asset_file in asset_pack_file:
                if not os.path.exists(os.path.join(self.base_path, asset_file.name)):
                    asset_pack_file.extract(asset_file, filter="data")
                    if self.verbose:
                        print(f"   {asset_file.name}", flush=True)

    def focus_gain_handlder(self) -> None:
        """Handler for focus gain events to render the latest content to the display surface.
        Since pygame 2.5.2, the display surface is cleared when focus is lost and gained
        (see https://github.com/pygame/pygame/issues/4133).
        """
        if self.loading_screen:
            if self.verbose:
                print("Re-drawing to the display due to invocation of focus_gain_handlder", flush=True)
            self.loading_screen.draw()

    def window_resize_handlder(self) -> None:
        """Handler for window resize events needed to implement a resizeable window."""
        if self.loading_screen:
            if self.verbose:
                print("Re-drawing to the display due to invocation of window_resize_handlder", flush=True)
            self.loading_screen.draw()

    def terminate_pygame(self) -> None:
        """Terminate pygame"""
        AudioPlayer().terminate()
        pygame.joystick.quit()
        pygame.quit()
