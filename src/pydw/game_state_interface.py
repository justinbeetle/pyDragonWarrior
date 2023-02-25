#!/usr/bin/env python

# Imports to support type annotations
from typing import List, Optional

import abc
import pygame

from generic_utils.point import Point

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


class GameStateInterface(GenericGameState, metaclass=abc.ABCMeta):
    def __init__(self, screen: pygame.surface.Surface) -> None:
        super().__init__(screen)

    @abc.abstractmethod
    def get_game_info(self) -> GameInfo:
        pass

    @abc.abstractmethod
    def get_tile_info(self, tile: Optional[Point]) -> Tile:
        pass

    @abc.abstractmethod
    def get_image_pad_tiles(self) -> Point:
        pass

    @abc.abstractmethod
    def get_hero_party(self) -> HeroParty:
        pass

    @abc.abstractmethod
    def check_progress_markers(
        self, progress_marker: Optional[str], inverse_progress_marker: Optional[str]
    ) -> bool:
        pass

    @abc.abstractmethod
    def get_dialog_replacement_variables(self) -> DialogReplacementVariables:
        pass

    @abc.abstractmethod
    def is_outside(self) -> bool:
        pass

    @abc.abstractmethod
    def is_inside(self) -> bool:
        pass

    @abc.abstractmethod
    def is_in_combat(self) -> bool:
        pass

    @abc.abstractmethod
    def is_combat_allowed(self) -> bool:
        pass

    @abc.abstractmethod
    def is_light_restricted(self) -> bool:
        pass

    # TODO: Move this into the HeroParty
    @abc.abstractmethod
    def get_map_name(self) -> str:
        pass

    @abc.abstractmethod
    def set_map(
        self,
        new_map_name: str,
        one_time_decorations: Optional[List[MapDecoration]] = None,
        respawn_decorations: bool = False,
    ) -> None:
        pass

    @abc.abstractmethod
    def is_facing_locked_item(self) -> bool:
        pass

    @abc.abstractmethod
    def is_facing_openable_item(self) -> bool:
        pass

    @abc.abstractmethod
    def open_locked_item(self) -> Optional[MapDecoration]:
        pass

    @abc.abstractmethod
    def remove_decoration(self, decoration: MapDecoration) -> None:
        pass

    @abc.abstractmethod
    def get_npc_by_name(self, name: str) -> Optional[MapCharacterState]:
        pass

    @abc.abstractmethod
    def draw_map(
        self,
        flip_buffer: bool = True,
        draw_background: bool = True,
        draw_combat: bool = True,
        draw_status: bool = True,
        draw_only_character_sprites: bool = False,
    ) -> None:
        pass

    @abc.abstractmethod
    def save(self) -> None:
        pass

    @abc.abstractmethod
    def get_win_size_pixels(self) -> Point:
        pass

    @abc.abstractmethod
    def initiate_encounter(
        self,
        monster_info: Optional[MonsterInfo] = None,
        approach_dialog: Optional[DialogType] = None,
        victory_dialog: Optional[DialogType] = None,
        run_away_dialog: Optional[DialogType] = None,
        encounter_music: Optional[str] = None,
        message_dialog: Optional[GameDialog] = None,
    ) -> None:
        pass

    @abc.abstractmethod
    def handle_death(self, message_dialog: Optional[GameDialog] = None) -> None:
        pass

    @abc.abstractmethod
    def handle_quit(self, force: bool = False) -> None:
        pass

    @abc.abstractmethod
    def should_add_math_problems_in_combat(self) -> bool:
        pass
