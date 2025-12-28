#!/usr/bin/env python

# Imports to support type annotations
from abc import ABC, abstractmethod
from typing import List, Optional

import pygame

from generic_utils.point import Point
from pydw.dialog_manager import DialogManager
from pydw.game_dialog import GameDialog
from pydw.game_info import GameInfo
from pydw.game_types import (
    DialogReplacementVariables,
    DialogType,
    MapDecoration,
    MonsterInfo,
    Tile,
)
from pydw.generic_game_state import GenericGameState
from pydw.hero_party import HeroParty
from pydw.map_character_state import MapCharacterState


class GameStateInterface(ABC, GenericGameState):
    def __init__(self, screen: pygame.surface.Surface) -> None:
        super().__init__(screen)

    @abstractmethod
    def get_game_info(self) -> GameInfo:
        """Get the static game info"""

    @abstractmethod
    def get_tile_info(self, tile: Optional[Point]) -> Tile:
        """Get the tile info for the specified position, or if not specified, the location of the player character."""

    @abstractmethod
    def get_image_pad_tiles(self) -> Point:
        """Get a point where the width and height indicate how many times to repeat the outermost tiles so that the
        maps extend to the edge of the screen."""

    @abstractmethod
    def get_hero_party(self) -> HeroParty:
        """Get the hero party."""

    @abstractmethod
    def check_progress_markers(self, progress_marker: Optional[str], inverse_progress_marker: Optional[str]) -> bool:
        """Return True if the progress marker conditions are met.  Else return False."""

    @abstractmethod
    def get_dialog_replacement_variables(self) -> DialogReplacementVariables:
        """Get the dialog replacement variables used based on the current game state."""

    @abstractmethod
    def is_outside(self) -> bool:
        """Return True if the player character is outside a dungeon where the outside spell cannot be used and the
        return spell can be used.  Else return False.  This is the negation of is_inside."""

    @abstractmethod
    def is_inside(self) -> bool:
        """Return True if the player character is inside a dungeon where the outside spell can be used and the return.
        spell cannot be used.  Else return False.  This is the negation of is_outside."""

    @abstractmethod
    def is_in_combat(self) -> bool:
        """Return True if the player character is in combat.  Else return False."""

    @abstractmethod
    def is_combat_allowed(self) -> bool:
        """Return True if the player character is in a location where a combat encounter could start.
        Else return False."""

    @abstractmethod
    def is_light_restricted(self) -> bool:
        """Return True if the entire map is not lit.  Else return False."""

    # TODO: Move this into the HeroParty
    @abstractmethod
    def get_map_name(self) -> str:
        """Get the name of the current map."""

    @abstractmethod
    def set_map(
        self,
        new_map_name: str,
        one_time_decorations: Optional[List[MapDecoration]] = None,
        respawn_decorations: bool = False,
    ) -> None:
        """Set to a new map."""

    @abstractmethod
    def is_facing_locked_item(self) -> bool:
        """Return True is the player character is standing on or looking at (next tile over in the direction they are
        facing) a locked item (ie a locked door or chest which requires a key to open).  Else return False."""

    @abstractmethod
    def is_facing_openable_item(self) -> bool:
        """Return True is the player character is standing on or looking at (next tile over in the direction they are
        facing) a locked or unlocked item (ie any door or chest).  Else return False."""

    @abstractmethod
    def open_locked_item(self) -> Optional[MapDecoration]:
        pass

    @abstractmethod
    def remove_decoration(self, decoration: MapDecoration) -> None:
        pass

    @abstractmethod
    def get_npc_by_name(self, name: str) -> Optional[MapCharacterState]:
        pass

    @abstractmethod
    def draw_map(
        self,
        flip_buffer: bool = True,
        draw_background: bool = True,
        draw_combat: bool = True,
        draw_status: bool = True,
        draw_only_character_sprites: bool = False,
    ) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def get_win_size_pixels(self) -> Point:
        pass

    @abstractmethod
    def initiate_encounter(
        self,
        monster_info: Optional[MonsterInfo] = None,
        approach_dialog: Optional[DialogType] = None,
        victory_dialog: Optional[DialogType] = None,
        run_away_dialog: Optional[DialogType] = None,
        encounter_music: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def handle_death(self) -> None:
        pass

    @abstractmethod
    def handle_quit(self, force: bool = False) -> None:
        pass

    @abstractmethod
    def should_add_math_problems_in_combat(self) -> bool:
        pass

    @abstractmethod
    def get_dialog_manager(self) -> DialogManager:
        """Get the dialog manager."""

    @abstractmethod
    def advance_tick(self) -> bool:
        """Advance the game state by one tick (frame).  Return a bool indicating if the state was advanced,
        which would then require re-drawing the game mode to the display."""

    @abstractmethod
    def draw(self, flip_buffer: bool = True) -> None:
        """Draw the current state of the game mode to the display."""
