#!/usr/bin/env python

from generic_utils.point import Point
from pydw.game_types import Direction, NpcInfo
from pydw.map_character_state import MapCharacterState


class NpcState(MapCharacterState):
    def __init__(self, npc_info: NpcInfo) -> None:
        super().__init__(
            character_type=npc_info.character_type,
            pos_dat_tile=npc_info.point,
            direction=npc_info.direction,
        )
        self.npc_info = npc_info
        self.is_talking = False
        self.talking_direction = Direction.SOUTH

    def set_talking(self, talking_pos_dat_tile: Point, talking_direction: Direction) -> None:
        """Update the NPC to move to and face the player character"""
        self.is_talking = True
        if talking_pos_dat_tile != self.dest_pos_dat_tile:
            if self.is_moving():
                # Turn the NPC around if walking away from the tile they should be talking from.
                self.direction = self.direction.get_opposite()
                self.dest_pos_dat_tile = talking_pos_dat_tile
            else:
                direction = Direction.get_optional_direction(talking_pos_dat_tile - self.curr_pos_dat_tile)
                self.direction = direction if direction else talking_direction
                self.dest_pos_dat_tile = talking_pos_dat_tile
        self.talking_direction = talking_direction

    def done_talking(self) -> None:
        """Update the NPC to resume their typical behavior once done talking."""
        self.is_talking = False

        # Stationary characters should resume looking in the default direction after talking to the
        # player.
        if not self.npc_info.walking:
            self.direction = self.npc_info.direction

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({MapCharacterState.__str__(self)}, {self.npc_info})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({MapCharacterState.__repr__(self)}, {self.npc_info!r})"


def main() -> None:
    # TODO: Convert to unit test

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
            traceback.format_exception(None, e, e.__traceback__),  # <- type(e) by docs, but ignored
            file=sys.stderr,
            flush=True,
        )
        traceback.print_exc()
