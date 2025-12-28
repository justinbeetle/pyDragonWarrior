#!/usr/bin/env python

"""Define the GameMode base class."""

import logging
from abc import ABC, abstractmethod

import pygame

from pydw.dialog_manager import DialogManager

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

    def advance_time(self, flip_buffer: bool = True) -> None:
        """Update the state of the game mode for one tick (frame) of game time, if applicable for the mode.
        Return a boolean indicating if the state was updated, as state updates need to be followed by
        drawing the updated state to the display."""
        # Allow pygame to process internal events for interacting with the OS every frame
        pygame.event.pump()

        DESIRED_FRAME_RATE_HZ = 30
        self.clock.tick(DESIRED_FRAME_RATE_HZ)
        self.tick_count += 1
        if logger.getEffectiveLevel() <= logging.DEBUG:
            DESIRED_FPS_LOGGING_RATE_S = 10
            FRAMES_TO_LOG_AFTER = DESIRED_FRAME_RATE_HZ * DESIRED_FPS_LOGGING_RATE_S
            if FRAMES_TO_LOG_AFTER - 1 == self.tick_count % FRAMES_TO_LOG_AFTER:
                logger.debug("%.2f FPS", self.clock.get_fps())

        if flip_buffer:
            pygame.display.flip()

    def advance_tick(self) -> bool:
        """Advance the state of the game mode by one tick (frame), if applicable to the mode.  If the game state
        changes, redraw the display and advance time to maintain the frame rate.  Return a boolean indicating
        if the the state was advanced, the display redrawn, and the buffer flipped.
        """
        was_state_advanced = self.advance_state()
        if self.advance_state():
            # First do the work
            self.draw(flip_buffer=False)
            # Then advance time to maintain and flip the buffer to maintain a steady frame rate
            self.advance_time(flip_buffer=True)
            return True

        # Allow pygame to process internal events for interacting with the OS every frame
        pygame.event.pump()
        return False
