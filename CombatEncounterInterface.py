#!/usr/bin/env python

# Imports to support type annotations
from typing import List

import abc

from CombatCharacterState import CombatCharacterState
from MonsterState import MonsterState


class CombatEncounterInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def render_monsters(self) -> None:
        pass

    @abc.abstractmethod
    def render_damage_to_targets(self, targets: List[CombatCharacterState]) -> None:
        pass

    @abc.abstractmethod
    def get_monsters_still_in_combat(self) -> List[MonsterState]:
        pass
