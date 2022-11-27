#!/usr/bin/env python

# Imports to support type annotations
from typing import List

import abc

from pydw.combat_character_state import CombatCharacterState


class CombatParty:
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def get_combat_members(self) -> List[CombatCharacterState]:
        pass

    def is_still_in_combat(self) -> bool:
        for member in self.get_combat_members():
            if member.is_still_in_combat():
                return True
        return False

    def get_still_in_combat_members(self) -> List[CombatCharacterState]:
        alive_members = []
        for member in self.get_combat_members():
            if member.is_still_in_combat():
                alive_members.append(member)
        return alive_members

    def get_highest_attack_strength(self) -> int:
        highest_attack_strength = 0
        for member in self.get_combat_members():
            if member.is_still_in_combat():
                highest_attack_strength = max(
                    highest_attack_strength, member.get_attack_strength()
                )
        return highest_attack_strength
