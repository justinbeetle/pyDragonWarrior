#!/usr/bin/env python

# Imports to support type annotations
from typing import cast, Dict, List, Union

from pydw.combat_character_state import CombatCharacterState
from pydw.combat_party import CombatParty
from pydw.game_types import MonsterInfo, SpecialMonster
from pydw.monster_state import MonsterState


class MonsterParty(CombatParty):
    NUMBERS = [
        "a",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
    ]
    ORDINAL_NUMBERS = [
        "first",
        "second",
        "third",
        "fourth",
        "fifth",
        "sixth",
        "seventh",
        "eighth",
        "ninth",
        "tenth",
    ]

    def __init__(
        self, monsters: List[Union[MonsterInfo, SpecialMonster, MonsterState]] = []
    ) -> None:
        super().__init__()
        self.members: List[MonsterState] = []
        for monster in monsters:
            self.add_monster(monster)

    def get_combat_members(self) -> List[CombatCharacterState]:
        return cast(List[CombatCharacterState], self.members)

    def add_monster(
        self, monster: Union[MonsterInfo, SpecialMonster, MonsterState]
    ) -> None:
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
            monster.set_name(
                "the "
                + MonsterParty.ORDINAL_NUMBERS[
                    current_monster_type_to_count_map[monster.monster_info.name]
                ]
                + " "
                + monster.monster_info.name
            )
            current_monster_type_to_count_map[monster.monster_info.name] += 1

    def get_default_approach_dialog(self) -> str:
        if 1 == len(self.members):
            return "A " + self.members[0].monster_info.name + " draws near!"
        return MonsterParty.get_monster_summary(self.members) + " draw near!"

    def get_defeated_monster_summary(self) -> str:
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
            term = (
                MonsterParty.NUMBERS[monster_type_counts[type_name] - 1]
                + " "
                + type_name
            )
            if 1 != monster_type_counts[type_name]:
                term += "s"
            terms.append(term)

        # Finally concatenate the terms into a single string
        return MonsterParty.concatenate_string_list(terms)

    @staticmethod
    def concatenate_string_list(terms: List[str]) -> str:
        if 0 == len(terms):
            raise ValueError
        if 1 == len(terms):
            return terms[0]
        terms[-1] = "and " + terms[-1]
        if 2 == len(terms):
            return " ".join(terms)
        return ", ".join(terms)

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
        return f"{self.__class__.__name__}({self.members})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.members!r})"
