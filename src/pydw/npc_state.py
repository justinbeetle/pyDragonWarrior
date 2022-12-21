#!/usr/bin/env python

from pydw.map_character_state import MapCharacterState
from pydw.game_types import NpcInfo


class NpcState(MapCharacterState):
    def __init__(self, npc_info: NpcInfo) -> None:
        super().__init__(
            character_type=npc_info.character_type,
            pos_dat_tile=npc_info.point,
            direction=npc_info.direction,
        )
        self.npc_info = npc_info

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({MapCharacterState.__str__(self)}, {self.npc_info})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({MapCharacterState.__repr__(self)}, {self.npc_info!r})"


def main() -> None:
    # TODO: Convert to unit test
    from pydw.game_types import Direction

    # Test out character states
    state = NpcState(NpcInfo.create_null())
    print(state, flush=True)
    state.direction = Direction.WEST
    print(state, flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import sys
        import traceback

        print(
            traceback.format_exception(
                None, e, e.__traceback__  # <- type(e) by docs, but ignored
            ),
            file=sys.stderr,
            flush=True,
        )
        traceback.print_exc()
