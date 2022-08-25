#!/usr/bin/env python

from typing import List

import os.path

from pydw.game_map_viewer import GameMapViewer


def main() -> None:
    # Load the GameInfo - using GameMapViewer for convenience
    base_path = os.path.join(os.path.dirname(__file__), os.path.pardir)
    viewer = GameMapViewer(base_path)

    list_markdown_lines: List[str] = []
    table_markdown_lines: List[str] = []
    table_markdown_lines.append('<table>')
    table_markdown_lines.append('   <tr>')
    columns_per_row = 3
    current_columns_in_row = 0
    for encounter_background in viewer.game_info.encounter_backgrounds.values():
        if encounter_background.artist != 'Uncredited':
            if current_columns_in_row == columns_per_row:
                table_markdown_lines.append('   </tr>')
                table_markdown_lines.append('   <tr>')
                current_columns_in_row = 0

            list_markdown = '  * '
            table_markdown = '      <td>'
            if encounter_background.artist_url is not None:
                list_markdown += '['
                table_markdown += f'<a href="{encounter_background.artist_url}">'
            list_markdown += encounter_background.artist
            table_markdown += encounter_background.artist
            if encounter_background.artist_url is not None:
                list_markdown += f']({encounter_background.artist_url})'
                table_markdown += '</a>'
            list_markdown += ': '
            table_markdown += ': '
            if encounter_background.image_url is not None:
                list_markdown += '['
                table_markdown += f'<a href="{encounter_background.image_url}">'
            image_markdown = f'{encounter_background.name}<br><img alt="{encounter_background.name}" ' \
                        f'src="{os.path.relpath(encounter_background.image_path, base_path)}" width=200>'
            list_markdown += image_markdown
            table_markdown += image_markdown
            if encounter_background.image_url is not None:
                list_markdown += f']({encounter_background.image_url})'
                table_markdown += '</a>'
            table_markdown += '</td>'

            list_markdown_lines.append(list_markdown)
            table_markdown_lines.append(table_markdown)
            current_columns_in_row += 1

    table_markdown_lines.append('   </tr>')
    table_markdown_lines.append('</table>')

    print("List markdown:")
    for line in list_markdown_lines:
        print(line)

    print("Table markdown:")
    for line in table_markdown_lines:
        print(line)


if __name__ == '__main__':
    main()
