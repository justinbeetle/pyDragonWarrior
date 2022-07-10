#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import cast, List, Optional, Tuple, Union

from enum import Enum
import math
import os
import pygame

from generic_utils.point import Point

import pygame_utils.game_events as GameEvents

from pydw.hero_party import HeroParty


class GameDialogSpacing(Enum):
    EQUAL_COLUMNS = 1
    OUTSIDE_JUSTIFIED = 2
    SPACERS = 3


class GameDialog:
    NOMINAL_HEALTH_FONT_COLOR = pygame.Color('white')
    LOW_HEALTH_FONT_COLOR = pygame.Color(252, 116, 96)

    SHIFT_UNICODE = '\u21e7'
    CAPSLOCK_UNICODE = '\u21ea'
    BACKSPACE_UNICODE = '\u232b'
    ENTER_UNICODE = '\u21b5'
    UNICODE_CHARACTERS = [SHIFT_UNICODE, CAPSLOCK_UNICODE, BACKSPACE_UNICODE, ENTER_UNICODE]

    # True =  Use menus for all text entry
    # False = Type on keyboard for all text entry
    # None  = Use menus for all text entry when a gamepad/joystick is present, else use the keyboard
    force_use_menus_for_text_entry: Optional[bool] = None

    win_size_tiles = Point(20, 15)
    tile_size_pixels = 48
    default_font_color = NOMINAL_HEALTH_FONT_COLOR
    font: pygame.Font
    widest_character: int = 0
    anti_alias = True
    outside_spacing_pixels = 24
    internal_spacing_pixels = 10
    selection_indicator_pixels = 16
    border_image: Optional[pygame.surface.Surface] = None

    @staticmethod
    def static_init(win_size_tiles: Point,
                    tile_size_pixels: int,
                    font_names: List[str] = [],
                    border_image_filename: Optional[str] = None) -> None:
        GameDialog.win_size_tiles = win_size_tiles
        GameDialog.tile_size_pixels = tile_size_pixels
        if border_image_filename is not None:
            try:
                image = pygame.image.load(border_image_filename)

                # Expect the border image to be square
                if image.get_width() != image.get_height() and 0 == image.get_width() % 3:
                    print('ERROR: The dialog border image must be square with a size divisible by 3', flush=True)
                    GameDialog.border_image = None
                else:
                    scale_factor = tile_size_pixels // (image.get_width() // 3) - 1
                    if scale_factor > 0:
                        scale_size = image.get_width() * scale_factor
                        GameDialog.border_image = pygame.transform.scale(image, (scale_size, scale_size))
                    else:
                        GameDialog.border_image = image
            except:
                print('ERROR: Failed to load', border_image_filename, flush=True)

        # Determine fonts
        def find_font_by_name(font_names: List[str], default_font_name: Optional[str] = None) -> Optional[str]:
            font_name = default_font_name
            for name in font_names:
                if name in pygame.font.get_fonts():
                    font_name = name
                    # print('Found system font', name, flush=True)
                    break
                elif os.path.exists(name):
                    font_name = name
                    # print('Found font', name, flush=True)
                    break
                else:
                    print('WARN: Failed to load font', name, flush=True)
            return font_name

        font_name = find_font_by_name(font_names, None)

        # Log information about available fonts if using the default font
        if font_name is None:
            print('pygame.font.get_default_font() =', pygame.font.get_default_font(), flush=True)
            print('pygame.font.get_fonts() =', pygame.font.get_fonts(), flush=True)

        # Determine font size by sizing it based on the tile size
        def calc_font_size(font_name: Optional[str]) -> int:
            font_size = 1
            while create_font(font_name, font_size).get_height() < tile_size_pixels - GameDialog.internal_spacing_pixels:
                font_size += 1
            font_size -= 1
            # print('Calculated font size of {} for font {}'.format(font_name, font_size), flush=True)
            return font_size

        # Create fonts
        def create_font(font_name: Optional[str], font_size: Optional[int] = None) -> pygame.Font:
            if font_size is None:
                font_size = calc_font_size(font_name)
            if font_name in pygame.font.get_fonts():
                return pygame.font.SysFont(font_name, font_size)
            return pygame.font.Font(font_name, font_size)

        GameDialog.font = create_font(font_name)

        # Determine the widest character
        for character in GameDialog.get_all_characters():
            GameDialog.widest_character = max(GameDialog.widest_character, GameDialog.get_font_width(character))

    @staticmethod
    def get_size_for_content(longest_string: str,
                             num_rows: int,
                             title: Optional[str]) -> Point:
        width_pixels = 2 * GameDialog.outside_spacing_pixels + GameDialog.get_font_width(longest_string)
        height_pixels = 2 * GameDialog.outside_spacing_pixels + num_rows * GameDialog.font.get_height() + (
                num_rows - 1) * GameDialog.internal_spacing_pixels
        if title is not None:
            width_pixels = max(width_pixels, 2 * GameDialog.outside_spacing_pixels + GameDialog.get_font_width(title))
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
        for option in options:
            if isinstance(option, str):
                option_pixels = GameDialog.get_font_width(option)
            else:
                option_pixels = 0
                for option_col in option:
                    option_pixels += GameDialog.get_font_width(option_col) + 2 * GameDialog.internal_spacing_pixels

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

    @staticmethod
    def get_font(text: str) -> pygame.Font:
        return GameDialog.font

    @staticmethod
    def get_font_width(text: str) -> int:
        if text in GameDialog.UNICODE_CHARACTERS:
            return GameDialog.widest_character
        return int(GameDialog.get_font(text).size(text)[0])

    @staticmethod
    def render_font(text: str, color: pygame.Color) -> pygame.surface.Surface:
        if text in GameDialog.UNICODE_CHARACTERS:
            width = GameDialog.get_font_width(text)
            height = GameDialog.get_font(text).get_height()
            font_surface = pygame.Surface((width, height))

            inner_border = 4
            half_inner_width = 1
            inner_width = half_inner_width * 2

            quarter_width = width // 4
            full_width = width - 1
            quarter_height = height // 4
            half_height = quarter_height * 2
            three_quarters_height = quarter_height * 3

            y_coords = (quarter_height + inner_border,
                        half_height - half_inner_width,
                        half_height,
                        half_height + half_inner_width,
                        three_quarters_height - inner_border)

            if text == GameDialog.BACKSPACE_UNICODE:
                # Draw the outer shape
                pointlist = [
                    (0, half_height),
                    (quarter_width, quarter_height),
                    (full_width, quarter_height),
                    (full_width, three_quarters_height),
                    (width // 4, three_quarters_height)]
                pygame.draw.aalines(font_surface, color, True, pointlist)
                pygame.draw.polygon(font_surface, color, pointlist)

                # Draw the inner shape
                x_start = quarter_width + inner_border
                x_mid = quarter_width + (full_width - quarter_width) // 2
                x_end = x_start + (x_mid - x_start) * 2
                x_coords = [x_start, x_start + inner_width,
                            x_mid - half_inner_width, x_mid, x_mid + half_inner_width,
                            x_end - inner_width, x_end]
                pointlist = [
                    (x_coords[0], y_coords[0]),
                    (x_coords[1], y_coords[0]),
                    (x_coords[3], y_coords[1]),
                    (x_coords[5], y_coords[0]),
                    (x_coords[6], y_coords[0]),
                    (x_coords[4], y_coords[2]),
                    (x_coords[6], y_coords[4]),
                    (x_coords[5], y_coords[4]),
                    (x_coords[3], y_coords[3]),
                    (x_coords[1], y_coords[4]),
                    (x_coords[0], y_coords[4]),
                    (x_coords[2], y_coords[2])]
                pygame.draw.aalines(font_surface, 'black', True, pointlist)
                pygame.draw.polygon(font_surface, 'black', pointlist)
                return font_surface
            elif text == GameDialog.ENTER_UNICODE:
                # Draw the outer shape
                pointlist = [
                    (0, quarter_height),
                    (full_width, quarter_height),
                    (full_width, three_quarters_height),
                    (0, three_quarters_height)]
                pygame.draw.aalines(font_surface, color, True, pointlist)
                pygame.draw.polygon(font_surface, color, pointlist)

                # Draw the inner shape
                x_start = inner_border
                x_end = full_width - inner_border
                x_coords = [x_start, width // 2, x_end - inner_width, x_end]
                pointlist = [
                    (x_coords[0], y_coords[2]),
                    (x_coords[1], y_coords[0]),
                    (x_coords[1], y_coords[1]),
                    (x_coords[2], y_coords[1]),
                    (x_coords[2], y_coords[0]),
                    (x_coords[3], y_coords[0]),
                    (x_coords[3], y_coords[3]),
                    (x_coords[1], y_coords[3]),
                    (x_coords[1], y_coords[4])]
                pygame.draw.aalines(font_surface, 'black', True, pointlist)
                pygame.draw.polygon(font_surface, 'black', pointlist)
                return font_surface
        return cast(pygame.surface.Surface,
                    GameDialog.get_font(text).render(text,
                                                     GameDialog.anti_alias,
                                                     color,
                                                     pygame.Color('black')))

    @staticmethod
    def use_menus_for_text_entry() -> bool:
        if GameDialog.force_use_menus_for_text_entry is None:
            return GameEvents.setup_joystick()
        return GameDialog.force_use_menus_for_text_entry

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
        self.font_color = GameDialog.default_font_color

        # Initialize the image
        self.image = pygame.surface.Surface((0, 0))
        self.initialize_image()

        self.displayed_message_lines: List[str] = []
        self.remainder_of_current_line: str = ''
        self.remaining_message_lines: List[str] = []
        self.acknowledged = True
        self.lines_since_last_acknowledgement = 0
        self.is_in_quotation = False

        self.row_data: Optional[List[List[Optional[str]]]] = None
        self.row_data_prompt: Optional[str] = None
        self.row_data_spacing: Optional[GameDialogSpacing] = None
        self.row_data_trailing_message_lines: List[str] = []
        self.is_menu = False
        self.menu_row = 0
        self.menu_col = 0
        self.menu_data: Optional[List[List[Optional[str]]]] = None

        self.allow_user_typing = False
        self.user_text_prompt = ''
        self.user_text = ''
        self.input_allowed_characters: Optional[str] = None

    def initialize_image(self) -> None:
        self.image = pygame.surface.Surface(self.size_tiles * GameDialog.tile_size_pixels)
        self.image.fill('black')
        if GameDialog.border_image is not None:
            border_image = GameDialog.border_image.convert().copy()
            pygame.transform.threshold(border_image,
                                       border_image,
                                       search_color=pygame.Color('white'),
                                       set_color=self.font_color,
                                       inverse_set=True)

            border_px = border_image.get_width() // 3
            src_size = (border_px, border_px)
            middle_width_span = self.image.get_width() - 2 * border_px
            middle_height_span = self.image.get_height() - 2 * border_px

            # Top Left Corner
            src_pos = dst_pos = (0, 0)
            self.image.blit(border_image, dst_pos, pygame.Rect(src_pos, src_size))
            # Top Middle
            src_pos = dst_pos = (border_px, 0)
            dst_size = (middle_width_span, border_px)
            pygame.transform.scale(border_image.subsurface(pygame.Rect(src_pos, src_size)), dst_size,
                                   self.image.subsurface(pygame.Rect(dst_pos, dst_size)))
            # Top Right Corner
            src_pos = (border_px + border_px, 0)
            dst_pos = (border_px + middle_width_span, 0)
            self.image.blit(border_image, dst_pos, pygame.Rect(src_pos, src_size))
            # Left Middle
            src_pos = (0, border_px)
            dst_pos = (0, border_px)
            dst_size = (border_px, middle_height_span)
            pygame.transform.scale(border_image.subsurface(pygame.Rect(src_pos, src_size)), dst_size,
                                   self.image.subsurface(pygame.Rect(dst_pos, dst_size)))
            # Right Middle
            src_pos = (border_px + border_px, border_px)
            dst_pos = (border_px + middle_width_span, border_px)
            dst_size = (border_px, middle_height_span)
            pygame.transform.scale(border_image.subsurface(pygame.Rect(src_pos, src_size)),
                                   dst_size,
                                   self.image.subsurface(pygame.Rect(dst_pos, dst_size)))
            # Bottom Left Corner
            src_pos = (0, border_px + border_px)
            dst_pos = (0, border_px + middle_height_span)
            self.image.blit(border_image, dst_pos, pygame.Rect(src_pos, src_size))
            # Bottom Middle
            src_pos = (border_px, border_px + border_px)
            dst_pos = (border_px, border_px + middle_height_span)
            dst_size = (middle_width_span, border_px)
            pygame.transform.scale(border_image.subsurface(pygame.Rect(src_pos, src_size)), dst_size,
                                   self.image.subsurface(pygame.Rect(dst_pos, dst_size)))
            # Bottom Right Corner
            src_pos = (border_px + border_px, border_px + border_px)
            dst_pos = (border_px + middle_width_span, border_px + middle_height_span)
            self.image.blit(border_image, dst_pos, pygame.Rect(src_pos, src_size))
        else:
            outside_border_width = 5
            inside_border_width = 4
            pygame.draw.rect(self.image, self.font_color,
                             pygame.Rect(outside_border_width,
                                         outside_border_width,
                                         self.image.get_width() - 2 * outside_border_width,
                                         self.image.get_height() - 2 * outside_border_width),
                             inside_border_width)
        if self.title is not None:
            title_image = GameDialog.render_font(self.title, self.font_color)
            title_image_pos_x = (self.image.get_width() - title_image.get_width()) / 2
            self.image.fill(
                'black',
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
            ['TALK', 'SPELL', 'ITEM', 'STATUS', 'SEARCH', 'OPEN'],
            3)

    @staticmethod
    def create_encounter_menu() -> GameDialog:
        title: Optional[str] = 'COMMANDS'
        options: List[str] = ['FIGHT', 'SPELL', 'RUN', 'ITEM']
        num_cols: int = len(options)
        return GameDialog.create_menu_dialog(
            Point(-1, 1),
            Point(
                GameDialog.get_size_for_menu(['TALK', 'SPELL', 'ITEM', 'STATUS', 'SEARCH', 'OPEN'], 3, title).w,
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
            dialog.add_message(prompt, fully_populate=True)
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
            longest_string = 'Health '+'10000000'*(len(row_data[0])-1)
            size_tiles = GameDialog.get_size_for_content(longest_string, len(row_data), title)

            # Add in length for trailing_message
            if trailing_message is not None:
                size_pixels = size_tiles * GameDialog.tile_size_pixels
                trailing_message_lines = GameDialog.convert_message_to_lines(trailing_message, int(size_pixels.w))
                size_tiles = GameDialog.get_size_for_content(longest_string,
                                                             len(row_data) + len(trailing_message_lines),
                                                             title)

        dialog = GameDialog(pos_tile, size_tiles, title)
        dialog.add_row_data(row_data, spacing_type=spacing_type, trailing_message=trailing_message)
        return dialog

    @staticmethod
    def create_persistent_status_dialog(party: HeroParty) -> GameDialog:
        title: Optional[str] = None
        if 1 == len(party.combat_members):
            title = party.main_character.name
            spacing_type = GameDialogSpacing.OUTSIDE_JUSTIFIED
            status_data: List[List[Optional[str]]] = [['Level', party.main_character.level.name],
                                                      ['Health', str(party.main_character.hp)],
                                                      ['Magic', str(party.main_character.mp)]]
        else:
            spacing_type = GameDialogSpacing.EQUAL_COLUMNS
            status_data = [[''],
                           ['Level'],
                           ['Health'],
                           ['Magic']]
            for member in party.combat_members:
                status_data[0].append(member.get_name())
                status_data[1].append(member.level.name)
                status_data[2].append(str(member.hp))
                status_data[3].append(str(member.mp))

        return GameDialog.create_status_dialog(
            Point(1, 1),
            None,
            title,
            status_data,
            spacing_type=spacing_type)

    @staticmethod
    def create_exploring_status_dialog(party: HeroParty) -> GameDialog:
        return GameDialog.create_encounter_status_dialog(party)

    @staticmethod
    def create_encounter_status_dialog(party: HeroParty) -> GameDialog:
        title: Optional[str] = None
        trailing_message: Optional[str] = None
        if 1 == len(party.combat_members):
            title = party.main_character.name
            spacing_type = GameDialogSpacing.OUTSIDE_JUSTIFIED
            status_data: List[List[Optional[str]]] = [['Level', party.main_character.level.name],
                                                      ['Health', str(party.main_character.hp)],
                                                      ['Magic', str(party.main_character.mp)],
                                                      ['XP', str(party.main_character.xp)],
                                                      ['Gold', str(party.gp)]]
        else:
            spacing_type = GameDialogSpacing.EQUAL_COLUMNS
            status_data = [[''],
                           ['Level'],
                           ['Health'],
                           ['Magic'],
                           ['XP']]
            for member in party.combat_members:
                status_data[0].append(member.get_name())
                status_data[1].append(member.level.name)
                status_data[2].append(str(member.hp))
                status_data[3].append(str(member.mp))
                status_data[4].append(str(member.xp))

            trailing_message = f'Gold: {party.gp}'

        return GameDialog.create_status_dialog(
            Point(1, 1),
            None,
            title,
            status_data,
            spacing_type=spacing_type,
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
            ['Level', pc.level.name],
            ['Max Hit Points', str(pc.level.hp)],
            ['Hit Points', str(pc.hp)],
            ['Max Magic Points', str(pc.level.mp)],
            ['Magic Points', str(pc.mp)],
            ['Experience Points', str(pc.xp)],
            ['Gold Pieces', str(party.gp)],
            ['Strength', str(pc.level.strength)],
            ['Agility', str(pc.level.agility)],
            ['Attack Strength', str(pc.get_attack_strength())],
            ['Defense Strength', str(pc.get_defense_strength())],
            ['Weapon', weapon_name],
            ['Helm', helm_name],
            ['Armor', armor_name],
            ['Shield', shield_name]]
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
                    append: bool = True,
                    fully_populate: bool = False) -> None:

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
            if fully_populate:
                if 0 == len(self.remaining_message_lines):
                    if len(new_message_lines) <= num_rows:
                        if len(self.displayed_message_lines) + len(new_message_lines) <= num_rows:
                            self.displayed_message_lines += new_message_lines
                        else:
                            self.displayed_message_lines = self.displayed_message_lines[
                                                           len(self.displayed_message_lines) +
                                                           len(new_message_lines) - num_rows:] + new_message_lines
                    else:
                        self.displayed_message_lines = new_message_lines[0: num_rows]
                        self.remaining_message_lines = new_message_lines[num_rows:]
                else:
                    self.displayed_message_lines = self.remaining_message_lines[0: num_rows]
                    self.remaining_message_lines = self.remaining_message_lines[num_rows:]
            else:
                if 0 == len(self.remainder_of_current_line) and 0 == len(self.remaining_message_lines):
                    if len(self.displayed_message_lines) >= num_rows:
                        self.displayed_message_lines = self.displayed_message_lines[1:]
                    self.displayed_message_lines += ['']
                    self.remainder_of_current_line = new_message_lines[0]
                    self.remaining_message_lines = new_message_lines[1:]
                else:
                    self.remaining_message_lines += new_message_lines
        else:
            if fully_populate:
                self.displayed_message_lines = new_message_lines[0: num_rows]
                self.remaining_message_lines = new_message_lines[num_rows:]
            else:
                self.displayed_message_lines = ['']
                self.remainder_of_current_line = new_message_lines[0]
                self.remaining_message_lines = new_message_lines[1:]

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
    def get_default_font_color() -> pygame.Color:
        return GameDialog.default_font_color

    @staticmethod
    def set_default_font_color(font_color: pygame.Color) -> None:
        GameDialog.default_font_color = font_color

    def set_font_color(self, font_color: pygame.Color) -> None:
        if font_color != self.font_color:
            self.font_color = font_color
            self.refresh_image()

    def is_empty(self) -> bool:
        return (len(self.displayed_message_lines) == 0 and
                len(self.remainder_of_current_line) == 0 and
                len(self.remaining_message_lines) == 0)

    def clear(self) -> None:
        self.displayed_message_lines = []
        self.remainder_of_current_line = ''
        self.remaining_message_lines = []
        self.row_data = None

    def is_last_row_blank(self) -> bool:
        if self.is_empty():
            return True
        elif 0 == len(self.remaining_message_lines):
            return self.displayed_message_lines[-1] + self.remainder_of_current_line == ''
        else:
            return self.remaining_message_lines[-1] == ''

    def has_more_content(self) -> bool:
        return len(self.remainder_of_current_line) + len(self.remaining_message_lines) != 0

    def advance_content(self) -> Tuple[bool, bool]:
        '''
        :return (should_wait_for_acknowledgement, is_new_content_part_of_quotation):
        should_wait_for_acknowledgement = Whether an acknowledged is required before rolling to the next line of text
        is_new_content_part_of_quotation = Whether the new characters, whether in part or whole, are part of a quotation
        '''
        if not self.has_more_content():
            return False, False

        # Determine if the content being advanced is part of a quote.
        was_in_quotation = self.is_in_quotation

        # Determine the number of lines of text which can be displayed in the dialog
        # Subtract out 1 row to leave room for the waiting indicator
        num_rows = self.get_num_rows() - 1

        if len(self.remainder_of_current_line) > 0:
            # Shift in two characters at a time remainder_of_current_line
            characters_to_advance = 3
            new_content = self.remainder_of_current_line[:characters_to_advance]
            if '"' in new_content:
                self.is_in_quotation = not self.is_in_quotation
            self.displayed_message_lines[-1] += new_content
            self.remainder_of_current_line = self.remainder_of_current_line[characters_to_advance:]
        else:
            # Shift in one row at a time from remaining_message_lines
            self.lines_since_last_acknowledgement += 1
            if len(self.displayed_message_lines) >= num_rows:
                if self.lines_since_last_acknowledgement >= num_rows:
                    return True, self.is_in_quotation
                self.displayed_message_lines = self.displayed_message_lines[1:]
            self.displayed_message_lines += ['']
            self.remainder_of_current_line = self.remaining_message_lines[0]
            self.remaining_message_lines = self.remaining_message_lines[1:]

        # Refresh image
        self.refresh_image()
        self.acknowledged = False

        return False, was_in_quotation or self.is_in_quotation

    def refresh_image(self) -> None:
        # Clear the image
        self.initialize_image()

        # Blit lines to dialog
        col_pos_x = GameDialog.outside_spacing_pixels
        row_pos_y = self.get_starting_row_pos_y()
        for lines in self.displayed_message_lines:
            self.image.blit(GameDialog.render_font(lines, self.font_color), (col_pos_x, row_pos_y))
            row_pos_y += GameDialog.font.get_height() + GameDialog.internal_spacing_pixels

        # Blit row data to dialog
        if self.row_data is not None and len(self.row_data) > 0:
            row_pos_y = self.get_row_pos_y(len(self.displayed_message_lines))
            num_cols = len(self.row_data[0])
            if self.row_data_spacing == GameDialogSpacing.OUTSIDE_JUSTIFIED and num_cols % 2 != 0:
                print('ERROR: refresh_image invoked with OUTSIDE_JUSTIFIED for odd num_cols =', num_cols, flush=True)
            first_col_pos_x = GameDialog.outside_spacing_pixels
            if self.row_data_prompt is not None:
                first_col_pos_x += GameDialog.get_font_width(self.row_data_prompt)
                self.image.blit(GameDialog.render_font(self.row_data_prompt, self.font_color),
                                (GameDialog.outside_spacing_pixels, row_pos_y))

            # Determine column widths
            col_widths = []
            for col in range(num_cols):
                col_width = 0
                for row in range(len(self.row_data)):
                    row_col_text = self.row_data[row][col]
                    if row_col_text is not None:
                        col_width = max(col_width, GameDialog.get_font_width(row_col_text))
                col_widths.append(col_width)

            for row in range(len(self.row_data)):
                col_pos_x = first_col_pos_x
                for col in range(num_cols):
                    row_col_text = self.row_data[row][col]
                    if row_col_text is None:
                        continue
                    if self.row_data_spacing == GameDialogSpacing.SPACERS:
                        col_pos_x += GameDialog.selection_indicator_pixels + 5 * GameDialog.internal_spacing_pixels
                        if col != 0:
                            col_pos_x += col_widths[col-1]
                    elif self.row_data_spacing == GameDialogSpacing.OUTSIDE_JUSTIFIED and col % 2 == 1:
                        col_pos_x = self.image.get_width() * (col + 1) // num_cols \
                                    - GameDialog.get_font_width(row_col_text) \
                                    - GameDialog.outside_spacing_pixels
                    else:
                        col_pos_x = first_col_pos_x + col * (self.image.get_width() - first_col_pos_x -
                                                             GameDialog.outside_spacing_pixels) // num_cols
                        if self.is_menu:
                            col_pos_x += GameDialog.selection_indicator_pixels + GameDialog.internal_spacing_pixels
                    self.image.blit(GameDialog.render_font(row_col_text, self.font_color), (col_pos_x, row_pos_y))
                row_pos_y += GameDialog.font.get_height() + GameDialog.internal_spacing_pixels

            col_pos_x = GameDialog.outside_spacing_pixels
            for lines in self.row_data_trailing_message_lines:
                self.image.blit(GameDialog.render_font(lines, self.font_color),
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
                index_in_options = row * num_cols + col
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
             surface: pygame.surface.Surface,
             flip_buffer: bool = False,
             offset_pixels: Point = Point(0, 0)) -> None:
        surface.blit(self.image, self.pos_tile * GameDialog.tile_size_pixels + offset_pixels)
        if flip_buffer:
            pygame.display.flip()

    def erase(self,
              surface: pygame.surface.Surface,
              background: pygame.surface.Surface,
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

    def draw_menu_indicator(self, color: Optional[pygame.Color] = None) -> None:
        if self.row_data is None or self.menu_data is None or len(self.menu_data) == 0:
            return

        if color is None:
            color = self.font_color

        first_col_pos_x = GameDialog.outside_spacing_pixels
        col_pos_x = first_col_pos_x
        if self.row_data_prompt is not None:
            first_col_pos_x += GameDialog.get_font_width(self.row_data_prompt) + GameDialog.internal_spacing_pixels
            col_pos_x = first_col_pos_x - GameDialog.internal_spacing_pixels
        num_cols = len(self.menu_data[0])
        if self.row_data_spacing == GameDialogSpacing.SPACERS:
            for col in range(self.menu_col + 1):
                col_pos_x += 4 * GameDialog.internal_spacing_pixels
                if col != 0:
                    prev_col_width = 0
                    for row in range(len(self.row_data)):
                        row_prev_col_text = self.menu_data[row][col - 1]
                        if row_prev_col_text is not None:
                            prev_col_width = max(prev_col_width, GameDialog.get_font_width(row_prev_col_text))

                    col_pos_x += prev_col_width + GameDialog.selection_indicator_pixels + \
                                 GameDialog.internal_spacing_pixels
        else:
            col_pos_x = first_col_pos_x + self.menu_col * (
                    self.image.get_width() - first_col_pos_x - GameDialog.outside_spacing_pixels) // num_cols
        row_pos_y = self.get_row_pos_y(len(self.displayed_message_lines) + self.menu_row) + (
                    GameDialog.font.get_height() - GameDialog.selection_indicator_pixels) / 2
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

    def process_event(self, event: pygame.Event, screen: pygame.surface.Surface) -> None:
        if self.allow_user_typing:
            # Process as an update to user_text
            if event.type == pygame.KEYDOWN:
                orig_user_text = self.user_text
                if pygame.K_BACKSPACE == event.key:
                    self.user_text = self.user_text[:-1]
                elif 'unicode' in event.__dict__ and 1 == len(event.unicode):
                    if self.input_allowed_characters is None or event.unicode in self.input_allowed_characters:
                        self.user_text += event.unicode

                # Refresh image if the user text has changed
                if orig_user_text != self.user_text:
                    self.displayed_message_lines[-1] = self.user_text_prompt + ' ' + self.user_text
                    self.refresh_image()
                    self.blit(screen, True)

        if self.row_data is None or self.menu_data is None:
            return

        # Process as an update to menu navigation or selection
        if event.type == pygame.KEYDOWN:
            num_cols = len(self.menu_data[0])
            last_row_num_cols = sum(x is not None for x in self.menu_data[-1])
            new_col = self.menu_col
            num_rows = len(self.menu_data)
            new_row = self.menu_row
            if event.key == pygame.K_DOWN:
                new_row = (self.menu_row + 1) % num_rows
            elif event.key == pygame.K_UP:
                if self.menu_row == 0 and self.menu_col >= last_row_num_cols:
                    new_row = (self.menu_row - 1) % (num_rows - 1)
                else:
                    new_row = (self.menu_row - 1) % num_rows
            elif event.key == pygame.K_LEFT:
                if self.menu_row == num_rows - 1:
                    new_col = (self.menu_col - 1) % last_row_num_cols
                else:
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
        self.lines_since_last_acknowledgement = 0

    def is_acknowledged(self) -> bool:
        return self.acknowledged

    @staticmethod
    def get_number_characters() -> str:
        return '7894561230'

    @staticmethod
    def get_text_characters() -> str:
        import string
        return string.ascii_uppercase + string.ascii_lowercase + '. '

    @staticmethod
    def get_all_characters() -> str:
        return '1234567890' + GameDialog.get_text_characters()

    def prompt_for_user_text(self, prompt: str = '', input_allowed_characters: Optional[str] = None) -> None:
        self.allow_user_typing = True
        self.add_message(prompt)
        self.user_text_prompt = prompt[prompt.rfind('\n')+1:]
        self.user_text = ''
        self.input_allowed_characters = input_allowed_characters

        if GameDialog.use_menus_for_text_entry():
            menu_characters = ''
            menu_cols = 0
            menu_spacing = GameDialogSpacing.EQUAL_COLUMNS
            if input_allowed_characters is not None:
                if sorted(input_allowed_characters) == sorted(GameDialog.get_number_characters()):
                    menu_characters = GameDialog.get_number_characters()
                    menu_cols = 3
                    menu_spacing = GameDialogSpacing.SPACERS
                elif sorted(input_allowed_characters) == sorted(GameDialog.get_text_characters()):
                    menu_characters = GameDialog.get_text_characters()
                    menu_cols = 14
            if 0 == len(menu_characters):
                menu_characters = GameDialog.get_all_characters()
                menu_cols = 17
            self.add_menu_prompt(list(menu_characters) + [GameDialog.BACKSPACE_UNICODE, GameDialog.ENTER_UNICODE],
                                 menu_cols,
                                 menu_spacing)

    def get_user_text(self) -> str:
        self.allow_user_typing = False
        return self.user_text

    @staticmethod
    def fix_capitalization(message: str) -> str:
        for punctuation in ['.', '!', '?']:
            sentences = []
            for sentence in message.split(punctuation):
                # Trim out any duplicated spaces between words
                words = [word for word in sentence.split(' ') if word != '']
                sentence = ' '.join(words)

                # Capitalize first letter
                if len(sentence) > 0:
                    sentence = sentence[0].upper() + sentence[1:]

                sentences.append(sentence)
            # Join the sentences back together
            message = f'{punctuation} '.join(sentences)
        return message.strip()


def main() -> None:
    # Initialize pygame
    pygame.init()
    pygame.font.init()

    # Setup the screen
    win_size_pixels = Point(1280, 960)
    tile_size_pixels = 48
    win_size_tiles = (win_size_pixels / tile_size_pixels).ceil()
    win_size_pixels = win_size_tiles * tile_size_pixels
    screen = pygame.display.set_mode(win_size_pixels.getAsIntTuple(),
                                     pygame.SRCALPHA | pygame.HWSURFACE)

    # Test out game dialog
    GameDialog.static_init(win_size_tiles, tile_size_pixels, ['lucidasans', 'arialms'])
    from pydw.hero_state import HeroState
    hero_party = HeroParty(HeroState.create_null())

    GameDialog.force_use_menus_for_text_entry = True

    def wait_for_message_to_fully_display(dialog_with_message: GameDialog) -> None:
        clock = pygame.time.Clock()
        dialog_with_message.blit(screen, True)
        while dialog_with_message.has_more_content():
            should_wait_for_acknowledgement = dialog_with_message.advance_content()[0]
            if should_wait_for_acknowledgement:
                is_waiting_indicator_drawn = False
                for i in range(0, 8):
                    if is_waiting_indicator_drawn:
                        dialog_with_message.erase_waiting_indicator()
                    else:
                        dialog_with_message.draw_waiting_indicator()
                    is_waiting_indicator_drawn = not is_waiting_indicator_drawn
                    dialog_with_message.blit(screen)
                    clock.tick(8)
                    pygame.display.flip()
                dialog_with_message.acknowledge()
            else:
                dialog_with_message.blit(screen)
                clock.tick(30)
                pygame.display.flip()

    def wait_for_menu_selection(dialog_with_menu: GameDialog) -> None:
        is_awaiting_selection = True
        dialog_with_menu.blit(screen, True)
        while is_awaiting_selection:
            events = GameEvents.get_events()
            if 0 == len(events):
                pygame.time.wait(25)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    elif event.key == pygame.K_RETURN:
                        is_awaiting_selection = False
                        print('Selection made =', dialog_with_menu.get_selected_menu_option(), flush=True)
                    else:
                        dialog_with_menu.process_event(event, screen)
                elif event.type == pygame.QUIT:
                    pygame.quit()

    def wait_for_user_input(dialog_with_user_input: GameDialog) -> None:
        is_waiting_for_user_input = True
        wait_for_message_to_fully_display(dialog_with_user_input)
        while is_waiting_for_user_input:
            events = GameEvents.get_events()
            if 0 == len(events):
                pygame.time.wait(25)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    elif event.key == pygame.K_RETURN:
                        if GameDialog.use_menus_for_text_entry():
                            # Get a menu selection and turn that into an event
                            menu_result = dialog_with_user_input.get_selected_menu_option()
                            if menu_result == GameDialog.ENTER_UNICODE:
                                is_waiting_for_user_input = False
                                print('Selection made =', dialog_with_user_input.get_user_text(), flush=True)
                            elif menu_result == GameDialog.BACKSPACE_UNICODE:
                                event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_BACKSPACE})
                            else:
                                event = pygame.event.Event(pygame.KEYDOWN, {'key': None, 'unicode': menu_result})

                            if is_waiting_for_user_input:
                                message_dialog.process_event(event, screen)
                        else:
                            is_waiting_for_user_input = False
                            print('Selection made =', dialog_with_user_input.get_user_text(), flush=True)
                    else:
                        dialog_with_user_input.process_event(event, screen)
                elif event.type == pygame.QUIT:
                    pygame.quit()

    screen.fill('pink')
    GameDialog.create_exploring_status_dialog(hero_party).blit(screen, False)
    message_dialog = GameDialog.create_message_dialog('Hail!')
    message_dialog.add_message('Shift=' + GameDialog.SHIFT_UNICODE)
    message_dialog.add_message('Capslock=' + GameDialog.CAPSLOCK_UNICODE)
    message_dialog.add_message('Backspace=' + GameDialog.BACKSPACE_UNICODE)
    message_dialog.add_message('Enter=' + GameDialog.ENTER_UNICODE)
    wait_for_message_to_fully_display(message_dialog)

    wait_for_menu_selection(GameDialog.create_exploring_menu())

    wait_for_menu_selection(GameDialog.create_menu_dialog(
        Point(-1, 1),
        None,
        'OPTIONS',
        [f'Option {n}' for n in range(0, 100)],
        2))

    screen.fill('pink')
    GameDialog.create_encounter_status_dialog(hero_party).blit(screen, False)
    wait_for_message_to_fully_display(GameDialog.create_message_dialog(
        'word wrap testing...  Word wrap testing...  word wrap testing...  ' +
        'Word Wrap testing...  word Wrap testing...  Word Wrap testing...'))
    wait_for_menu_selection(GameDialog.create_encounter_menu())

    screen.fill('pink')
    GameDialog.create_encounter_status_dialog(hero_party).blit(screen, False)
    message_dialog = GameDialog.create_message_dialog(
        'Hail 1!\nHail 2!\nHail 3!\nHail 4!\nHail 5!\nHail 6!\nHail 7!\nHail 8!\nHail 9!\nHail 10!\nHail 11!')
    wait_for_message_to_fully_display(message_dialog)

    message_dialog.add_menu_prompt(['Yes', 'No'], 2, GameDialogSpacing.SPACERS)
    GameDialog.set_default_font_color(GameDialog.LOW_HEALTH_FONT_COLOR)
    GameDialog.create_encounter_status_dialog(hero_party).blit(screen, False)
    message_dialog.set_font_color(GameDialog.LOW_HEALTH_FONT_COLOR)
    GameDialog.create_encounter_status_dialog(hero_party).blit(screen, False)
    wait_for_menu_selection(message_dialog)
    message_dialog.add_message('\nLexie attacks!')
    wait_for_message_to_fully_display(message_dialog)

    message_dialog.prompt_for_user_text('\n1 + 15 =', GameDialog.get_number_characters())
    wait_for_user_input(message_dialog)

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
