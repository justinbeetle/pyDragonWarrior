#!/usr/bin/env python

from __future__ import annotations

import abc
import random

from GameTypes import Spell


class CombatCharacterState(metaclass=abc.ABCMeta):
    def __init__(self, hp: int, max_hp: int = 0) -> None:
        self.hp = hp
        self.max_hp = max(hp, max_hp)
        self.is_asleep = False
        self.turns_asleep = 0
        self.are_spells_blocked = False
        self.has_run_away = False

    def clear_combat_status_affects(self) -> None:
        self.is_asleep = False
        self.turns_asleep = 0
        self.are_spells_blocked = False
        self.has_run_away = False

    def is_alive(self) -> bool:
        return self.hp > 0

    def is_dead(self) -> bool:
        return not self.is_alive()

    def heals(self, heal_hp: int) -> None:
        self.hp = min(self.max_hp, self.hp + heal_hp)

    def takes_damages(self, damage_hp: int) -> None:
        self.hp = max(0, self.hp - damage_hp)

    def is_still_in_combat(self) -> bool:
        return self.is_alive() and not self.has_run_away

    def does_spell_work(self, spell: Spell, target: CombatCharacterState) -> bool:
        if self.are_spells_blocked:
            return False
        if target.get_spell_resistance(spell) > random.uniform(0, 1):
            return False
        if 'SLEEP' == spell.name.upper() and target.is_asleep:
            return False
        if 'STOPSPELL' == spell.name.upper() and target.are_spells_blocked:
            return False
        return True

    @abc.abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError

    # Determine if character should remain asleep.  Should maintain turnsAsleep.
    @abc.abstractmethod
    def is_still_asleep(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_strength(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_agility(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_attack_strength(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_defense_strength(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def allows_critical_hits(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_spell_resistance(self, spell: Spell) -> float:
        raise NotImplementedError

    def __str__(self) -> str:
        return "%s(%s, %s, %s, %s, %s)" % (
            self.__class__.__name__,
            self.hp,
            self.max_hp,
            self.is_asleep,
            self.turns_asleep,
            self.are_spells_blocked)

    def __repr__(self) -> str:
        return "%s(%r, %r, %r, %r, %r)" % (
            self.__class__.__name__,
            self.hp,
            self.max_hp,
            self.is_asleep,
            self.turns_asleep,
            self.are_spells_blocked)
