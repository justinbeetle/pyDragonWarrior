#!/usr/bin/env python

import os.path

from pydw.game_map_viewer import GameMapViewer


def main() -> None:
    # Load the GameInfo - using GameMapViewer for convenience
    viewer = GameMapViewer(os.path.join(os.path.dirname(__file__), os.path.pardir))
    for encounter_background in viewer.game_info.encounter_backgrounds.values():
        if encounter_background.artist != 'Uncredited':
            markdown = '  * '
            if encounter_background.artist_url is not None:
                markdown += '['
            markdown += encounter_background.artist
            if encounter_background.artist_url is not None:
                markdown += f'](item.artist_url)'
            if encounter_background.image_url is not None:
                markdown += f': [{encounter_background.name}]({encounter_background.image_url})'
            print(markdown)


if __name__ == '__main__':
    main()
