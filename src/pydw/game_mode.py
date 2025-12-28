#!/usr/bin/env python

"""Define the GameMode base class."""

from abc import ABC, abstractmethod

from pydw.dialog_manager import DialogManager


class GameMode(ABC):
    """Base class for game modes"""

    def __init__(self, dialog_manager: DialogManager) -> None:
        self.dialog_manager = dialog_manager

    @abstractmethod
    def game_mode_loop(self) -> None:
        """The game loop for the game mode."""

    @abstractmethod
    def draw_background(self, flip_buffer: bool = False) -> None:
        """Draw the current state of the game mode's background to the display.
        The background is whatever is behind the dialogs."""

    def advance_tick(self) -> bool:
        """Advance the state of the game mode by one tick (frame), if applicable to the mode.  Return a bool indicating
        if the the state was advanced, which would then require re-drawing the game mode to the display."""
        return False

    def draw(self, flip_buffer: bool = True) -> None:
        """Draw the current state of the game mode to the display."""
        self.draw_background()
        self.dialog_manager.draw_dialogs(flip_buffer)
