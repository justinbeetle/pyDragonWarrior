#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Dict, List, Optional, Union

import math
import random

from MapCharacterState import MapCharacterState
from CombatCharacterState import CombatCharacterState
from Point import Point
from GameTypes import Armor, Direction, Helm, ItemType, Level, Shield, Spell, Tool, Weapon


class HeroState(MapCharacterState, CombatCharacterState):
    def __init__(self,
                 type: str,
                 pos_dat_tile: Point,
                 direction: Direction,
                 name: str,
                 level: Level) -> None:
        MapCharacterState.__init__(self, type, pos_dat_tile, direction)
        CombatCharacterState.__init__(self, hp=level.hp)

        self.name = name
        self.level = level

        self.mp = level.mp
        self.xp = level.xp
         
        self.weapon: Optional[Weapon] = None

        self.helm: Optional[Helm] = None
        self.armor: Optional[Armor] = None
        self.shield: Optional[Shield] = None

        self.other_equipped_items: List[Tool] = []
        self.unequipped_items: Dict[ItemType, int] = {}  # Dict where keys are items and values are the item counts

    def get_item_row_data(self,
                          limit_to_droppable: bool = False,
                          filter_types: Optional[List[str]] = None) -> List[List[str]]:
        item_row_data: List[List[str]] = []
        if self.weapon is not None:
            HeroState.add_item_to_item_row_data(self.weapon, 'E', limit_to_droppable, filter_types, item_row_data)
        if self.helm is not None:
            HeroState.add_item_to_item_row_data(self.helm, 'E', limit_to_droppable, filter_types, item_row_data)
        if self.armor is not None:
            HeroState.add_item_to_item_row_data(self.armor, 'E', limit_to_droppable, filter_types, item_row_data)
        if self.shield is not None:
            HeroState.add_item_to_item_row_data(self.shield, 'E', limit_to_droppable, filter_types, item_row_data)
        for tool in sorted(self.other_equipped_items, key=lambda inner_item: inner_item.name):
            HeroState.add_item_to_item_row_data(tool, 'E', limit_to_droppable, filter_types, item_row_data)
        for item in sorted(self.unequipped_items, key=lambda inner_item: inner_item.name):
            item_count_str = str(self.unequipped_items[item])
            HeroState.add_item_to_item_row_data(item, item_count_str, limit_to_droppable, filter_types, item_row_data)
        return item_row_data

    @staticmethod
    def add_item_to_item_row_data(item: ItemType,
                                  col_value: str,
                                  limit_to_droppable: bool,
                                  filter_types: Optional[List[str]],
                                  item_row_data: List[List[str]]) -> None:
        item_passed_type_filter = False
        if filter_types is None:
            item_passed_type_filter = True
        else:
            for filterType in filter_types:
                if filterType == 'Weapon' and isinstance(item, Weapon):
                    item_passed_type_filter = True
                    break
                elif filterType == 'Helm' and isinstance(item, Helm):
                    item_passed_type_filter = True
                    break
                elif filterType == 'Armor' and isinstance(item, Armor):
                    item_passed_type_filter = True
                    break
                elif filterType == 'Shield' and isinstance(item, Shield):
                    item_passed_type_filter = True
                    break
                elif filterType == 'Tool' and isinstance(item, Tool):
                    item_passed_type_filter = True
                    break
        if item_passed_type_filter and (not limit_to_droppable or not isinstance(item, Tool) or item.droppable):
            item_row_data.append([item.name, col_value])

    def is_item_equipped(self, item_name: str) -> bool:
        ret_val = False
        if self.weapon is not None and item_name == self.weapon.name:
            ret_val = True
        elif self.helm is not None and item_name == self.helm.name:
            ret_val = True
        elif self.armor is not None and item_name == self.armor.name:
            ret_val = True
        elif self.shield is not None and item_name == self.shield.name:
            ret_val = True
        else:
            for item in self.other_equipped_items:
                if item_name == item.name:
                    ret_val = True
                    break
        return ret_val

    def has_item(self, item_name: str) -> bool:
        return self.get_item_count(item_name) > 0

    def get_item_count(self, item_name: str, unequipped_only=False) -> int:
        ret_val = 0
        for item in self.unequipped_items:
            if item_name == item.name:
                ret_val = self.unequipped_items[item]
                break
        if not unequipped_only and self.is_item_equipped(item_name):
            ret_val += 1
        return ret_val

    def get_item_options(self, item_name: str) -> List[str]:
        item_options = []
        is_equipped = False
        if self.is_item_equipped(item_name):
            item_options.append('UNEQUIP')
            item_options.append('DROP')  # At present all equipable items are also droppable
            is_equipped = True
        for item in self.unequipped_items:
            if item_name == item.name:
                if (not isinstance(item, Tool) or item.equippable) and not is_equipped:
                    item_options.append('EQUIP')
                if isinstance(item, Tool) and item.use_dialog is not None:
                    item_options.append('USE')
                if (not isinstance(item, Tool) or item.droppable) and not is_equipped:
                    item_options.append('DROP')
                break
        return item_options

    def equip_item(self, item_name: str) -> None:
        # Equip an unequipped item - may result in the unequiping of a previously equipped item
        if not self.is_item_equipped(item_name):
            item = self.lose_item(item_name)
            if item is not None:
                if isinstance(item, Weapon):
                    if self.weapon is not None:
                        self.gain_item(self.weapon)
                    self.weapon = item
                elif isinstance(item, Helm):
                    if self.helm is not None:
                        self.gain_item(self.helm)
                    self.helm = item
                elif isinstance(item, Armor):
                    if self.armor is not None:
                        self.gain_item(self.armor)
                    self.armor = item
                elif isinstance(item, Shield):
                    if self.shield is not None:
                        self.gain_item(self.shield)
                    self.shield = item
                elif isinstance(item, Tool) and item.equippable:
                    self.other_equipped_items.append(item)
                else:
                    print('ERROR: Item cannot be equipped:', item, flush=True)
                    self.gain_item(item)
            else:
                print('WARN: Item not in inventory:', item_name, flush=True)
        else:
            print('WARN: Item already equipped:', item_name, flush=True)
         
    def unequip_item(self, item_name: str) -> None:
        # Unequip an equipped item by removing it as eqipped and adding it as unequipped
        if self.weapon is not None and item_name == self.weapon.name:
            self.gain_item(self.weapon)
            self.weapon = None
        elif self.helm is not None and item_name == self.helm.name:
            self.gain_item(self.helm)
            self.helm = None
        elif self.armor is not None and item_name == self.armor.name:
            self.gain_item(self.armor)
            self.armor = None
        elif self.shield is not None and item_name == self.shield.name:
            self.gain_item(self.shield)
            self.shield = None
        else:
            for item in self.other_equipped_items:
                if item_name == item.name:
                    self.gain_item(item)
                    self.other_equipped_items.remove(item)
                    break

    def gain_item(self, item: ItemType, count: int=1) -> None:
        # Gained items always go unequippedItems
        if item in self.unequipped_items:
            self.unequipped_items[item] += count
        else:
            self.unequipped_items[item] = count

    def lose_item(self, item_name: str, count: int=1, unequipped_only=False) -> Optional[ItemType]:
        # Lost items are taken from unequippedItems where possible, else equipped items
        ret_val = None
        remaining_items_to_lose = count
        for item in self.unequipped_items:
            if item_name == item.name:
                ret_val = item
                self.unequipped_items[item] -= count
                if self.unequipped_items[item] <= 0:
                    remaining_items_to_lose = -self.unequipped_items[item]
                    del self.unequipped_items[item]
                    break
        if remaining_items_to_lose > 0 and not unequipped_only:
            if self.weapon is not None and item_name == self.weapon.name:
                ret_val = self.weapon
                self.weapon = None
                remaining_items_to_lose -= 1
            elif self.helm is not None and item_name == self.helm.name:
                ret_val = self.helm
                self.helm = None
                remaining_items_to_lose -= 1
            elif self.armor is not None and item_name == self.armor.name:
                ret_val = self.armor
                self.armor = None
                remaining_items_to_lose -= 1
            elif self.shield is not None and item_name == self.shield.name:
                ret_val = self.shield
                self.shield = None
                remaining_items_to_lose -= 1
            else:
                for item in self.other_equipped_items:
                    if item_name == item.name:
                        ret_val = item
                        self.other_equipped_items.remove(item)
                        remaining_items_to_lose -= 1
                        break
        return ret_val

    def get_name(self) -> str:
        return self.name

    def is_still_asleep(self) -> bool:
        ret_val = self.is_asleep and (self.turns_asleep == 0 or random.uniform(0, 1) > 0.5)
        if ret_val:
            self.turns_asleep += 1
        else:
            self.is_asleep = False
            self.turns_asleep = 0
        return ret_val

    def get_strength(self) -> int:
        return self.level.strength

    def get_agility(self) -> int:
        return self.level.agility

    def get_attack_strength(self) -> int:
        ret_val = self.get_strength()
        if self.weapon is not None:
            ret_val += self.weapon.attack_bonus
        for item in self.other_equipped_items:
            ret_val += item.attack_bonus
        return math.floor(ret_val)

    def get_defense_strength(self) -> int:
        ret_val = self.get_agility() // 2
        if self.helm is not None:
            ret_val += self.helm.defense_bonus
        if self.armor is not None:
            ret_val += self.armor.defense_bonus
        if self.shield is not None:
            ret_val += self.shield.defense_bonus
        for item in self.other_equipped_items:
            ret_val += item.defense_bonus
        return ret_val

    def allows_critical_hits(self) -> bool:
        return False

    def get_spell_resistance(self, spell: Spell) -> float:
        if spell.name == 'Stopspell' and self.armor is not None:
            return self.armor.stopspell_resistance
        return 0

    def critical_hit_check(self, monster: CombatCharacterState) -> bool:
        return monster.allows_critical_hits() and random.uniform(0, 1) < 1/32

    def calc_regular_hit_damage_to_monster(self, monster: CombatCharacterState) -> int:
        return HeroState.calc_damage(
            (self.get_attack_strength() - monster.get_agility() // 2) // 4,
            (self.get_attack_strength() - monster.get_agility() // 2) // 2)

    def calc_critical_hit_damage_to_monster(self, monster: CombatCharacterState) -> int:
        return HeroState.calc_damage(
            self.get_attack_strength() // 2,
            self.get_attack_strength())

    def calc_hit_damage_from_monster(self, monster: CombatCharacterState) -> int:
        if self.get_defense_strength() < monster.get_strength():
            return HeroState.calc_damage(
                (monster.get_strength() - self.get_defense_strength() // 2) // 4,
                (monster.get_strength() - self.get_defense_strength() // 2) // 2)
        else:
            return HeroState.calc_damage(0, (monster.get_strength() + 4) // 6)

    # TODO: Add spell checks and damage calc methods

    # TODO: Add method for determining available spells

    @staticmethod
    def calc_damage(min_damage: int, max_damage: int) -> int:
        # print('min_damage =', min_damage, flush=True)
        # print('max_damage =', max_damage, flush=True)
        damage = math.floor(min_damage + random.uniform(0, 1) * (max_damage - min_damage))
        if damage < 1:
            if random.uniform(0, 1) < 0.5:
                damage = 0
            else:
                damage = 1
        return damage

    @staticmethod
    def calc_level(levels: List[Level], xp: int) -> Level:
        for level in reversed(levels):
            if level.xp <= xp:
                return level
        return levels[0]

    def level_up_check(self, levels: List[Level]) -> bool:
        leveled_up = False
        if self.level is not None:
            new_level = HeroState.calc_level(levels, self.xp)
            leveled_up = self.level != new_level
            self.level = new_level
        return leveled_up

    def is_ignoring_tile_penalties(self) -> bool:
        ret_val = False
        if not ret_val and self.armor is not None:
            ret_val = self.armor.ignores_tile_penalties
        return ret_val

    def calc_xp_to_next_level(self, levels: List[Level]) -> int:
        ret_val = 0
        if self.level is not None:
            for level in levels:
                if level.xp > self.level.xp:
                    ret_val = level.xp - self.xp
                    break
        return ret_val

    def __str__(self) -> str:
        return "%s(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.__class__.__name__,
            self.name,
            self.level,
            self.hp,
            self.mp,
            self.xp,
            self.type_name,
            self.curr_pos_dat_tile,
            self.dest_pos_dat_tile,
            self.curr_pos_offset_img_px,
            self.direction)

    def __repr__(self) -> str:
        return "%s(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r)" % (
            self.__class__.__name__,
            self.name,
            self.level,
            self.hp,
            self.mp,
            self.xp,
            self.type_name,
            self.curr_pos_dat_tile,
            self.dest_pos_dat_tile,
            self.curr_pos_offset_img_px,
            self.direction)


def main() -> None:
   # Test out character states
   level = Level( 0, '1', 2, 3, 4, 25, 6 )
   hero_state = HeroState('hero', Point(7,3), Direction.WEST, 'Sir Me', level)
   print(hero_state, flush=True)
   while hero_state.is_alive():
      hero_state.hp -= 10
      print(hero_state, flush=True)


if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
