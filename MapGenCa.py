#!/usr/bin/env python

from typing import List


class MapGenCa:
    staticmethod
    def genMapDat(width: int,
                  height: int) -> List[str]:
        dat = []
        dat.append('w'*(width+2))
        for y in range(height):
            dat.append('w' + '_'*width + 'w')
        dat.append('w'*(width+2))
        return dat


def main() -> None:
    from GameInfo import GameInfoMapViewer
    from GameTypes import Map

    # Generate and render a map
    map_name = 'mapGenCa'
    viewer = GameInfoMapViewer()
    viewer.game_info.maps[map_name] = Map.create(map_name, MapGenCa.genMapDat(50,50))
    viewer.view_map(map_name)


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
