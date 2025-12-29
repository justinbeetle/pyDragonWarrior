#!/usr/bin/env python

"""Define the GameMode base class."""

import logging
from abc import ABC, abstractmethod
from typing import Optional

import pygame

from pydw.dialog_manager import DialogManager
from pygame_utils import game_events
from pygame_utils.audio_player import AudioPlayer

logger = logging.getLogger(__name__)


class GameMode(ABC):
    """Base class for game modes"""

    def __init__(self, dialog_manager: DialogManager) -> None:
        self.dialog_manager = dialog_manager

        # State to maintain and monitor frame rate
        self.clock = pygame.time.Clock()
        self.tick_count = 0

    @abstractmethod
    def game_mode_loop(self) -> None:
        """The game loop for the game mode."""

    @abstractmethod
    def draw_background(self, flip_buffer: bool = False) -> None:
        """Draw the current state of the game mode's background to the display.
        The background is whatever is behind the dialogs."""

    def draw_dialogs(self, flip_buffer: bool = False) -> None:
        """Draw the current set of dialogs to the display."""
        self.dialog_manager.draw_dialogs(flip_buffer)

    def draw(self, flip_buffer: bool = True) -> None:
        """Draw the current state of the game mode to the display."""
        self.draw_background()
        self.draw_dialogs(flip_buffer)

    @abstractmethod
    def advance_state(self) -> bool:
        """Update the state of the game mode for one tick (frame) of game time, if applicable for the mode.
        Return a boolean indicating if the state was updated, as state updates need to be followed by
        drawing the updated state to the display."""

    def advance_time(self, flip_buffer: bool = True, frame_rate_hz: int = 30) -> None:
        """Update the state of the game mode for one tick (frame) of game time, if applicable for the mode.
        Return a boolean indicating if the state was updated, as state updates need to be followed by
        drawing the updated state to the display."""
        # Allow pygame to process internal events for interacting with the OS every frame
        pygame.event.pump()

        self.clock.tick(frame_rate_hz)
        self.tick_count += 1
        if logger.getEffectiveLevel() <= logging.DEBUG:
            desired_fps_logging_period_s = 10
            frames_to_log_after = frame_rate_hz * desired_fps_logging_period_s
            if frames_to_log_after - 1 == self.tick_count % frames_to_log_after:
                logger.debug("%.2f FPS", self.clock.get_fps())

        if flip_buffer:
            pygame.display.flip()

    def advance_tick(self) -> bool:
        """Advance the state of the game mode by one tick (frame), if applicable to the mode.  If the game state
        changes, redraw the display and advance time to maintain the frame rate.  Return a boolean indicating
        if the the state was advanced, the display redrawn, and the buffer flipped.
        """
        if self.advance_state():
            # First do the work
            self.draw(flip_buffer=False)
            # Then advance time to maintain and flip the buffer to maintain a steady frame rate
            self.advance_time(flip_buffer=True)
            return True

        # Allow pygame to process internal events for interacting with the OS every frame
        pygame.event.pump()
        return False

    @abstractmethod
    def get_music(self) -> tuple[Optional[str], Optional[str], Optional[bool], Optional[float], Optional[float]]:
        """Get paramters for invoking AudioPlayer().play_music for the mode.  Returns a tuple matching the arguments
        of AudioPlayer().play_music, except that the first parameter is optional and a None for this parameter
        will result in stopping any playing music."""

    def activate(self) -> None:
        """Handle a transition in control from one game mode to another by drawing the mode and playing music, if
        any."""
        # Play music, if any
        music_rel_file_path1, music_rel_file_path2, interrupt, music_file_start1_sec, music_file_start2_sec = (
            self.get_music()
        )
        if music_rel_file_path1 is None:
            AudioPlayer().stop_music()
        else:
            if interrupt is None:
                interrupt = False
            if music_file_start1_sec is None:
                music_file_start1_sec = 0.0
            if music_file_start2_sec is None:
                music_file_start2_sec = 0.0
            AudioPlayer().play_music(
                music_rel_file_path1, music_rel_file_path2, interrupt, music_file_start1_sec, music_file_start2_sec
            )

        # Draw the display
        self.draw(flip_buffer=True)

        # Clear the event queue for a clean start on the new map
        game_events.clear_events()
