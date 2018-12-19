#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import List, Optional, Union

from enum import Enum
import math
import pygame

from HeroParty import HeroParty
from Point import Point


class GameDialogSpacing(Enum):
    EQUAL_COLUMNS = 1
    OUTSIDE_JUSTIFIED = 2
    SPACERS = 3


class GameDialog:
    NOMINAL_HEALTH_FONT_COLOR = pygame.Color('white')
    LOW_HEALTH_FONT_COLOR = pygame.Color(252, 116, 96)

    win_size_tiles = Point(20, 15)
    tile_size_pixels = 48
    font_size = 32
    font_color = NOMINAL_HEALTH_FONT_COLOR
    font: pygame.Font
    outside_spacing_pixels = 24
    internal_spacing_pixels = 10
    selection_indicator_pixels = 16

    @staticmethod
    def static_init(win_size_tiles: Point,
                    tile_size_pixels: int) -> None:
        GameDialog.win_size_tiles = win_size_tiles
        GameDialog.tile_size_pixels = tile_size_pixels
        # GameDialog.font_size = 1
        # while pygame.font.SysFont('arial', GameDialog.font_size).get_height() < tile_size_pixels:
        #   GameDialog.font_size += 1
        # GameDialog.font_size -= 1
        # print('GameDialog.font_size =', GameDialog.font_size, flush=True)

        # Create font
        # TODO: Size font to tile_size_pixels
        # print('pygame.font.get_default_font() =', pygame.font.get_default_font(), flush=True)
        # print('pygame.font.get_fonts() =', pygame.font.get_fonts(), flush=True)
        GameDialog.font = pygame.font.SysFont('arial', GameDialog.font_size)
        # GameDialog.font = pygame.font.Font(None, GameDialog.tile_size_pixels)

    @staticmethod
    def get_size_for_content(longest_string: str,
                             num_rows: int,
                             title: Optional[str]) -> Point:
        width_pixels = 2 * GameDialog.outside_spacing_pixels + GameDialog.font.size(longest_string)[0]
        height_pixels = 2 * GameDialog.outside_spacing_pixels + num_rows * GameDialog.font.get_height() + (
                num_rows - 1) * GameDialog.internal_spacing_pixels
        if title is not None:
            width_pixels = max(width_pixels, 2 * GameDialog.outside_spacing_pixels + GameDialog.font.size(title)[0])
            height_pixels += GameDialog.font.get_height()
        return Point(math.ceil(width_pixels / GameDialog.tile_size_pixels), height_pixels / GameDialog.tile_size_pixels)

    @staticmethod
    def get_size_for_menu(options: Union[List[str], List[List[str]]],
                          num_cols: int,
                          title: Optional[str]) -> Point:
        row_data = GameDialog.convert_options_to_row_data(options, num_cols)
        num_rows = len(row_data)

        # Determine width
        longest_option_pixels = 0
        if isinstance(options[0], list):
            for option in options:
                option_pixels = 0
                for option_col in option:
                    option_pixels += GameDialog.font.size(option_col)[0] + 2 * GameDialog.internal_spacing_pixels
                if option_pixels > longest_option_pixels:
                    longest_option_pixels = option_pixels
        else:
            for option in options:
                option_pixels = GameDialog.font.size(option)[0]
                if option_pixels > longest_option_pixels:
                    longest_option_pixels = option_pixels
        width_pixels = 2 * GameDialog.outside_spacing_pixels + num_cols * (
                1.1 * longest_option_pixels
                + 2 * GameDialog.internal_spacing_pixels
                + GameDialog.selection_indicator_pixels)

        # Determine height
        if title is not None:
            height_pixels = GameDialog.outside_spacing_pixels + (
                        num_rows + 1) * GameDialog.font.get_height() + num_rows * GameDialog.internal_spacing_pixels
        else:
            height_pixels = 2 * GameDialog.outside_spacing_pixels + num_rows * GameDialog.font.get_height() + (
                        num_rows - 1) * GameDialog.internal_spacing_pixels
        return Point(math.ceil(width_pixels / GameDialog.tile_size_pixels), height_pixels / GameDialog.tile_size_pixels)

    def __init__(self,
                 pos_tile: Point,
                 size_tiles: Point,
                 title: Optional[str] = None) -> None:
        if pos_tile.x < 0:
            self.pos_tile = Point(GameDialog.win_size_tiles.x - size_tiles.x + pos_tile.x, pos_tile.y)
        else:
            self.pos_tile = Point(pos_tile)
        self.size_tiles = Point(size_tiles)
        self.title = title
        self.font_color = GameDialog.font_color

        # Initialize the image
        self.image = pygame.Surface((0, 0))
        self.intitialize_image()

        self.displayed_message_lines: List[str] = []
        self.remaining_message_lines: List[str] = []
        self.acknowledged = True

        self.row_data: Optional[List[List[Optional[str]]]] = None
        self.row_data_prompt: Optional[str] = None
        self.row_data_spacing: Optional[GameDialogSpacing] = None
        self.row_data_trailing_message_lines: List[str] = []
        self.is_menu = False
        self.menu_row = 0
        self.menu_col = 0
        self.menu_data: Optional[List[List[Optional[str]]]] = None

    def intitialize_image(self) -> None:
        self.image = pygame.Surface(self.size_tiles * GameDialog.tile_size_pixels)
        self.image.fill(pygame.Color('black'))
        pygame.draw.rect(self.image, self.font_color,
                         pygame.Rect(8, 8, self.image.get_width() - 16, self.image.get_height() - 16), 7)
        if self.title is not None:
            title_image = GameDialog.font.render(self.title, False, self.font_color, pygame.Color('black'))
            title_image_pos_x = (self.image.get_width() - title_image.get_width()) / 2
            self.image.fill(
                pygame.Color('black'),
                pygame.Rect(
                    title_image_pos_x - GameDialog.internal_spacing_pixels,
                    0,
                    title_image.get_width() + 2 * GameDialog.internal_spacing_pixels,
                    title_image.get_height()))
            self.image.blit(title_image, (title_image_pos_x, 0))

    @staticmethod
    def create_message_dialog(message_content: Optional[str] = None) -> GameDialog:
        dialog = GameDialog(
            Point(2, GameDialog.win_size_tiles.y / 2 + 1.5),
            Point(GameDialog.win_size_tiles.x - 4, (GameDialog.win_size_tiles.y - 1) / 2 - 2))
        if message_content is not None:
            dialog.add_message(message_content)
        return dialog

    @staticmethod
    def create_menu_dialog(pos_tile: Point,
                           size_tiles: Optional[Point],
                           title: Optional[str],
                           options: Union[List[str], List[List[str]]],
                           num_cols: int = 2,
                           spacing_type: GameDialogSpacing = GameDialogSpacing.EQUAL_COLUMNS) -> GameDialog:
        if size_tiles is None:
            size_tiles = GameDialog.get_size_for_menu(options, num_cols, title)
        dialog = GameDialog(pos_tile, size_tiles, title)
        dialog.add_menu_prompt(options, num_cols, spacing_type)
        return dialog

    @staticmethod
    def create_exploring_menu() -> GameDialog:
        return GameDialog.create_menu_dialog(
            Point(-1, 1),
            None,
            'COMMANDS',
            ['TALK', 'STATUS', 'STAIRS', 'SEARCH', 'SPELL', 'ITEM'],
            3)

    @staticmethod
    def create_encounter_menu() -> GameDialog:
        title: Optional[str] = 'COMMANDS'
        options: List[str] = ['FIGHT', 'SPELL', 'RUN', 'ITEM']
        num_cols: int = len(options)
        return GameDialog.create_menu_dialog(
            Point(-1, 1),
            Point(
                GameDialog.get_size_for_menu(['TALK', 'STATUS', 'STAIRS', 'SEARCH', 'SPELL', 'ITEM'], 3, title).w,
                GameDialog.get_size_for_menu(options, num_cols, title).h),
            title,
            options,
            num_cols)

    @staticmethod
    def create_yes_no_menu(pos_tile: Point,
                           prompt: Optional[str],
                           title: Optional[str] = None) -> GameDialog:
        size_tiles_menu = GameDialog.get_size_for_menu(['YES', 'NO'], 2, title)
        if prompt is not None:
            size_tiles_prompt = GameDialog.get_size_for_content(prompt, 2, title)
            size_tiles = Point(max(size_tiles_prompt.w, size_tiles_menu.w), size_tiles_prompt.h)
        else:
            size_tiles = size_tiles_menu
        dialog = GameDialog(pos_tile, size_tiles, title)
        if prompt is not None:
            dialog.add_message(prompt)
        dialog.add_yes_no_prompt()
        return dialog

    @staticmethod
    def create_status_dialog(pos_tile: Point,
                             size_tiles: Optional[Point],
                             title: Optional[str],
                             row_data: List[List[Optional[str]]],
                             spacing_type: GameDialogSpacing = GameDialogSpacing.OUTSIDE_JUSTIFIED,
                             trailing_message: Optional[str] = None) -> GameDialog:
        if size_tiles is None:
            # TODO: Calculate size based on row_data
            size_tiles = GameDialog.get_size_for_content('XP 1000000000', len(row_data), title)

            # Add in length for trailing_message
            if trailing_message is not None:
                size_pixels = size_tiles * GameDialog.tile_size_pixels
                trailing_message_lines = GameDialog.convert_message_to_lines(trailing_message, int(size_pixels.w))
                size_tiles = GameDialog.get_size_for_content(
                    'XP 1000000000', len(row_data) + len(trailing_message_lines), title)
        dialog = GameDialog(pos_tile, size_tiles, title)
        dialog.add_row_data(row_data, spacing_type=spacing_type, trailing_message=trailing_message)
        return dialog

    @staticmethod
    def create_exploring_status_dialog(party: HeroParty) -> GameDialog:
        if 1 == len(party.members):
            return GameDialog.create_status_dialog(
                Point(1, 1),
                None,
                party.main_character.name,
                [['LV', party.main_character.level.name],
                 ['HP', str(party.main_character.hp)],
                 ['MP', str(party.main_character.mp)],
                 ['GP', str(party.gp)],
                 ['XP', str(party.main_character.xp)]])
        else:
            # Use encounter dialog instead even when exploring for parties
            return GameDialog.create_encounter_status_dialog(party, 'Gold: ' + str(party.gp))

    @staticmethod
    def create_encounter_status_dialog(party: HeroParty, trailing_message: Optional[str] = None) -> GameDialog:
        title: Optional[str] = None
        if 1 == len(party.members):
            title = party.main_character.name
            status_data: List[List[Optional[str]]] = [['LV', party.main_character.level.name],
                                                      ['HP', str(party.main_character.hp)],
                                                      ['MP', str(party.main_character.mp)]]
        else:
            status_data = [[''],
                           ['LV'],
                           ['HP'],
                           ['MP']]
            for member in party.members:
                status_data[0].append(member.get_name())
                status_data[1].append(member.level.name)
                status_data[2].append(str(member.hp))
                status_data[3].append(str(member.mp))

        return GameDialog.create_status_dialog(
            Point(1, 1),
            None,
            title,
            status_data,
            trailing_message=trailing_message)

    @staticmethod
    def create_full_status_dialog(party: HeroParty) -> GameDialog:
        pc = party.main_character
        title = pc.name
        weapon_name = 'None'
        helm_name = 'None'
        armor_name = 'None'
        shield_name = 'None'
        if pc.weapon is not None:
            weapon_name = pc.weapon.name
        if pc.helm is not None:
            helm_name = pc.helm.name
        if pc.armor is not None:
            armor_name = pc.armor.name
        if pc.shield is not None:
            shield_name = pc.shield.name
        row_data: List[List[Optional[str]]] = [
            ['Level:', pc.level.name],
            ['Max Hit Points:', str(pc.level.hp)],
            ['Hit Points:', str(pc.hp)],
            ['Max Magic Points:', str(pc.level.mp)],
            ['Magic Points:', str(pc.mp)],
            ['Experience Points:', str(pc.xp)],
            ['Gold Pieces:', str(party.gp)],
            ['Strength:', str(pc.level.strength)],
            ['Agility:', str(pc.level.agility)],
            ['Attack Strength:', str(pc.get_attack_strength())],
            ['Defense Strength:', str(pc.get_defense_strength())],
            ['Weapon:', weapon_name],
            ['Helm:', helm_name],
            ['Armor:', armor_name],
            ['Shield:', shield_name]]
        return GameDialog.create_status_dialog(
            Point(1, 1),
            GameDialog.get_size_for_content('Experience Points 1000000000', len(row_data), title),
            title,
            row_data)

    @staticmethod
    def convert_message_to_lines(message: Optional[str], width_px: int) -> List[str]:
        lines: List[str] = []
        if message is None:
            return lines
        for line in message.split('\n'):
            line_to_display = ''
            for word in line.split(' '):
                # print('word =', word, flush=True)
                if line_to_display == '':
                    line_to_evaluate = word
                else:
                    line_to_evaluate = line_to_display + ' ' + word
                line_to_evaluate_size = Point(GameDialog.font.size(line_to_evaluate))
                # print('line_to_evaluate =', line_to_evaluate, flush=True)
                if line_to_evaluate_size[0] + 2 * GameDialog.outside_spacing_pixels <= width_px:
                    line_to_display = line_to_evaluate
                    # print('line_to_display =', line_to_display, flush=True)
                else:
                    lines.append(line_to_display)
                    line_to_display = word
                    # print('line_to_display =', line_to_display, flush=True)
            if line_to_display is not None:
                lines.append(line_to_display)
        return lines

    def add_message(self,
                    new_message: str,
                    append: bool = True) -> None:

        self.acknowledged = False
        self.row_data = None

        # Fix capitalization in message
        new_message = GameDialog.fix_capitalization(new_message)

        # Turn message into lines of text
        new_message_lines = GameDialog.convert_message_to_lines(new_message, self.image.get_width())

        # Determine the number of lines of text which can be displayed in the dialog
        # Subtract out 1 row to leave room for the waiting indicator
        num_rows = self.get_num_rows() - 1

        # Merge new message content with old message content
        if append and len(self.displayed_message_lines) > 0:
            if 0 == len(self.remaining_message_lines):
                if len(new_message_lines) <= num_rows:
                    if len(self.displayed_message_lines) + len(new_message_lines) <= num_rows:
                        self.displayed_message_lines += new_message_lines
                    else:
                        self.displayed_message_lines = self.displayed_message_lines[
                            len(self.displayed_message_lines) + len(new_message_lines) - num_rows:] + new_message_lines
                else:
                    self.displayed_message_lines = new_message_lines[0: num_rows]
                    self.remaining_message_lines = new_message_lines[num_rows:]
            else:
                self.remaining_message_lines += new_message_lines
                self.displayed_message_lines = self.remaining_message_lines[0: num_rows]
                self.remaining_message_lines = self.remaining_message_lines[num_rows:]
        else:
            self.displayed_message_lines = new_message_lines[0: num_rows]
            self.remaining_message_lines = new_message_lines[num_rows:]

        # Refresh image
        self.refresh_image()
        self.acknowledged = False

    def add_encounter_prompt(self,
                             options: List[str] = ['FIGHT', 'RUN', 'SPELL', 'ITEM'],
                             prompt: str = 'Command?') -> None:
        self.add_menu_prompt(options, len(options), GameDialogSpacing.SPACERS, prompt)

    def add_yes_no_prompt(self,
                          prompt: Optional[str] = None) -> None:
        self.add_menu_prompt(['YES', 'NO'], 2, GameDialogSpacing.SPACERS, prompt)

    @staticmethod
    def set_default_font_color(font_color: pygame.Color) -> None:
        GameDialog.font_color = font_color

    def set_font_color(self, font_color: pygame.Color) -> None:
        if font_color != self.font_color:
            self.font_color = font_color
            self.refresh_image()

    def is_empty(self) -> bool:
        return len(self.displayed_message_lines) + len(self.remaining_message_lines) == 0

    def is_last_row_blank(self) -> bool:
        if self.is_empty():
            return True
        return (self.displayed_message_lines + self.remaining_message_lines)[-1] == ''

    def has_more_content(self) -> bool:
        return len(self.remaining_message_lines) != 0

    def advance_content(self) -> None:
        if not self.has_more_content():
            return

        # Determine the number of lines of text which can be displayed in the dialog
        num_rows = self.get_num_rows()

        # Shift remainingMessageLines into displayedMessageLines
        self.displayed_message_lines = self.remaining_message_lines[0: num_rows]
        self.remaining_message_lines = self.remaining_message_lines[num_rows:]

        # Refresh image
        self.refresh_image()
        self.acknowledged = False

    def refresh_image(self) -> None:
        # Clear the image
        self.intitialize_image()

        # Blit lines to dialog
        col_pos_x = GameDialog.outside_spacing_pixels
        row_pos_y = self.get_starting_row_pos_y()
        for lines in self.displayed_message_lines:
            self.image.blit(GameDialog.font.render(lines, False, self.font_color, pygame.Color('black')),
                            (col_pos_x, row_pos_y))
            row_pos_y += GameDialog.font.get_height() + GameDialog.internal_spacing_pixels

        # Blit row data to dialog
        if self.row_data is not None and len(self.row_data) > 0:
            row_pos_y = self.get_row_pos_y(len(self.displayed_message_lines))
            num_cols = len(self.row_data[0])
            if self.row_data_spacing == GameDialogSpacing.OUTSIDE_JUSTIFIED and num_cols % 2 != 0:
                print('ERROR: refresh_image invoked with OUTSIDE_JUSTIFIED for odd num_cols =', num_cols, flush=True)
            first_col_pos_x = GameDialog.outside_spacing_pixels
            col_pos_x = first_col_pos_x
            if self.row_data_prompt is not None:
                first_col_pos_x += GameDialog.font.size(self.row_data_prompt)[0] + GameDialog.internal_spacing_pixels
                col_pos_x = first_col_pos_x - GameDialog.internal_spacing_pixels
                self.image.blit(GameDialog.font.render(self.row_data_prompt,
                                                       False,
                                                       self.font_color,
                                                       pygame.Color('black')),
                                (GameDialog.outside_spacing_pixels, row_pos_y))
            for row in range(len(self.row_data)):
                for col in range(num_cols):
                    if self.row_data[row][col] is None:
                        continue
                    if self.row_data_spacing == GameDialogSpacing.SPACERS:
                        col_pos_x += GameDialog.selection_indicator_pixels + 5 * GameDialog.internal_spacing_pixels
                        if col != 0:
                            col_pos_x += GameDialog.font.size(self.row_data[row][col - 1])[0]
                    elif self.row_data_spacing == GameDialogSpacing.OUTSIDE_JUSTIFIED and col % 2 == 1:
                        col_pos_x = self.image.get_width() * (col + 1) / num_cols\
                                    - GameDialog.font.size(self.row_data[row][col])[0]\
                                    - GameDialog.outside_spacing_pixels
                    else:
                        col_pos_x = first_col_pos_x + col * (
                                self.image.get_width() - first_col_pos_x - GameDialog.outside_spacing_pixels) / num_cols
                        if self.is_menu:
                            col_pos_x += GameDialog.selection_indicator_pixels + GameDialog.internal_spacing_pixels
                    self.image.blit(GameDialog.font.render(self.row_data[row][col],
                                                           False,
                                                           self.font_color,
                                                           pygame.Color('black')),
                                    (col_pos_x, row_pos_y))
                row_pos_y += GameDialog.font.get_height() + GameDialog.internal_spacing_pixels

            col_pos_x = GameDialog.outside_spacing_pixels
            for lines in self.row_data_trailing_message_lines:
                self.image.blit(GameDialog.font.render(lines, False, self.font_color, pygame.Color('black')),
                                (col_pos_x, row_pos_y))
                row_pos_y += GameDialog.font.get_height() + GameDialog.internal_spacing_pixels

            if self.is_menu:
                self.draw_menu_indicator()

    def get_starting_row_pos_y(self) -> int:
        return self.get_row_pos_y(0)

    def get_row_pos_y(self, row: int) -> int:
        if self.title is None:
            starting_row_pos_y = GameDialog.outside_spacing_pixels
        else:
            starting_row_pos_y = GameDialog.font.get_height() + GameDialog.internal_spacing_pixels
        return int(starting_row_pos_y + row * (GameDialog.font.get_height() + GameDialog.internal_spacing_pixels))

    def get_num_rows(self) -> int:
        # Determine the number of lines of text which can be displayed in the dialog
        num_rows = 2
        while self.get_row_pos_y(num_rows) <= self.image.get_height():
            num_rows += 1
        return num_rows - 1

    def add_menu_prompt(self,
                        options: Union[List[str], List[List[str]]],
                        num_cols: int,
                        spacing_type: GameDialogSpacing = GameDialogSpacing.EQUAL_COLUMNS,
                        prompt: Optional[str] = None) -> None:
        self.add_row_data(GameDialog.convert_options_to_row_data(options, num_cols), spacing_type, True, prompt)

    @staticmethod
    def convert_options_to_row_data(options: Union[List[str], List[List[str]]],
                                    num_cols: int) -> List[List[Optional[str]]]:
        num_rows = math.ceil(len(options) / num_cols)
        row_data = []
        cols_per_option = 1
        if len(options) > 0 and isinstance(options[0], list):
            cols_per_option = len(options[0])
        for row in range(num_rows):
            temp: List[Optional[str]] = []
            for col in range(num_cols):
                index_in_options = row + col * num_rows
                if index_in_options < len(options):
                    current_option = options[index_in_options]
                    if isinstance(current_option, list):
                        for item in current_option:
                            temp.append(item)
                    elif isinstance(current_option, str):
                        temp.append(current_option)
                else:
                    for colInner in range(cols_per_option):
                        temp.append(None)
            row_data.append(temp)
        return row_data

    def add_row_data(self,
                     row_data: List[List[Optional[str]]],
                     spacing_type: GameDialogSpacing = GameDialogSpacing.OUTSIDE_JUSTIFIED,
                     is_menu: bool = False,
                     prompt: Optional[str] = None,
                     trailing_message: Optional[str] = None) -> None:
        # NOTE:  spacing_type == OUTSIDE_JUSTIFIED assumes 2 columns in rowData
        # NOTE:  If is_menu and spacing_type == OUTSIDE_JUSTIFIED, each row constitutes a single menu item
        self.row_data = row_data
        self.row_data_prompt = prompt
        self.row_data_spacing = spacing_type
        self.row_data_trailing_message_lines = GameDialog.convert_message_to_lines(trailing_message,
                                                                                   self.image.get_width())
        self.is_menu = is_menu
        self.menu_row = 0
        self.menu_col = 0
        if is_menu:
            if spacing_type == GameDialogSpacing.OUTSIDE_JUSTIFIED:
                self.menu_data = []
                num_cols = len(row_data[0])
                for row in range(len(row_data)):
                    temp = []
                    for col in range(num_cols // 2):
                        temp.append(row_data[row][2 * col])
                    self.menu_data.append(temp)
            else:
                self.menu_data = row_data

        # Determine the number of lines of text which can be displayed in the dialog
        num_rows = self.get_num_rows()
        avail_rows = num_rows - len(self.displayed_message_lines)
        new_rows = len(row_data) + len(self.row_data_trailing_message_lines)
        if new_rows > avail_rows:
            self.displayed_message_lines = self.displayed_message_lines[new_rows - avail_rows:]

        # Refresh image
        self.refresh_image()

    def blit(self,
             surface: pygame.Surface,
             flip_buffer: bool = False,
             offset_pixels: Point = Point(0, 0)) -> None:
        surface.blit(self.image, self.pos_tile * GameDialog.tile_size_pixels + offset_pixels)
        if flip_buffer:
            pygame.display.flip()

    def erase(self,
              surface: pygame.Surface,
              background: pygame.Surface,
              flip_buffer: bool = False,
              offset_pixels: Point = Point(0, 0)) -> None:
        surface.blit(background.subsurface(pygame.Rect(self.pos_tile * GameDialog.tile_size_pixels + offset_pixels,
                                                       self.image.get_size())),
                     self.pos_tile * GameDialog.tile_size_pixels + offset_pixels)
        if flip_buffer:
            pygame.display.flip()

    def get_selected_menu_option(self) -> Optional[str]:
        if self.row_data is not None and self.menu_data is not None:
            return self.menu_data[self.menu_row][self.menu_col]
        return None

    def set_selected_menu_option(self, menu_item: str) -> None:
        if self.row_data is not None and self.menu_data is not None:
            for row in range(len(self.menu_data)):
                for col in range(len(self.menu_data[row])):
                    if menu_item == self.menu_data[row][col]:
                        self.erase_menu_indicator()
                        self.menu_row = row
                        self.menu_col = col
                        self.draw_menu_indicator()
                        break
        return None

    def erase_menu_indicator(self) -> None:
        self.draw_menu_indicator(pygame.Color('black'))

    def draw_menu_indicator(self, color: pygame.Color = None) -> None:
        if self.row_data is None or self.menu_data is None or len(self.menu_data) == 0:
            return

        if color is None:
            color = self.font_color

        first_col_pos_x = GameDialog.outside_spacing_pixels
        col_pos_x = first_col_pos_x
        if self.row_data_prompt is not None:
            first_col_pos_x += GameDialog.font.size(self.row_data_prompt)[0] + GameDialog.internal_spacing_pixels
            col_pos_x = first_col_pos_x - GameDialog.internal_spacing_pixels
        num_cols = len(self.menu_data[0])
        if self.row_data_spacing == GameDialogSpacing.SPACERS:
            for col in range(self.menu_col + 1):
                col_pos_x += 4 * GameDialog.internal_spacing_pixels
                if col != 0:
                    col_pos_x += GameDialog.font.size(self.menu_data[self.menu_row][col - 1])[
                                   0] + GameDialog.selection_indicator_pixels + GameDialog.internal_spacing_pixels
        else:
            col_pos_x = first_col_pos_x + self.menu_col * (
                        self.image.get_width() - first_col_pos_x - GameDialog.outside_spacing_pixels) / num_cols
        row_pos_y = self.get_row_pos_y(len(self.displayed_message_lines) + self.menu_row) + (
                    GameDialog.font.get_height() - GameDialog.internal_spacing_pixels) / 3
        pointlist = (
            (col_pos_x + 1 / 4 * GameDialog.selection_indicator_pixels,
             row_pos_y),
            (col_pos_x + 1 / 4 * GameDialog.selection_indicator_pixels,
             row_pos_y + GameDialog.selection_indicator_pixels),
            (col_pos_x + 3 / 4 * GameDialog.selection_indicator_pixels,
             row_pos_y + GameDialog.selection_indicator_pixels / 2))
        pygame.draw.polygon(self.image, color, pointlist)

    def erase_waiting_indicator(self) -> None:
        self.draw_waiting_indicator(pygame.Color('black'))

    def draw_waiting_indicator(self, color: Optional[pygame.Color] = None) -> None:
        if color is None:
            color = self.font_color
        col_pos_x = (self.image.get_width() - GameDialog.selection_indicator_pixels) / 2
        row_pos_y = self.get_row_pos_y(len(self.displayed_message_lines))
        pointlist = (
            (col_pos_x,
             row_pos_y + 1 / 4 * GameDialog.selection_indicator_pixels),
            (col_pos_x + GameDialog.selection_indicator_pixels,
             row_pos_y + 1 / 4 * GameDialog.selection_indicator_pixels),
            (col_pos_x + GameDialog.selection_indicator_pixels / 2,
             row_pos_y + 3 / 4 * GameDialog.selection_indicator_pixels))
        pygame.draw.polygon(self.image, color, pointlist)

    def process_event(self, event: pygame.Event, screen: pygame.Surface) -> None:
        if self.row_data is None or self.menu_data is None:
            return

        if event.type == pygame.KEYDOWN:
            num_cols = len(self.menu_data[0])
            new_col = self.menu_col
            num_rows = len(self.menu_data)
            new_row = self.menu_row
            if event.key == pygame.K_DOWN:
                new_row = (self.menu_row + 1) % num_rows
            elif event.key == pygame.K_UP:
                new_row = (self.menu_row - 1) % num_rows
            elif event.key == pygame.K_LEFT:
                new_col = (self.menu_col - 1) % num_cols
            elif event.key == pygame.K_RIGHT:
                new_col = (self.menu_col + 1) % num_cols

            # Skip over empty cells in menuOptions
            if self.menu_data[new_row][new_col] is None:
                if new_row != self.menu_row:
                    new_row = 0
                if new_col != self.menu_col:
                    new_col = 0

            if new_row != self.menu_row or new_col != self.menu_col:
                # Erase old indicator
                self.erase_menu_indicator()

                self.menu_row = new_row
                self.menu_col = new_col

                # Draw new indicator
                self.draw_menu_indicator()
                self.blit(screen, True)

    def acknowledge(self) -> None:
        self.acknowledged = True

    def is_acknowledged(self) -> bool:
        return self.acknowledged

    @staticmethod
    def fix_capitalization(message: str) -> str:
        for punctuation in ['.', '!', '?']:
            sentences = []
            for sentence in message.split(punctuation):
                start_of_sentence_index = len(sentence) - len(sentence.lstrip())
                if start_of_sentence_index < len(sentence):
                    sentence = (sentence[0:start_of_sentence_index]
                                + sentence[start_of_sentence_index].upper()
                                + sentence[start_of_sentence_index+1:])
                sentences.append(sentence)
            message = punctuation.join(sentences)
        return message


def main() -> None:
    # Initialize pygame
    pygame.init()
    pygame.font.init()

    # Setup the screen
    win_size_pixels = Point(1280, 960)
    tile_size_pixels = 48
    win_size_tiles = (win_size_pixels / tile_size_pixels).ceil()
    win_size_pixels = win_size_tiles * tile_size_pixels
    screen = pygame.display.set_mode(win_size_pixels, pygame.SRCALPHA | pygame.HWSURFACE)
    clock = pygame.time.Clock()
    pygame.key.set_repeat()

    # Test out game dialog
    GameDialog.static_init(win_size_tiles, tile_size_pixels)
    from HeroState import HeroState
    hero_party = HeroParty(HeroState.create_null())

    screen.fill(pygame.Color('pink'))
    GameDialog.create_exploring_status_dialog(hero_party).blit(screen, False)
    message_dialog = GameDialog.create_message_dialog('Hail!')
    message_dialog.draw_waiting_indicator()
    message_dialog.blit(screen, False)
    menu = GameDialog.create_exploring_menu()
    menu.blit(screen, True)

    is_awaiting_selection = True
    while is_awaiting_selection:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_awaiting_selection = False
                elif event.key == pygame.K_RETURN:
                    is_awaiting_selection = False
                    print('Selection made =', menu.get_selected_menu_option(), flush=True)
                else:
                    menu.process_event(event, screen)
            elif event.type == pygame.QUIT:
                is_awaiting_selection = False
        clock.tick(30)

    screen.fill(pygame.Color('pink'))
    GameDialog.create_encounter_status_dialog(hero_party).blit(screen, False)
    GameDialog.create_message_dialog(
        'word wrap testing...  Word wrap testing...  word wrap testing...  ' +
        'Word Wrap testing...  word Wrap testing...  Word Wrap testing...').blit(screen, False)
    menu = GameDialog.create_encounter_menu()
    menu.blit(screen, True)

    is_awaiting_selection = True
    while is_awaiting_selection:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_awaiting_selection = False
                elif event.key == pygame.K_RETURN:
                    is_awaiting_selection = False
                    print('Selection made =', menu.get_selected_menu_option(), flush=True)
                else:
                    menu.process_event(event, screen)
            elif event.type == pygame.QUIT:
                is_awaiting_selection = False
        clock.tick(30)

    screen.fill(pygame.Color('pink'))
    GameDialog.create_encounter_status_dialog(hero_party).blit(screen, False)
    message_dialog = GameDialog.create_message_dialog(
        'Hail 1!\nHail 2!\nHail 3!\nHail 4!\nHail 5!\nHail 6!\nHail 7!\nHail 8!\nHail 9!\nHail 10!\nHail 11!')
    while message_dialog.has_more_content():
        message_dialog.draw_waiting_indicator()
        message_dialog.blit(screen, True)
        pygame.time.wait(1000)
        message_dialog.advance_content()
    message_dialog.blit(screen, True)

    # messageDialog.addEncounterPrompt()
    message_dialog.add_menu_prompt(['Yes', 'No'], 2, GameDialogSpacing.SPACERS)
    message_dialog.set_font_color(GameDialog.LOW_HEALTH_FONT_COLOR)
    message_dialog.blit(screen, True)
    is_awaiting_selection = True
    while is_awaiting_selection:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_awaiting_selection = False
                elif event.key == pygame.K_RETURN:
                    is_awaiting_selection = False
                    print('Selection made =', message_dialog.get_selected_menu_option(), flush=True)
                else:
                    message_dialog.process_event(event, screen)
            elif event.type == pygame.QUIT:
                is_awaiting_selection = False
        clock.tick(30)
    message_dialog.add_message('\nLexie attacks!')
    message_dialog.blit(screen, True)
    pygame.time.wait(1000)

    # Terminate pygame
    pygame.font.quit()
    pygame.quit()


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
