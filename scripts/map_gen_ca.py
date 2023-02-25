#!/usr/bin/env python

from typing import List

import os

from pydw.game_map_viewer import GameMapViewer
from pydw.game_types import Map


class MapGenCa:
    @staticmethod
    def gen_map_dat(width: int, height: int) -> List[str]:
        dat: List[str] = []
        dat.append("w" * (width + 2))
        for _ in range(height):
            dat.append("w" + "_" * width + "w")
        dat.append("w" * (width + 2))
        return dat


def main() -> None:
    # Generate and render a map
    map_name = "mapGenCa"
    viewer = GameMapViewer(os.path.join(os.path.dirname(__file__), os.path.pardir))
    viewer.game_info.maps[map_name] = Map.create(map_name, MapGenCa.gen_map_dat(50, 50))
    viewer.view_map(map_name)


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
