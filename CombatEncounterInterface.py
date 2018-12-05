#!/usr/bin/env python

# Imports to support type annotations
from typing import List

import abc

from CombatCharacterState import CombatCharacterState


class CombatEncounterInterface:
    @abc.abstractmethod
    def render_damage_to_targets(self, targets: List[CombatCharacterState]) -> None:
        raise NotImplementedError
