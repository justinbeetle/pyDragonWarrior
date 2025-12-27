#!/usr/bin/env python

"""Module defining DialogManager class and its outgoing DialogManagerMediator interface."""

from typing import List, Optional, Union

from abc import ABC, abstractmethod
import logging

import pygame

from pydw.game_dialog import GameDialog

logger = logging.getLogger(__name__)


class DialogManagerMediator(ABC):
    """DialogManager's outgoing interface."""

    @abstractmethod
    def draw_background(self, flip_buffer: bool = False) -> None:
        """Draw the current state of the game mode's background to the display.
        The background is whatever is behind the dialogs."""

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
        self.message_dialog_has_focus = True

        # Potentially cascading dialogs that may eclipse other dialogs
        self.high_priority_cascading_dialogs: List[GameDialog] = []
        self.cascading_dialogs: List[GameDialog] = []

    def add_status_dialog(self, dialog: GameDialog, flip_buffer: bool = True, draw_display: bool = False) -> None:
        """Add a status dialog and optionally redraw the display."""
        old_dialog = self.status_dialog
        self.status_dialog = dialog

        if draw_display:
            # If the old dialog is entirely covered by the new dialog, only draw the dialogs.  Else draw everything.
            if old_dialog is None:
                self.draw_dialogs(flip_buffer)
            else:
                old_rect = old_dialog.get_screen_rect()
                new_rect = dialog.get_screen_rect()
                if old_rect.clip(new_rect) == old_rect:
                    self.draw_dialogs(flip_buffer)
                else:
                    self.draw(flip_buffer)

    def remove_status_dialog(self, flip_buffer: bool = True, draw_display: bool = False) -> None:
        """Remove the status dialog and redraw the display."""
        if self.status_dialog:
            self.status_dialog = None

            if draw_display:
                self.draw(flip_buffer)

    def add_message_dialog(self, dialog: GameDialog, flip_buffer: bool = True, draw_display: bool = False) -> None:
        """Add a message dialog and redraw the display."""
        self.message_dialog = dialog

        if draw_display:
            self.draw_dialogs(flip_buffer)

    def remove_message_dialog(self, flip_buffer: bool = True, draw_display: bool = False) -> None:
        """Remove the message dialog and redraw the display."""
        if self.message_dialog:
            self.message_dialog = None

            if draw_display:
                self.draw(flip_buffer)

    def add_high_priority_cascading_dialog(
        self, dialog: GameDialog, menu_selection: Optional[Union[str, tuple[int, int]]] = None, flip_buffer: bool = True
    ) -> GameDialog:
        """Add a high priority cascading dialog and redraw the display."""
        return self._add_cascading_dialog_helper(
            self.high_priority_cascading_dialogs, dialog, menu_selection, flip_buffer
        )

    def add_cascading_dialog(
        self, dialog: GameDialog, menu_selection: Optional[Union[str, tuple[int, int]]] = None, flip_buffer: bool = True
    ) -> GameDialog:
        """Add a cascading dialog and redraw the display."""
        return self._add_cascading_dialog_helper(self.cascading_dialogs, dialog, menu_selection, flip_buffer)

    def _add_cascading_dialog_helper(
        self,
        cascading_dialogs: List[GameDialog],
        dialog: GameDialog,
        menu_selection: Optional[Union[str, tuple[int, int]]] = None,
        flip_buffer: bool = True,
    ) -> GameDialog:
        """Helper for adding either high or regular priority cascading dialog."""
        cascading_dialogs.append(dialog)
        if menu_selection is not None:
            if isinstance(menu_selection, str):
                dialog.set_selected_menu_option(menu_selection)
            else:
                dialog.set_selected_menu_position(menu_selection[0], menu_selection[1])
        self.draw_dialogs(flip_buffer)
        return dialog

    def remove_cascading_dialog(self, flip_buffer: bool = True) -> None:
        """Remove a high priority cascading dialog and redraw the display."""
        if 0 < len(self.high_priority_cascading_dialogs):
            removed_dialog = self.high_priority_cascading_dialogs.pop()
            logger.debug("Removed dialog with title %s", removed_dialog.title)
            self.draw(flip_buffer)
        elif 0 < len(self.cascading_dialogs):
            removed_dialog = self.cascading_dialogs.pop()
            logger.debug("Removed dialog with title %s", removed_dialog.title)
            self.draw(flip_buffer)

    def clear_cascading_dialogs(self, flip_buffer: bool = True) -> None:
        """Remove all cascading dialogs and redraw the display."""
        if 0 < len(self.cascading_dialogs) or 0 < len(self.high_priority_cascading_dialogs):
            self.high_priority_cascading_dialogs.clear()
            self.cascading_dialogs.clear()
            self.draw(flip_buffer)

    def draw_dialogs(self, flip_buffer: bool = True) -> None:
        """Draw the current set of dialogs to the display."""
        # Determine the font (and border) color for the dialogs
        # Use a base color depending on party health
        # Use the base color for the foreground dialog(s) and a darker colore for background dialogs
        has_high_priority_cascading_dialogs = 0 < len(self.high_priority_cascading_dialogs)
        has_cascading_dialogs = 0 < len(self.cascading_dialogs)
        foreground_font_color = self.mediator.get_foreground_dialog_font_color()
        background_font_color = foreground_font_color.lerp(pygame.Color("black"), 0.4)

        # Render each of the dialogs using the appropriate color
        screen = pygame.display.get_surface()
        if screen is None:
            raise ValueError("No screen")
        if self.status_dialog:
            dialog_color = background_font_color if has_high_priority_cascading_dialogs else foreground_font_color
            self.status_dialog.set_font_color(dialog_color)
            self.status_dialog.blit(screen)
        if self.message_dialog and not self.message_dialog_has_focus:
            dialog_color = (
                background_font_color
                if has_high_priority_cascading_dialogs or has_cascading_dialogs
                else foreground_font_color
            )
            self.message_dialog.set_font_color(dialog_color)
            self.message_dialog.blit(screen)
        if has_cascading_dialogs:
            for dialog in self.cascading_dialogs[:-1]:
                dialog.set_font_color(background_font_color)
                dialog.blit(screen)
            dialog_color = (
                background_font_color
                if has_high_priority_cascading_dialogs
                or (self.message_dialog is not None and self.message_dialog_has_focus)
                else foreground_font_color
            )
            self.cascading_dialogs[-1].set_font_color(dialog_color)
            self.cascading_dialogs[-1].blit(screen)
        if self.message_dialog and self.message_dialog_has_focus:
            dialog_color = background_font_color if has_high_priority_cascading_dialogs else foreground_font_color
            self.message_dialog.set_font_color(dialog_color)
            self.message_dialog.blit(screen)
        if has_high_priority_cascading_dialogs:
            for dialog in self.high_priority_cascading_dialogs[:-1]:
                dialog.set_font_color(background_font_color)
                dialog.blit(screen)
            self.high_priority_cascading_dialogs[-1].set_font_color(foreground_font_color)
            self.high_priority_cascading_dialogs[-1].blit(screen)
        if flip_buffer:
            pygame.display.flip()

    def draw(self, flip_buffer: bool = True) -> None:
        """Draw the current state of the game (background and dialogs) to the display."""
        self.mediator.draw_background(False)
        self.draw_dialogs(flip_buffer)
