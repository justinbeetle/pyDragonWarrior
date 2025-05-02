#!/usr/bin/env python

"""Module defining DialogManager class and its outgoing DialogManagerMediator interface."""

from typing import List, Optional

from abc import ABC, abstractmethod

import pygame

from pydw.game_dialog import GameDialog


class DialogManagerMediator(ABC):
    """DialogManager's outgoing interface."""

    @abstractmethod
    def draw(self, flip_buffer: bool = True) -> None:
        """Draw the full display (background and dialogs.  Should invoke DialogManager's draw_dialogs method."""

    @abstractmethod
    def get_foreground_dialog_font_color(self) -> pygame.Color:
        """Get the color to use for the font and border of the foreground dialogs."""


class DialogManager:
    """DialogManager for handling the various game dialogs."""

    def __init__(self, mediator: DialogManagerMediator) -> None:
        self.mediator = mediator

        # Status dialog is for health and status information - there should only ever be one of these at a time
        # and nothing should obscure it (when present)
        self.status_dialog: Optional[GameDialog] = None

        # Message dialog is for most game interactions, including conversations and menu selections taking place
        # within the message dialog.
        self.message_dialog: Optional[GameDialog] = None

        # Potentially cascading dialogs that may eclipse other dialogs
        self.cascading_dialogs: List[GameDialog] = []

    def add_status_dialog(self, dialog: GameDialog, flip_buffer: bool = True) -> None:
        """Add a status dialog."""
        self.status_dialog = dialog

        # Need to draw the whole screen as the status dialog type may change and be smaller than the previous one
        self.mediator.draw(flip_buffer)

    def remove_status_dialog(self, flip_buffer: bool = True) -> None:
        """Remove the status dialog."""
        if self.status_dialog:
            self.status_dialog = None
            self.mediator.draw(flip_buffer)

    def add_message_dialog(self, dialog: GameDialog, flip_buffer: bool = True) -> None:
        """Add a message dialog."""
        self.message_dialog = dialog
        self.draw_dialogs(flip_buffer)

    def remove_message_dialog(self, flip_buffer: bool = True) -> None:
        """Remove the message dialog."""
        if self.message_dialog:
            self.message_dialog = None
            self.mediator.draw(flip_buffer)

    def add_cascading_dialog(self, dialog: GameDialog, flip_buffer: bool = True) -> None:
        """Add a cascading dialog."""
        self.cascading_dialogs.append(dialog)
        self.draw_dialogs(flip_buffer)

    def remove_cascading_dialog(self, flip_buffer: bool = True) -> None:
        """Remove a cascading dialog."""
        if 0 < len(self.cascading_dialogs):
            self.cascading_dialogs.pop()
            self.mediator.draw(flip_buffer)

    def clear_cascading_dialogs(self, flip_buffer: bool = True) -> None:
        """Remove all cascading dialogs."""
        if 0 < len(self.cascading_dialogs):
            self.cascading_dialogs.clear()
            self.mediator.draw(flip_buffer)

    def draw_dialogs(self, flip_buffer: bool = True) -> None:
        """Draw the current set of dialogs to the display."""
        # Determine the font (and border) color for the dialogs
        # Use a base color depending on party health
        # Use the base color for the foreground dialog(s) and a darker colore for background dialogs
        has_cascading_dialogs = 0 < len(self.cascading_dialogs)
        foreground_font_color = self.mediator.get_foreground_dialog_font_color()
        background_font_color = foreground_font_color.lerp(pygame.Color("black"), 0.4)

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
