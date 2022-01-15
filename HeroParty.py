#!/usr/bin/env python

# Imports to support type annotations
from typing import List, Optional, Union
from GameTypes import ItemType

from GameTypes import DialogType, Direction
from HeroState import HeroState
from MapCharacterState import MapCharacterState
from MonsterParty import MonsterParty
from Point import Point


class HeroParty:
    def __init__(self, main_character: HeroState) -> None:
        self.main_character = main_character
        self.members = [main_character]  # in party order
        self.gp = 0
        self.progress_markers: List[str] = []

        self.light_diameter: Optional[float] = None  # None indicates the light diameter is unlimited
        self.light_diameter_decay_steps: Optional[int] = None
        self.light_diameter_decay_steps_remaining: Optional[int] = None

        self.repel_monsters = False
        self.repel_monsters_decay_steps_remaining: Optional[int] = None
        self.repel_monster_fade_dialog: Optional[DialogType] = None

        self.last_outside_map_name = ''
        self.last_outside_pos_dat_tile = Point()
        self.last_outside_dir = Direction.SOUTH

    @property
    def combat_members(self) -> List[HeroState]:
        return [member for member in self.members if member.is_combat_character]

    def add_member(self, member: HeroState, order: Optional[int]=None, is_main_character: bool=False) -> None:
        if is_main_character:
            self.main_character = member
        if member not in self.members:
            if order is None:
                if is_main_character:
                    # Add new members that will be the main character for the party to the front
                    self.members = [member] + self.members
                else:
                    # Add new members other than the main character to the back of the party
                    self.members.append(member)
            else:
                self.members.insert(order, member)
        else:
            print('ERROR: Cannot add a member that is already in the party', flush=True)

    def add_non_combat_member(self, name: str, member: MapCharacterState) -> None:
        self.add_member(HeroState(member.character_type,
                                  member.curr_pos_dat_tile,
                                  member.direction,
                                  name,
                                  is_combat_character=False))

    # Remove party member by name or reference
    def remove_member(self, member: Union[HeroState, str]) -> None:
        member_to_remove = self.get_member(member)
        if member_to_remove in self.members:
            if member_to_remove is not self.main_character:
                self.members.remove(member_to_remove)
            else:
                print('ERROR: Cannot remove main character from the party', flush=True)
        else:
            print('ERROR: Cannot remove member that it not in party', flush=True)

    # Set the main character - may add a new member to the party
    def set_main_character(self, member: Union[HeroState, str]) -> None:
        existing_member = self.get_member(member)
        if existing_member is not None:
            self.main_character = existing_member
        elif isinstance(member, HeroState):
            self.add_member(member, is_main_character=True)
        else:
            print('ERROR: Cannot add a new character from a name', flush=True)

    # Set positional order of a member in the party
    def set_member_order(self, member: Union[HeroState, str], order: int) -> None:
        existing_member = self.get_member(member)
        if existing_member is not None:
            self.members.remove(existing_member)
            self.members.insert(order, existing_member)
        else:
            print('ERROR: Cannot set position of member not in party', flush=True)

    # Get a member from the party by name or reference
    # Return None if the member is not found in the party
    def get_member(self, member: Union[HeroState, str]) -> Optional[HeroState]:
        if isinstance(member, HeroState):
            if member in self.members:
                return member
        elif isinstance(member, str):
            for party_member in self.members:
                if party_member.get_name() == member:
                    return party_member
        return None

    def has_item(self, name: str) -> bool:
        for member in self.members:
            if member.has_item(name):
                return True
        if name in self.progress_markers:
            return True
        return False

    def get_item_count(self, item_name: str) -> int:
        ret_val = 0
        for member in self.members:
            ret_val += member.get_item_count(item_name)
        if item_name in self.progress_markers:
            ret_val += 1
        return ret_val

    def get_item(self, item_name: str) -> Optional[ItemType]:
        for member in self.members:
            item = member.get_item(item_name)
            if item is not None:
                return item
        return None

    # TODO: Should gained items instead go into a communal party stash?
    def gain_item(self, item: ItemType, count: int = 1) -> None:
        self.main_character.gain_item(item, count)

    # Lose items
    # For lost items, first lose unequipped items then equipped items.
    # Start at the back of the party and move forward while skipping the main character then processing them last
    def lose_item(self, item_name: str, count: int = 1) -> None:
        traversal_list = self.members.copy()
        traversal_list.reverse()
        traversal_list.remove(self.main_character)
        traversal_list.append(self.main_character)
        remaining_count = count
        for member in traversal_list:
            member_lose_count = min(member.get_item_count(item_name, unequipped_only=True), remaining_count)
            if 0 < member_lose_count:
                member.lose_item(item_name, member_lose_count, unequipped_only=True)
                remaining_count -= member_lose_count
            if 0 == remaining_count:
                return
        for member in traversal_list:
            member_lose_count = min(member.get_item_count(item_name, unequipped_only=False), remaining_count)
            if 0 < member_lose_count:
                member.lose_item(item_name, member_lose_count, unequipped_only=False)
                remaining_count -= member_lose_count
            if 0 == remaining_count:
                return
        if 0 < remaining_count:
            print('ERROR: Remaining count of ' + str(remaining_count) + ' on attempt to lose ' + str(count) + ' of '
                  + item_name, flush=True)

    def gain_progress_marker(self, progress_marker: str) -> None:
        if progress_marker not in self.progress_markers:
            self.progress_markers.append(progress_marker)
            # print('Gained progress marker', progress_marker, flush=True)
        else:
            print('WARN: Did not add previously added progress marker', progress_marker, flush=True)

    def lose_progress_marker(self, progress_marker: str) -> None:
        if progress_marker in self.progress_markers:
            self.progress_markers.remove(progress_marker)
            # print('Lost progress marker', progress_marker, flush=True)
        else:
            print('WARN: Unable to remove progress marker', progress_marker, flush=True)

    def clear_combat_status_affects(self) -> None:
        for member in self.members:
            member.clear_combat_status_affects()

    def has_surviving_members(self) -> bool:
        for member in self.members:
            if member.is_alive():
                return True
        return False

    def is_still_in_combat(self) -> bool:
        for member in self.members:
            if member.is_still_in_combat():
                return True
        return False

    def get_still_in_combat_members(self) -> List[HeroState]:
        alive_members = []
        for member in self.members:
            if member.is_still_in_combat():
                alive_members.append(member)
        return alive_members

    def is_ignoring_tile_penalties(self) -> bool:
        for member in self.members:
            if not member.is_ignoring_tile_penalties():
                return False
        return True

    def get_curr_pos_dat_tile(self) -> Point:
        return self.members[0].curr_pos_dat_tile

    def get_curr_pos_offset_img_px(self) -> Point:
        return self.members[0].curr_pos_offset_img_px

    def dest_pos_dat_tile(self) -> Point:
        return self.members[0].dest_pos_dat_tile

    def get_direction(self) -> Direction:
        return self.members[0].direction

    def set_pos(self, pos: Point, direction: Direction) -> None:
        for member in self.members:
            member.curr_pos_dat_tile = member.dest_pos_dat_tile = pos
            member.curr_pos_offset_img_px = Point(0, 0)
            member.direction = direction

    def set_last_outside_pos(self, map_name: str, pos: Point, direction: Direction) -> None:
        self.last_outside_map_name = map_name
        self.last_outside_pos_dat_tile = pos
        self.last_outside_dir = direction

    # Optionally return dialog to indicate the fading of status effects.
    def inc_step_counter(self) -> Optional[DialogType]:
        # Depending on equipment heal party members over time
        for member in self.members:
            if member.is_alive():
                member.inc_step_counter()

        # Decay the light radius effect over time
        if self.light_diameter is not None and self.light_diameter_decay_steps_remaining is not None:
            self.light_diameter_decay_steps_remaining -= 1
            if 0 >= self.light_diameter_decay_steps_remaining:
                self.light_diameter = max(0.5, self.light_diameter-2)
                self.light_diameter_decay_steps_remaining = self.light_diameter_decay_steps

        # Decay the repel monsters effect over time
        if self.repel_monsters and self.repel_monsters_decay_steps_remaining is not None:
            self.repel_monsters_decay_steps_remaining -= 1
            if 0 >= self.repel_monsters_decay_steps_remaining:
                self.repel_monsters = False
                return self.repel_monster_fade_dialog

        return None

    def get_lowest_health_ratio(self) -> float:
        lowest_health_ratio = 1.0
        for member in self.members:
            if member.max_hp > 0:
                lowest_health_ratio = min(lowest_health_ratio, member.hp / member.max_hp)
        return lowest_health_ratio

    def get_highest_defense_strength(self) -> int:
        highest_defense_strength = 0
        for member in self.members:
            if member.is_alive():
                highest_defense_strength = max(highest_defense_strength, member.get_defense_strength())
        return highest_defense_strength

    def has_low_health(self) -> bool:
        return self.get_lowest_health_ratio() < 0.25

    # Get listing of all unequipped items for the party
    def get_item_row_data(self,
                          limit_to_droppable: bool = False,
                          filter_types: Optional[List[str]] = None) -> List[List[str]]:
        item_row_data: List[List[str]] = []
        for member in self.members:
            member_item_row_data = member.get_item_row_data(limit_to_droppable, True, filter_types)
            if 0 == len(item_row_data):
                item_row_data = member_item_row_data
            else:
                for member_row in member_item_row_data:
                    found = False
                    for row in item_row_data:
                        if member_row[0] == row[0]:
                            row[0] = str(int(member_row[0]) + int(row[0]))
                            found = True
                    if not found:
                        item_row_data.append(member_row)
        item_row_data.sort(key=lambda x: x[0])
        return item_row_data

    def is_monster_party_repelled(self, monster_party: MonsterParty, is_outside: bool) -> bool:
        # Repel only works outside
        if not self.repel_monsters or not is_outside:
            return False

        return (self.get_highest_defense_strength() // 2 >
                monster_party.get_highest_attack_strength() // 2)

    def __str__(self) -> str:
        return "%s(%s, %s, %s, %s)" % (
            self.__class__.__name__,
            self.main_character,
            self.members,
            self.gp,
            self.progress_markers)

    def __repr__(self) -> str:
        return "%s(%r, %r, %r, %r)" % (
            self.__class__.__name__,
            self.main_character,
            self.members,
            self.gp,
            self.progress_markers)


def main() -> None:
    from GameTypes import CharacterType, Direction
    character_type = CharacterType('myType', {}, [])
    hero_state = HeroState(character_type, Point(7, 3), Direction.WEST, 'Sir Me')
    hero_party = HeroParty(hero_state)
    print(hero_party, '\n', flush=True)
    for name in ['member1', 'member2', 'member3']:
        member = HeroState(character_type, Point(7, 3), Direction.WEST, name)
        hero_party.add_member(member)
        print(hero_party, '\n', flush=True)


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
