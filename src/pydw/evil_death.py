#!/usr/bin/env python

"""Module defining MainMenu class."""

from typing import Optional

import pygame

from pydw.game_mode import GameMode
from pydw.game_state_interface import GameStateInterface
from pygame_utils import game_events, surface_effects


class EvilDeath(GameMode):
    """Game mode for the endless loop of being an evil, betrayed minion."""

    def __init__(self, game_state: GameStateInterface) -> None:
        super().__init__(game_state.get_dialog_manager())
        self.game_state = game_state
        self.background_game_mode = game_state.get_game_mode()

    def game_mode_loop(self) -> None:
        """The game loop for the being an evil, betrayed minion - where quiting is the only escape."""
        self.activate()
        while self.game_state.is_running:
            events = game_events.get_events()
            if 0 == len(events):
                self.advance_tick()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.handle_quit()
                elif event.type == pygame.QUIT:
                    self.game_state.handle_quit(force=True)

    def draw_background(self, flip_buffer: bool = False) -> None:
        """Draw the background for the main menu, which is the same as the background for the loading screen."""
        self.background_game_mode.draw_background(flip_buffer=flip_buffer)

    def draw(self, flip_buffer: bool = True) -> None:
        """Draw the current state of the game mode to the display."""
        self.background_game_mode.draw(flip_buffer=False)
        surface_effects.black_red_monochrome_effect(self.game_state.screen, flip_buffer=False)
        self.game_state.get_game_map().draw_character_sprites()

        # Flip the screen buffer
        if flip_buffer:
            pygame.display.flip()

    def advance_state(self) -> bool:
        """Update the state of the game mode for one tick (frame) of game time, if applicable for the mode.
        Return a boolean indicating if the state was updated, as state updates need to be followed by
        drawing the updated state to the display."""
        return self.background_game_mode.advance_state()

    def get_music(self) -> tuple[Optional[str], Optional[str], Optional[bool], Optional[float], Optional[float]]:
        """Implementation of GameMode.get_music for this game mode."""
        return self.background_game_mode.get_music()
