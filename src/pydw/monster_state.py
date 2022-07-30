#!/usr/bin/env python

from typing import Optional, Tuple, Union

import random

from pydw.combat_character_state import CombatCharacterState
from pydw.game_types import ActionCategoryTypeEnum, DialogActionEnum, MonsterInfo, SpecialMonster, Spell



class MonsterState(CombatCharacterState):
    def __init__(self, monster_info: Union[MonsterInfo, SpecialMonster]) -> None:
        if isinstance(monster_info, SpecialMonster):
            self.monster_info = monster_info.monster_info
            self.special_monster_info: Optional[SpecialMonster] = monster_info
        else:
            self.monster_info = monster_info
            self.special_monster_info = None
        super().__init__(hp=random.randint(self.monster_info.min_hp, self.monster_info.max_hp))
        self.gp = random.randint(self.monster_info.min_gp, self.monster_info.max_gp)
        self.xp = self.monster_info.xp  # TODO: Should this also come from a range?
        self.name = 'the ' + self.monster_info.name

    def get_name(self) -> str:
        return self.name

    def get_type_name(self) -> str:
        return self.monster_info.name

    def set_name(self, name: str) -> None:
        self.name = name

    def is_still_asleep(self) -> bool:
        ret_val = self.is_asleep and (self.turns_asleep == 0 or random.uniform(0, 1) > 1.0 / 3.0)
        if ret_val:
            self.turns_asleep += 1
        else:
            self.is_asleep = False
            self.turns_asleep = 0
        return ret_val

    def get_strength(self) -> int:
        return self.monster_info.strength

    def get_agility(self) -> int:
        return self.monster_info.agility

    def get_attack_strength(self) -> int:
        return self.get_strength()

    def get_defense_strength(self) -> int:
        return self.get_agility()

    def allows_critical_hits(self) -> bool:
        return self.monster_info.allows_critical_hits

    # Determine if the monster dodges an attack
    def is_dodging_attack(self) -> bool:
        return (not self.is_asleep
                and random.uniform(0, 1) < self.monster_info.dodge)

    # TODO: In progress work to generalize and replace get_spell_resistance with get_resistance
    def get_resistance(self, action: DialogActionEnum, category: ActionCategoryTypeEnum) -> float:
        if DialogActionEnum.SLEEP == action:
            return self.monster_info.sleep_resist
        if DialogActionEnum.STOPSPELL == action:
            return self.monster_info.stopspell_resist
        if DialogActionEnum.DAMAGE_TARGET == action and ActionCategoryTypeEnum.MAGICAL == category:
            return self.monster_info.hurt_resist
        return 0

    def get_spell_resistance(self, spell: Spell) -> float:
        if 'HURT' == spell.name.upper() or 'HURTMORE' == spell.name.upper():
            return self.monster_info.hurt_resist
        if 'SLEEP' == spell.name.upper():
            return self.monster_info.sleep_resist
        if 'STOPSPELL' == spell.name.upper():
            return self.monster_info.stopspell_resist
        return 0

    def get_damage_modifier(self, damage_type: ActionCategoryTypeEnum) -> float:
        return 1.0

    def get_attack_damage(self,
                          target: CombatCharacterState,
                          damage_type: ActionCategoryTypeEnum = ActionCategoryTypeEnum.PHYSICAL,
                          is_critical_hit: Optional[bool] = None) -> Tuple[int, bool]:
        if is_critical_hit is None:
            is_critical_hit = False
        if target.get_defense_strength() < self.get_strength():
            min_damage = (self.get_strength() - target.get_defense_strength() // 2) // 4
            max_damage = (self.get_strength() - target.get_defense_strength() // 2) // 2
        else:
            min_damage = 0
            max_damage = (self.get_strength() + 4) // 6
        damage = CombatCharacterState.calc_damage(
            min_damage,
            max_damage,
            target,
            damage_type)

        # For critical hits from monsters, perform a second damage calculation and use the higher of the two damage
        # values.
        if is_critical_hit:
            damage = max(damage, CombatCharacterState.calc_damage(
                min_damage,
                max_damage,
                target,
                damage_type))

        return damage, is_critical_hit

    # Determine if the monster has the initiative and attacks first in an encounter.
    # As implemented, special monsters never attack first.
    def has_initiative(self, hero_state: CombatCharacterState) -> bool:
        # TODO: Verify that special monsters never take the initiative
        return (not self.monster_info.may_run_away and self.special_monster_info is None
                and hero_state.get_agility() * random.uniform(0, 1) < self.get_agility() * random.uniform(0, 1) * 0.25)

    # Determine if the monster will attempt to run away.
    # Special monsters never run away.
    def should_run_away(self, hero_state: CombatCharacterState) -> bool:
        return (self.monster_info.may_run_away and self.special_monster_info is None
                and hero_state.get_strength() > self.get_strength() * 2 and random.uniform(0, 1) < 0.25)

    # Determine if the monster blocks an attempt by the hero to run away
    def is_blocking_escape(self, hero_state: CombatCharacterState) -> bool:
        return (not self.is_asleep
                and hero_state.get_agility() * random.uniform(0, 1) <
                self.get_agility() * random.uniform(0, 1) * self.monster_info.block_factor)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{super()}, ' \
               f'{self.monster_info}, ' \
               f'{self.special_monster_info}, ' \
               f'{self.gp}, ' \
               f'{self.xp})'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{super()!r}, ' \
               f'{self.monster_info!r}, ' \
               f'{self.special_monster_info!r}, ' \
               f'{self.gp!r}, ' \
               f'{self.xp!r})'


def main() -> None:
    import pygame
    monster_info = MonsterInfo(
        name='MonsterName',
        image=pygame.surface.Surface((0, 0)),
        strength=1,
        agility=2,
        min_hp=3,
        max_hp=4,
        sleep_resist=5.1,
        stopspell_resist=6.2,
        hurt_resist=7.3,
        dodge=8.4,
        block_factor=9.5,
        xp=10,
        min_gp=11,
        max_gp=12,
        monster_action_rules=[],
        allows_critical_hits=False,
        may_run_away=True)
    monster = MonsterState(monster_info)
    print(monster, flush=True)
    while monster.is_alive():
        monster.hp -= 10
        print(monster, flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import sys
        import traceback
        print(traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                         e,
                                         e.__traceback__),
              file=sys.stderr, flush=True)
        traceback.print_exc()
