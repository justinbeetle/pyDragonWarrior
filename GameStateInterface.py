#!/usr/bin/env python

# Imports to support type annotations
from typing import Dict, List, Optional
from GameTypes import DialogReplacementVariables, DialogType, ItemType, Level, MapDecoration

import abc
import pygame

from GenericGameState import GenericGameState
from HeroParty import HeroParty


class GameStateInterface(GenericGameState, metaclass=abc.ABCMeta):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

    @abc.abstractmethod
    def get_hero_party(self) -> HeroParty:
        raise NotImplementedError

    @abc.abstractmethod
    def get_dialog_replacement_variables(self) -> DialogReplacementVariables:
        raise NotImplementedError

    @abc.abstractmethod
    def get_item(self, name: str) -> ItemType:
        raise NotImplementedError

    @abc.abstractmethod
    def get_levels(self, character_type: str) -> List[Level]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_dialog_sequences(self) -> Dict[str, DialogType]:
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
    def is_facing_door(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def open_door(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def remove_decoration(self, decoration: MapDecoration) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self) -> None:
        raise NotImplementedError



