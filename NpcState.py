#!/usr/bin/env python

from MapCharacterState import MapCharacterState
from GameTypes import NpcInfo


class NpcState(MapCharacterState):
    def __init__(self, npc_info: NpcInfo) -> None:
        super(NpcState, self).__init__(type_name=npc_info.type,
                                       pos_dat_tile=npc_info.point,
                                       direction=npc_info.direction)
        self.npc_info = npc_info

    def __str__(self) -> str:
        return "%s(%s, %s)" % (self.__class__.__name__,
                               super(NpcState, self).__str__(),
                               self.npc_info)

    def __repr__(self) -> str:
        return "%s(%r, %r)" % (self.__class__.__name__,
                               super(NpcState, self).__repr__(),
                               self.npc_info)


def main() -> None:
    from Point import Point
    from GameTypes import Direction

    # Test out character states
    npc_info = NpcInfo(type='myType',
                       point=Point(5, 6),
                       direction=Direction.SOUTH,
                       walking=False)
    state = NpcState(npc_info)
    print(state, flush=True)
    state.direction = Direction.WEST
    print(state, flush=True)


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
