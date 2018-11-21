#!/usr/bin/env python

# Imports to support type annotations
from typing import List, Optional, Union
from GameTypes import ItemType

from GameTypes import Direction
from HeroState import HeroState
from Point import Point

class HeroParty:
    def __init__(self, main_character: HeroState) -> None:
        self.main_character = main_character
        self.members = [main_character]  # in party order
        self.gp = 0
        self.progress_markers: List[str] = []

    def add_member(self, member: HeroState, order: Optional[int]=None, is_main_character=False) -> None:
        if is_main_character:
            self.main_character = member
        if order is None:
            if is_main_character:
                # Add new members that will be the main character for the party to the front
                self.members = [member] + self.members
            else:
                # Add new members other than the main character to the back of the party
                self.members.append(member)
        else:
            self.members.insert(order, member)

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

    # Gain items (ItemType) or a progress marker (str)
    # Gained items always go to the main character
    # TODO: Should gained items instead go into a communal party stash?
    def gain_item(self, item: Union[ItemType, str], count: int = 1) -> None:
        if isinstance(item, str):
            if item not in self.progress_markers:
                self.progress_markers.append(item)
                # print('Added progress marker', item, flush=True)
            else:
                print('WARN: Did not add previously added progress marker', item, flush=True)
        else:
            self.main_character.gain_item(item, count)

    # Lose items
    # For lost items, first lose unequipped items then equipped items.
    # Start at the back of the party and move forward while skipping the main character then processing them last
    def lose_item(self, item_name: str, count: int = 1) -> Optional[ItemType]:
        ret_val = None
        traversal_list = reversed(self.members)
        traversal_list.remove(self.main_character)
        traversal_list.append(self.main_character)
        remaining_count = count
        for member in traversal_list:
            member_lose_count = min(member.get_item_count(item_name, unequipped_only=True), remaining_count)
            if 0 < member_lose_count:
                ret_val = member.lose_item(item_name, member_lose_count, unequipped_only=True)
                remaining_count -= member_lose_count
            if 0 == remaining_count:
                return ret_val
        for member in traversal_list:
            member_lose_count = min(member.get_item_count(item_name, unequipped_only=False), remaining_count)
            if 0 < member_lose_count:
                ret_val = member.lose_item(item_name, member_lose_count, unequipped_only=False)
                remaining_count -= member_lose_count
            if 0 == remaining_count:
                return ret_val
        if item_name in self.progress_markers:
            self.progress_markers.remove(item_name)
            # print('Removed progress marker', item_name, flush=True)
            remaining_count -= 1
        if 0 < remaining_count:
            print('ERROR: Remaining count of ' + str(remaining_count) + ' on attempt to lose ' + str(count) + ' of '
                  + item_name, flush=True)
        return ret_val

    def clear_combat_status_affects(self):
        for member in self.members:
            member.clear_combat_status_affects()

    def is_still_in_combat(self):
        for member in self.members:
            if member.is_still_in_combat():
                return True
        return False

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
            member.direction = direction

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
    # TODO: Test out HeroParty
    pass


if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
