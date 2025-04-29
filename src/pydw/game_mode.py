#!/usr/bin/env python

"""Define the GameMode base class."""

from typing import List, Optional

from abc import ABC, abstractmethod

import pygame

from pydw.game_dialog import GameDialog
from pydw.game_dialog_evaluator import GameDialogEvaluator
from pydw.game_state import GameState


class GameMode(ABC):
    """Base class for game modes"""

    def __init__(self, game_state: GameState) -> None:
        # Status dialog is for health and status information - there should only ever be one of these at a time
        # and nothing should obscure it (when present)
        self.status_dialog: Optional[GameDialog] = None

        # Message dialog is for most game interactions, including conversations and menu selections taking place
        # within the message dialog.
        self.message_dialog: Optional[GameDialog] = None

        # Potentially cascading dialogs that may eclipse other dialogs
        self.cascading_dialogs: List[GameDialog] = []

        self.game_state = game_state
        self.game_info = game_state.get_game_info()
        self.gde = GameDialogEvaluator(game_state)
        self.gde.update_default_dialog_font_color()

    @abstractmethod
    def game_mode_loop(self) -> None:
        """The game loop for the game mode."""

    @abstractmethod
    def render_background(self, flip_buffer: bool = False) -> None:
        """Render the current state of the game mode's background to the display.
        The background is whatever is behind the dialogs."""

    def render(self, flip_buffer: bool = True) -> None:
        """Render the current state of the game mode to the display."""
        self.render_background()
        screen = pygame.display.get_surface()
        if self.status_dialog:
            self.status_dialog.blit(screen)
        if self.message_dialog:
            self.message_dialog.blit(screen)
        for dialog in self.cascading_dialogs:
            dialog.blit(screen)
        if flip_buffer:
            pygame.display.flip()

    def resize(self) -> None:
        """Handle a resize of the display, including rendering to the display."""
        # TODO: Need to resize and replace the dialogs!!!
        self.render()

    def add_status_dialog(self, dialog: GameDialog, flip_buffer: bool = True) -> None:
        """Add a status dialog."""
        self.status_dialog = dialog
        screen = pygame.display.get_surface()
        dialog.blit(screen)
        if flip_buffer:
            pygame.display.flip()

    def remove_status_dialog(self, flip_buffer: bool = True) -> None:
        """Remove the status dialog."""
        if self.status_dialog:
            self.status_dialog = None
            self.render(flip_buffer)

    def add_message_dialog(self, dialog: GameDialog, flip_buffer: bool = True) -> None:
        """Add a message dialog."""
        self.message_dialog = dialog
        screen = pygame.display.get_surface()
        dialog.blit(screen)
        if flip_buffer:
            pygame.display.flip()

    def remove_message_dialog(self, flip_buffer: bool = True) -> None:
        """Remove the message dialog."""
        if self.message_dialog:
            self.message_dialog = None
            self.render(flip_buffer)

    def add_cascading_dialog(self, dialog: GameDialog, flip_buffer: bool = True) -> None:
        """Add a cascading dialog."""
        self.cascading_dialogs.append(dialog)
        screen = pygame.display.get_surface()
        dialog.blit(screen)
        if flip_buffer:
            pygame.display.flip()

    def remove_cascading_dialog(self, flip_buffer: bool = True) -> None:
        """Remove a cascading dialog."""
        if 0 < len(self.cascading_dialogs):
            self.cascading_dialogs.pop()
            self.render(flip_buffer)

    def clear_cascading_dialogs(self, flip_buffer: bool = True) -> None:
        """Remove all cascading dialogs."""
        self.cascading_dialogs.clear()
        self.render(flip_buffer)
