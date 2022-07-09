#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

import math
import random

from generic_utils.point import Point

from pydw.combat_character_state import CombatCharacterState
from pydw.game_types import ActionCategoryTypeEnum, Armor, CharacterType, DialogActionEnum, Direction, Helm, ItemType, \
    Level,  Shield, Spell, Tool, Weapon
from pydw.map_character_state import MapCharacterState


class HeroState(MapCharacterState, CombatCharacterState):
    def __init__(self,
                 character_type: CharacterType,
                 pos_dat_tile: Point,
                 direction: Direction,
                 name: str,
                 xp: int = 0,
                 is_combat_character: bool = True) -> None:
        MapCharacterState.__init__(self, character_type, pos_dat_tile, direction)
        self.name = name
        self.level = self.calc_level(xp)
        self.xp = xp
        CombatCharacterState.__init__(self, hp=self.level.hp, mp=self.level.mp, is_combat_character=is_combat_character)

        self.weapon: Optional[Weapon] = None
        self.helm: Optional[Helm] = None
        self.armor: Optional[Armor] = None
        self.shield: Optional[Shield] = None
        self.other_equipped_items: List[Tool] = []
        self.unequipped_items: Dict[ItemType, int] = {}  # Dict where keys are items and values are the item counts

        self.hp_regen_tiles_remaining: Optional[int] = None

    @staticmethod
    def create_null(name: str = 'null') -> HeroState:
        return HeroState(CharacterType.create_null(), Point(), Direction.SOUTH, name)

    def get_item_row_data(self,
                          limit_to_droppable: bool = False,
                          limit_to_unequipped: bool = False,
                          filter_types: Optional[List[str]] = None) -> List[List[str]]:
        item_row_data: List[List[str]] = []
        if not limit_to_unequipped:
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

        # Flip the data
        flipped_item_row_data: List[List[str]] = []
        for i in range((len(item_row_data) + 1) // 2):
            flipped_item_row_data.append(item_row_data[i])
            old_index = (len(item_row_data) + 1) // 2 + i
            if old_index < len(item_row_data):
                flipped_item_row_data.append(item_row_data[old_index])
        return flipped_item_row_data

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

    def get_item_count(self, item_name: str, unequipped_only: bool=False) -> int:
        ret_val = 0
        for item in self.unequipped_items:
            if item_name == item.name:
                ret_val = self.unequipped_items[item]
                break
        if not unequipped_only and self.is_item_equipped(item_name):
            ret_val += 1
        return ret_val

    def get_item(self, item_name: str, unequipped_only: bool=False) -> Optional[ItemType]:
        for item in self.unequipped_items:
            if item_name == item.name:
                return item
        if not unequipped_only:
            if self.weapon is not None and item_name == self.weapon.name:
                return self.weapon
            elif self.helm is not None and item_name == self.helm.name:
                return self.helm
            elif self.armor is not None and item_name == self.armor.name:
                return self.armor
            elif self.shield is not None and item_name == self.shield.name:
                return self.shield
            else:
                for item in self.other_equipped_items:
                    if item_name == item.name:
                        return item
        return None

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
            # Find and remove item from other_equipped_items
            item = None
            for unequipped_item in self.unequipped_items:
                if unequipped_item.name == item_name:
                    item = unequipped_item
                    self.lose_item(item_name)
                    break

            # Attempt to equip the item
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

    def lose_item(self, item_name: str, count: int=1, unequipped_only: bool=False) -> None:
        # Lost items are taken from unequippedItems where possible, else equipped items
        remaining_items_to_lose = count
        for item in self.unequipped_items:
            if item_name == item.name:
                self.unequipped_items[item] -= count
                remaining_items_to_lose = -self.unequipped_items[item]
                if self.unequipped_items[item] <= 0:
                    del self.unequipped_items[item]
                break
        if remaining_items_to_lose > 0 and not unequipped_only:
            if self.weapon is not None and item_name == self.weapon.name:
                self.weapon = None
                remaining_items_to_lose -= 1
            elif self.helm is not None and item_name == self.helm.name:
                self.helm = None
                remaining_items_to_lose -= 1
            elif self.armor is not None and item_name == self.armor.name:
                self.armor = None
                remaining_items_to_lose -= 1
            elif self.shield is not None and item_name == self.shield.name:
                self.shield = None
                remaining_items_to_lose -= 1
            for item in self.other_equipped_items:
                if item_name == item.name and 0 < remaining_items_to_lose:
                    self.other_equipped_items.remove(item)
                    remaining_items_to_lose -= 1

    def get_name(self) -> str:
        return self.name

    def get_type_name(self) -> str:
        return self.character_type.name

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

    def is_dodging_attack(self) -> bool:
        return False

    # TODO: In progress work to generalize and replace get_spell_resistance with get_resistance
    def get_resistance(self, action: DialogActionEnum, category: ActionCategoryTypeEnum) -> float:
        if DialogActionEnum.STOPSPELL == action and self.armor is not None:
            return self.armor.stopspell_resistance
        return 0

    def get_spell_resistance(self, spell: Spell) -> float:
        if 'STOPSPELL' == spell.name.upper() and self.armor is not None:
            return self.armor.stopspell_resistance
        return 0

    def get_damage_modifier(self, damage_type: ActionCategoryTypeEnum) -> float:
        if ActionCategoryTypeEnum.MAGICAL == damage_type:
            if self.armor is not None:
                return self.armor.hurt_dmg_modifier
        elif ActionCategoryTypeEnum.FIRE == damage_type:
            if self.armor is not None:
                return self.armor.fire_dmg_modifier
        return 1.0

    def get_attack_damage(self,
                          target: CombatCharacterState,
                          damage_type: ActionCategoryTypeEnum = ActionCategoryTypeEnum.PHYSICAL,
                          is_critical_hit: Optional[bool] = None) -> Tuple[int, bool]:
        if is_critical_hit is None:
            is_critical_hit = target.allows_critical_hits() and random.uniform(0, 1) < 1 / 32
        if is_critical_hit and target.allows_critical_hits():
            min_damage = self.get_attack_strength() // 2
            max_damage = self.get_attack_strength()
        else:
            min_damage = (self.get_attack_strength() - target.get_agility() // 2) // 4
            max_damage = (self.get_attack_strength() - target.get_agility() // 2) // 2
        damage = CombatCharacterState.calc_damage(
            min_damage,
            max_damage,
            target,
            damage_type)

        # For critical hits to targets which don't allow them, perform a second damage calculation and use the higher
        # of the two damage values.
        if is_critical_hit and not target.allows_critical_hits():
            damage = max(damage, CombatCharacterState.calc_damage(
                min_damage,
                max_damage,
                target,
                damage_type))

        return damage, is_critical_hit

    # TODO: Add spell checks and damage calc methods

    # TODO: Add method for determining available spells
    def get_castable_spells(self, is_in_combat: bool, is_inside: bool) -> List[Spell]:
        castable_spells = []
        for spell in self.get_available_spells():
            if spell.mp <= self.mp:
                if is_in_combat and not spell.available_in_combat:
                    continue
                if not is_in_combat and not spell.available_outside_combat:
                    continue
                if is_inside and not spell.available_inside:
                    continue
                if not is_inside and not spell.available_outside:
                    continue
                castable_spells.append(spell)
        return castable_spells

    def get_available_spells(self) -> List[Spell]:
        available_spells = []
        for level in self.character_type.levels:
            if level.number <= self.level.number and level.spell is not None:
                available_spells.append(level.spell)
        return available_spells

    def get_castable_spell_names(self, is_in_combat: bool, is_inside: bool) -> List[str]:
        return HeroState.get_spell_names(self.get_castable_spells(is_in_combat, is_inside))

    def get_available_spell_names(self) -> List[str]:
        return HeroState.get_spell_names(self.get_available_spells())

    def get_spell(self, name: str) -> Optional[Spell]:
        for spell in self.get_available_spells():
            if name == spell.name:
                return spell
        return None

    @staticmethod
    def get_spell_names(spells: List[Spell]) -> List[str]:
        spell_names = []
        for spell in spells:
            spell_names.append(spell.name)
        return spell_names

    def calc_level(self, xp: int) -> Level:
        if 0 == len(self.character_type.levels):
            return Level.create_null()
        for level in reversed(self.character_type.levels):
            if level.xp <= xp:
                return level
        return self.character_type.levels[0]

    def level_up_check(self) -> bool:
        leveled_up = False
        if self.level is not None:
            new_level = self.calc_level(self.xp)
            leveled_up = self.level != new_level
            self.level = new_level
            self.max_hp = self.level.hp
            self.max_mp = self.level.mp
        return leveled_up

    def is_ignoring_tile_penalties(self) -> bool:
        ret_val = not self.is_combat_character
        if not ret_val and self.armor is not None:
            ret_val = self.armor.ignores_tile_penalties
        return ret_val

    def calc_xp_to_next_level(self) -> int:
        if self.level is not None:
            for level in self.character_type.levels:
                if level.xp > self.level.xp:
                    return level.xp - self.xp
        return 0

    def inc_step_counter(self) -> None:
        if self.armor is not None and self.armor.hp_regen_tiles is not None:
            if self.hp_regen_tiles_remaining is None:
                self.hp_regen_tiles_remaining = self.armor.hp_regen_tiles
            self.hp_regen_tiles_remaining -= 1
            if 0 >= self.hp_regen_tiles_remaining:
                self.hp = min(self.max_hp, self.hp + 1)
                self.hp_regen_tiles_remaining = self.armor.hp_regen_tiles

    def __str__(self) -> str:
        return "%s(%s, %s, %s, %s, %s)" % (
            self.__class__.__name__,
            MapCharacterState.__str__(self),
            CombatCharacterState.__str__(self),
            self.name,
            self.level,
            self.xp)

    def __repr__(self) -> str:
        return "%s(%r, %r, %r, %r, %r)" % (
            self.__class__.__name__,
            MapCharacterState.__repr__(self),
            CombatCharacterState.__repr__(self),
            self.name,
            self.level,
            self.xp)


def main() -> None:
    # Test out character states
    hero_state = HeroState.create_null()
    print(hero_state, flush=True)
    while hero_state.is_alive():
        hero_state.hp -= 10
        print(hero_state, flush=True)


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
