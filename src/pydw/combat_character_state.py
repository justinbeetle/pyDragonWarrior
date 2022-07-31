#!/usr/bin/env python

from __future__ import annotations
from typing import Optional, Tuple

import abc
import math
import random

from pydw.game_types import ActionCategoryTypeEnum, DialogActionEnum, Spell


class CombatCharacterState(metaclass=abc.ABCMeta):
    def __init__(self,
                 hp: int,
                 max_hp: int = 0,
                 mp: int = 0,
                 max_mp: int = 0,
                 is_combat_character: bool = True) -> None:
        self.hp = hp
        self.max_hp = max(hp, max_hp)
        self.mp = mp
        self.max_mp = max(mp, max_mp)
        self.is_combat_character = is_combat_character
        self.is_asleep = False
        self.turns_asleep = 0
        self.are_spells_blocked = False
        self.has_run_away = not self.is_combat_character

    def clear_combat_status_affects(self) -> None:
        self.is_asleep = False
        self.turns_asleep = 0
        self.are_spells_blocked = False
        self.has_run_away = not self.is_combat_character

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

    # TODO: In progress work to generalize and replace does_spell_work with does_action_work
    def does_action_work(self,
                         action: DialogActionEnum,
                         category: ActionCategoryTypeEnum,
                         target: CombatCharacterState,
                         bypass_resistance: bool = False,
                         bypass_type_name: Optional[str] = None) -> bool:
        # Factor in the bypass_type_name
        # If bypass_resistance is True and bypass_type_name is None, bypass_resistance applies to all target types
        # If bypass_resistance is True and bypass_type_name is not None, the bypass_resistance only applies to the
        # target type with the name bypass_type_name.
        # TODO: Probably want to refine this mechanic
        if bypass_resistance and bypass_type_name is not None:
            bypass_resistance = target.get_type_name() == bypass_type_name

        if ActionCategoryTypeEnum.MAGICAL == category and self.are_spells_blocked:
            return False
        if DialogActionEnum.SLEEP == action and target.is_asleep:
            return False
        if DialogActionEnum.STOPSPELL == action and target.are_spells_blocked:
            return False
        if not bypass_resistance and target.get_resistance(action, category) > random.uniform(0, 1):
            return False
        if isinstance(self, type(target)) \
                and action in (DialogActionEnum.SLEEP, DialogActionEnum.STOPSPELL, DialogActionEnum.DAMAGE_TARGET):
            # Hero's shouldn't put other heroes to sleep and monsters shouldn't put other monsters to sleep
            return False
        return True

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
        pass

    @abc.abstractmethod
    def get_type_name(self) -> str:
        pass

    # Determine if character should remain asleep.  Maintain turns_asleep.
    def is_still_asleep(self) -> bool:
        ret_val = self.is_asleep and (self.turns_asleep == 0 or random.uniform(0, 1) > self.get_wake_probability())
        if ret_val:
            self.turns_asleep += 1
        else:
            self.is_asleep = False
            self.turns_asleep = 0
        return ret_val

    @abc.abstractmethod
    def get_wake_probability(self) -> float:
        pass

    @abc.abstractmethod
    def get_strength(self) -> int:
        pass

    @abc.abstractmethod
    def get_agility(self) -> int:
        pass

    @abc.abstractmethod
    def get_attack_strength(self) -> int:
        pass

    @abc.abstractmethod
    def get_defense_strength(self) -> int:
        pass

    @abc.abstractmethod
    def allows_critical_hits(self) -> bool:
        pass

    @abc.abstractmethod
    def is_dodging_attack(self) -> bool:
        pass

    # TODO: In progress work to generalize and replace get_spell_resistance with get_resistance
    @abc.abstractmethod
    def get_resistance(self, action: DialogActionEnum, category: ActionCategoryTypeEnum) -> float:
        pass

    @abc.abstractmethod
    def get_spell_resistance(self, spell: Spell) -> float:
        pass

    @abc.abstractmethod
    def get_damage_modifier(self, damage_type: ActionCategoryTypeEnum) -> float:
        pass

    # Return damage along with a bool indicating whether the attack was a critical hit
    # Accounts for and applies the damage modifier
    @abc.abstractmethod
    def get_attack_damage(self,
                          target: CombatCharacterState,
                          damage_type: ActionCategoryTypeEnum = ActionCategoryTypeEnum.PHYSICAL,
                          is_critical_hit: Optional[bool] = None) -> Tuple[int, bool]:
        pass

    @staticmethod
    def calc_damage(min_damage: int,
                    max_damage: int,
                    target: CombatCharacterState,
                    damage_type: ActionCategoryTypeEnum) -> int:
        # print('min_damage =', min_damage, flush=True)
        # print('max_damage =', max_damage, flush=True)
        modifier = target.get_damage_modifier(damage_type)
        damage = math.floor((min_damage + random.uniform(0, 1) * (max_damage - min_damage)) * modifier)
        if damage < 1:
            damage = random.randint(0, 1)
        return damage

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.hp}, {self.max_hp}, ' \
               f'{self.is_asleep}, {self.turns_asleep}, {self.are_spells_blocked})'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.hp!r}, {self.max_hp!r}, ' \
               f'{self.is_asleep!r}, {self.turns_asleep!r}, {self.are_spells_blocked!r})'
