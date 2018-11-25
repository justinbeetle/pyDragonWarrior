#!/usr/bin/env python

from Point import Point
from GameTypes import CharacterType, Direction


class MapCharacterState:
    def __init__(self, character_type: CharacterType, pos_dat_tile: Point, direction: Direction) -> None:
        self.character_type = character_type
        self.curr_pos_dat_tile = Point(pos_dat_tile)
        self.dest_pos_dat_tile = Point(pos_dat_tile)
        self.curr_pos_offset_img_px = Point(0, 0)
        self.direction = direction

    def __str__(self) -> str:
        return "%s(%s, %s, %s, %s, %s)" % (self.__class__.__name__,
                                           self.character_type,
                                           self.curr_pos_dat_tile,
                                           self.dest_pos_dat_tile,
                                           self.curr_pos_offset_img_px,
                                           self.direction)

    def __repr__(self) -> str:
        return "%s(%r, %r, %r, %r, %r)" % (self.__class__.__name__,
                                           self.character_type,
                                           self.curr_pos_dat_tile,
                                           self.dest_pos_dat_tile,
                                           self.curr_pos_offset_img_px,
                                           self.direction)


def main() -> None:
    # Test out character states
    state = MapCharacterState(CharacterType.create_null(), Point(5, 6), Direction.SOUTH)
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
