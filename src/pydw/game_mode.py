#!/usr/bin/env python

"""Define the GameMode base class."""

from typing import List, Optional

from abc import ABC, abstractmethod

import pygame

from generic_utils.point import Point

from pygame_utils.audio_player import AudioPlayer

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
    def draw_background(self, flip_buffer: bool = False) -> None:
        """Render the current state of the game mode's background to the display.
        The background is whatever is behind the dialogs."""

    def draw_dialogs(self, flip_buffer: bool = True) -> None:
        # Determine the font (and border) color for the dialogs
        # Use a base color depending on party health
        # Use the base color for the foreground dialog(s) and a darker colore for background dialogs
        has_cascading_dialogs = 0 < len(self.cascading_dialogs)
        if self.game_state.get_hero_party().has_low_health():
            foreground_font_color = GameDialog.LOW_HEALTH_FONT_COLOR
        else:
            foreground_font_color = GameDialog.NOMINAL_HEALTH_FONT_COLOR
        background_font_color = foreground_font_color.lerp(pygame.Color("black"), 0.2)

        # Render each of the dialogs using the appropriate color
        screen = pygame.display.get_surface()
        if self.status_dialog:
            dialog_color = background_font_color if has_cascading_dialogs else foreground_font_color
            self.status_dialog.set_font_color(dialog_color)
            self.status_dialog.blit(screen)
        if self.message_dialog:
            dialog_color = background_font_color if has_cascading_dialogs else foreground_font_color
            self.message_dialog.set_font_color(dialog_color)
            self.message_dialog.blit(screen)
        if has_cascading_dialogs:
            for dialog in self.cascading_dialogs[:-1]:
                dialog.set_font_color(background_font_color)
                dialog.blit(screen)
            self.cascading_dialogs[-1].set_font_color(foreground_font_color)
            self.cascading_dialogs[-1].blit(screen)
        if flip_buffer:
            pygame.display.flip()

    def draw(self, flip_buffer: bool = True) -> None:
        """Render the current state of the game mode to the display."""
        self.draw_background()
        self.draw_dialogs(flip_buffer)

    def resize(self) -> None:
        """Handle a resize of the display, including drawing to the display."""
        # TODO: Need to resize and replace the dialogs!!!
        self.draw()

    def add_status_dialog(self, dialog: GameDialog, flip_buffer: bool = True) -> None:
        """Add a status dialog."""
        self.status_dialog = dialog

        # Need to draw the whole screen as the status dialog type may change and be smaller than the previous one
        self.draw(flip_buffer)

    def remove_status_dialog(self, flip_buffer: bool = True) -> None:
        """Remove the status dialog."""
        if self.status_dialog:
            self.status_dialog = None
            self.draw(flip_buffer)

    def add_message_dialog(self, dialog: GameDialog, flip_buffer: bool = True) -> None:
        """Add a message dialog."""
        self.message_dialog = dialog
        self.draw_dialogs(flip_buffer)

    def remove_message_dialog(self, flip_buffer: bool = True) -> None:
        """Remove the message dialog."""
        if self.message_dialog:
            self.message_dialog = None
            self.draw(flip_buffer)

    def add_cascading_dialog(self, dialog: GameDialog, flip_buffer: bool = True) -> None:
        """Add a cascading dialog."""
        self.cascading_dialogs.append(dialog)
        self.draw_dialogs(flip_buffer)

    def remove_cascading_dialog(self, flip_buffer: bool = True) -> None:
        """Remove a cascading dialog."""
        if 0 < len(self.cascading_dialogs):
            self.cascading_dialogs.pop()
            self.draw(flip_buffer)

    def clear_cascading_dialogs(self, flip_buffer: bool = True) -> None:
        """Remove all cascading dialogs."""
        if 0 < len(self.cascading_dialogs):
            self.cascading_dialogs.clear()
            self.draw(flip_buffer)

    def handle_quit(self, force: bool = False) -> None:
        if force:
            self.game_state.is_running = False
            return

        AudioPlayer().play_sound("select")
        menu_dialog = GameDialog.create_yes_no_menu(Point(1, 1), "Do you really want to quit?")
        self.add_cascading_dialog(menu_dialog)
        menu_result = self.gde.get_menu_result(menu_dialog, allow_quit=False)
        if menu_result is not None and menu_result == "YES":
            self.game_state.is_running = False
            return
        self.remove_cascading_dialog()
