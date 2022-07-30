#!/usr/bin/env python

# Imports to support type annotations
from typing import List

import abc

from pydw.combat_character_state import CombatCharacterState
from pydw.monster_state import MonsterState


class CombatEncounterInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def render_monsters(self) -> None:
        pass

    @abc.abstractmethod
    def render_damage_to_targets(self, targets: List[CombatCharacterState]) -> None:
        pass

    @abc.abstractmethod
    def get_monsters_still_in_combat(self) -> List[CombatCharacterState]:
        pass
