#!/usr/bin/env python

from generic_utils.point import Point

from pydw.game_types import CharacterType, Direction


class MapCharacterState:
    """Data structure for the state of a character rendered to the map."""

    def __init__(self, character_type: CharacterType, pos_dat_tile: Point, direction: Direction) -> None:
        self.character_type = character_type
        self.curr_pos_dat_tile = Point(pos_dat_tile)
        self.dest_pos_dat_tile = Point(pos_dat_tile)
        self.curr_pos_offset_img_px = Point(0, 0)
        self.direction = direction

    def is_moving(self) -> bool:
        """Return true is the character is moving, else false."""
        return self.curr_pos_dat_tile != self.dest_pos_dat_tile

    def move(self, direction: Direction) -> None:
        """Update the state for movement in the specified direction.  Treated as a no-op when already moving."""
        if not self.is_moving():
            if self.direction != direction:
                self.direction = direction
            else:
                self.dest_pos_dat_tile = self.curr_pos_dat_tile + direction.get_vector()
        # else:
        #     print('Ignoring move as another move is already in progress', flush=True)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.character_type}, {self.curr_pos_dat_tile}, "
            f"{self.dest_pos_dat_tile}, {self.curr_pos_offset_img_px}, {self.direction})"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.character_type!r}, {self.curr_pos_dat_tile!r}, "
            f"{self.dest_pos_dat_tile!r}, {self.curr_pos_offset_img_px!r}, {self.direction!r})"
        )


def main() -> None:
    # TODO: Convert to unit test
    # Test out character states
    state = MapCharacterState(CharacterType.create_null(), Point(5, 6), Direction.SOUTH)
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
