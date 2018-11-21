#!/usr/bin/env python

# Imports to support type annotations
from typing import List

from MonsterState import MonsterState


class MonsterParty:
    def __init__(self, monsters: List[MonsterState] = None) -> None:
        self.members = monsters

    def add_monster(self, monster: MonsterState):
        self.members.append(monster)

    def is_still_in_combat(self):
        for member in self.members:
            if member.is_still_in_combat():
                return True
        return False

    def get_default_approach_dialog(self) -> str:
        # TODO: Update for monster parties with multiple members
        return 'A ' + self.members[0].get_name() + ' draws near!'

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
        return False

    def __str__(self) -> str:
        return "%s(%s)" % (
            self.__class__.__name__,
            self.members)

    def __repr__(self) -> str:
        return "%s(%r)" % (
            self.__class__.__name__,
            self.members)


def main() -> None:
    # TODO: Test out HeroParty
    pass


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
