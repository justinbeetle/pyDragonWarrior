#!/usr/bin/env python

# Imports to support type annotations
from typing import Dict, List, Optional
from GameTypes import DialogReplacementVariables, DialogType, ItemType, Level, MapDecoration, MonsterInfo, Spell, Tile

import abc
import pygame

from GameDialog import GameDialog
from GenericGameState import GenericGameState
from HeroParty import HeroParty
from Point import Point


class GameStateInterface(GenericGameState, metaclass=abc.ABCMeta):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

    @abc.abstractmethod
    def get_hero_party(self) -> HeroParty:
        raise NotImplementedError

    # TODO: Remove and instead get from GameInfo
    @abc.abstractmethod
    def get_dialog_replacement_variables(self) -> DialogReplacementVariables:
        raise NotImplementedError

    # TODO: Remove and instead get from GameInfo
    @abc.abstractmethod
    def get_item(self, name: str) -> Optional[ItemType]:
        raise NotImplementedError

    # TODO: Remove and instead get from GameInfo
    @abc.abstractmethod
    def get_dialog_sequences(self) -> Dict[str, DialogType]:
        raise NotImplementedError

    # TODO: Remove and instead get from GameInfo
    @abc.abstractmethod
    def get_tile(self, name: str) -> Tile:
        raise NotImplementedError

    @abc.abstractmethod
    def is_outside(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def is_inside(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def is_in_combat(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def is_light_restricted(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_light_diameter(self) -> Optional[float]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_light_diameter(self, light_diameter: Optional[float]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_map_name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def set_map(self,
                new_map_name: str,
                one_time_decorations: Optional[List[MapDecoration]] = None,
                respawn_decorations: bool = False) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def is_facing_door(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def open_door(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def remove_decoration(self, decoration: MapDecoration) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def draw_map(self, flip_buffer: bool = True) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_win_size_pixels(self) -> Point:
        raise NotImplementedError

    # TODO: Remove and instead get from GameInfo
    @abc.abstractmethod
    def get_tile_size_pixels(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def initiate_encounter(self,
                           monster_info: Optional[MonsterInfo] = None,
                           approach_dialog: Optional[DialogType] = None,
                           victory_dialog: Optional[DialogType] = None,
                           run_away_dialog: Optional[DialogType] = None,
                           encounter_music: Optional[str] = None,
                           message_dialog: Optional[GameDialog] = None) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def handle_death(self, message_dialog: Optional[GameDialog] = None) -> None:
        raise NotImplementedError
