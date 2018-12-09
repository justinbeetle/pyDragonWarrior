#!/usr/bin/env python

# Imports to support type annotations
from typing import Dict, List, Union

from GameTypes import MonsterInfo, SpecialMonster
from MonsterState import MonsterState


class MonsterParty:
    NUMBERS = ['a', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    ORDINAL_NUMBERS = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth']

    def __init__(self, monsters: List[Union[MonsterInfo, SpecialMonster, MonsterState]] = []) -> None:
        self.members: List[MonsterState] = []
        for monster in monsters:
            self.add_monster(monster)

    def add_monster(self, monster: Union[MonsterInfo, SpecialMonster, MonsterState]) -> None:
        if isinstance(monster, MonsterState):
            self.members.append(monster)
        else:
            self.members.append(MonsterState(monster))
        self.set_unique_monster_names()

    # Set each monster to have a unique name in the party
    def set_unique_monster_names(self) -> None:
        # First count the number of monsters of each type
        overall_monster_type_to_count_map: Dict[str, int] = {}
        for monster in self.members:
            if monster.monster_info.name not in overall_monster_type_to_count_map:
                overall_monster_type_to_count_map[monster.monster_info.name] = 0
            overall_monster_type_to_count_map[monster.monster_info.name] += 1

        # Now make a second pass and give instances of any repeated monster types unique names
        current_monster_type_to_count_map: Dict[str, int] = {}
        for monster in self.members:
            # Use the default name if we have only 1 instance of the monster type in the party
            if 1 == overall_monster_type_to_count_map[monster.monster_info.name]:
                continue

            # Change from the default name (the monster) to a unique version including an ordinal number to
            # differentiate between individual instances of the same monster type.
            if monster.monster_info.name not in current_monster_type_to_count_map:
                current_monster_type_to_count_map[monster.monster_info.name] = 0
            monster.set_name('the '
                             + MonsterParty.ORDINAL_NUMBERS[
                                 current_monster_type_to_count_map[monster.monster_info.name]]
                             + ' ' + monster.monster_info.name)
            current_monster_type_to_count_map[monster.monster_info.name] += 1


    def is_still_in_combat(self) -> bool:
        for member in self.members:
            if member.is_still_in_combat():
                return True
        return False

    def get_still_in_combat_members(self) -> List[MonsterState]:
        alive_members = []
        for member in self.members:
            if member.is_still_in_combat():
                alive_members.append(member)
        return alive_members

    def get_default_approach_dialog(self) -> str:
        if 1 == len(self.members):
            return 'A ' + self.members[0].monster_info.name + ' draws near!'
        return MonsterParty.get_monster_summary(self.members) + ' draw near!'

    def get_defeated_monster_summary(self) -> str:
        #defeated_monsters = []
        #for monster in self.members:
        #    if monster.is_dead():
        #        defeated_monsters.append(monster)
        #return MonsterParty.get_monster_summary(defeated_monsters)
        terms = []
        for monster in self.members:
            if monster.is_dead():
                terms.append(monster.get_name())
        return MonsterParty.concatenate_string_list(terms)

    @staticmethod
    def get_monster_summary(monsters: List[MonsterState]) -> str:
        if 1 == len(monsters):
            return monsters[0].get_name()

        # First count the number of killed monsters of each type
        type_names = []
        monster_type_counts: Dict[str, int] = {}
        for monster in monsters:
            if monster.monster_info.name not in monster_type_counts:
                type_names.append(monster.monster_info.name)
                monster_type_counts[monster.monster_info.name] = 0
            monster_type_counts[monster.monster_info.name] += 1

        # Now make a second pass and generate a term for each monster type
        terms = []
        for type_name in type_names:
            term = MonsterParty.NUMBERS[monster_type_counts[type_name]-1] + ' ' + type_name
            if 1 != monster_type_counts[type_name]:
                term += 's'
            terms.append(term)

        # Finally concatenate the terms into a single string
        return MonsterParty.concatenate_string_list(terms)

    @staticmethod
    def concatenate_string_list(terms: List[str]) -> str:
        if 0 == len(terms):
            raise ValueError
        if 1 == len(terms):
            return terms[0]
        terms[-1] = 'and ' + terms[-1]
        if 2 == len(terms):
            return ' '.join(terms)
        else:
            return ', '.join(terms)

    # Get the number of monsters defeated
    def get_defeated_count(self) -> int:
        ret_val = 0
        for member in self.members:
            if member.is_dead():
                ret_val += 1
        return ret_val

    # Get the amount of gold pieces to award at completion of encounter
    def get_gp(self) -> int:
        ret_val = 0
        for member in self.members:
            if member.is_dead():
                ret_val += member.gp
        return ret_val

    # Get the amount of experiences to award at completion of encounter
    def get_xp(self) -> int:
        ret_val = 0
        for member in self.members:
            if member.is_dead():
                ret_val += member.xp
        return ret_val

    def __str__(self) -> str:
        return "%s(%s)" % (
            self.__class__.__name__,
            self.members)

    def __repr__(self) -> str:
        return "%s(%r)" % (
            self.__class__.__name__,
            self.members)


def main() -> None:
    pass


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
