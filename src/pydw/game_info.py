#!/usr/bin/env python

from typing import Dict, List, Optional, Tuple, Union

import concurrent.futures
import os
import numpy
import sys
# xml.etree doesn't support nested xincludes prior to Python 3.9 (see https://github.com/python/cpython/issues/65127)
# Prior to Python 3.9, use lxml.etree
if sys.version_info[0] == 3 and sys.version_info[1] < 9:
    from typing import Callable
    import lxml.etree as ET
    import lxml.ElementInclude as ETI

    # lxml.etree._Element is not natively pickleable
    # See https://stackoverflow.com/questions/25991860/unable-to-pass-an-lxml-etree-object-to-a-separate-process/25994232#25994232
    def element_unpickler(data: str) -> ET._Element:
        return ET.fromstring(data)

    def element_pickler(element: ET._Element) -> Tuple[Callable[[str], ET._Element], Tuple[str]]:
        data = ET.tostring(element)
        return element_unpickler, (data,git )

    import copyreg
    copyreg.pickle(ET._Element, element_pickler)
else:
    import xml.etree.ElementTree as ET
    import xml.etree.ElementInclude as ETI

import pygame

from generic_utils.point import Point

from pygame_utils.audio_player import AudioPlayer, MusicTrack, SoundTrack

from pydw.game_dialog import GameDialog
from pydw.game_types import ActionCategoryTypeEnum, AnyTransition, Armor, CharacterType, Decoration, DialogAction, \
    DialogActionEnum, DialogCheck, DialogCheckEnum, DialogGoTo, DialogType, DialogVariable, DialogVendorBuyOptions, \
    DialogVendorBuyOptionsParamWithoutReplacementType,  DialogVendorBuyOptionsParamType, \
    DialogVendorBuyOptionsVariable, DialogVendorSellOptions, DialogVendorSellOptionsParamWithoutReplacementType, \
    DialogVendorSellOptionsParamType, DialogVendorSellOptionsVariable, Direction, EncounterBackground, GameTypes, \
    IncomingTransition, ItemType, Level, Map, MapDecoration, MonsterAction, MonsterActionRule, MonsterInfo, \
    MonsterInfoPicklable, MonsterZone, NamedLocation, NpcInfo, OutgoingTransition, Shield, SpecialMonster, Spell, \
    SurfacePickable, TargetTypeEnum, Tile, Tool, Weapon


class GameInfo:
    TRANSPARENT_COLOR = pygame.Color(0, 0, 0, 0)

    def __init__(self,
                 base_path: str,
                 game_xml_path: str,
                 tile_size_pixels: int,
                 win_size_pixels: Point) -> None:

        self.game_xml_path = game_xml_path
        self.tile_size_pixels = tile_size_pixels
        self.dialog_sequences: Dict[str, DialogType] = {}
        self.map_being_parsed: Optional[str] = None

        # Find image_px_step_size.  Select step size nearest to 1/6 of a tile which yields a value where
        # tile_size_pixels is divisible by image_px_step_size.
        desired_tile_move_steps = 6
        self.image_px_step_size = 1
        for possible_step_size in range(2, self.tile_size_pixels):
            if self.tile_size_pixels % possible_step_size == 0:
                if abs(self.tile_size_pixels / possible_step_size - desired_tile_move_steps) < \
                        abs(self.tile_size_pixels / self.image_px_step_size - desired_tile_move_steps):
                    self.image_px_step_size = possible_step_size
                else:
                    break

        # Parse XML
        xml_root = ET.parse(game_xml_path).getroot()
        ETI.include(xml_root)
        data_path = os.path.join(base_path, xml_root.attrib['dataPath'])
        image_path = os.path.join(data_path, xml_root.attrib['imagePath'])

        GameInfo.init_audio_player(xml_root, data_path)

        # Parse the encounter background images
        self.encounter_backgrounds = GameInfo.parse_encounter_backgrounds(xml_root, image_path)

        # Parse map locations - self.locations is a dictionary of Map name -> Location name -> NamedLocation
        self.locations = GameInfo.parse_map_locations(xml_root)

        # Parse items
        # TODO: Combine all of these into an items type?
        self.items: Dict[str, ItemType] = {}
        self.weapons, self.default_weapon = self.parse_weapons(xml_root)
        self.armors = GameInfo.parse_armors(xml_root, self.items)
        self.shields = GameInfo.parse_shields(xml_root, self.items)
        self.tools = self.parse_tools(xml_root)

        # Parse tiles
        # TODO: Combine all of these into an tiles type?
        self.tiles, self.tile_symbols, self.tile_probabilities = \
            GameInfo.parse_tiles(xml_root, image_path, self.tile_size_pixels)

        # Parse decorations
        self.decorations = GameInfo.parse_decoration(xml_root, image_path, self.tile_size_pixels)

        # Parse spells
        self.spells = self.parse_spells(xml_root)

        # Parse characters
        self.character_types = GameInfo.parse_character_types(xml_root, image_path, self.spells, self.tile_size_pixels)

        # Parse monsters
        self.monsters = self.parse_monsters(xml_root, image_path, int(win_size_pixels.y))

        # Parse monster sets
        self.monster_sets = GameInfo.parse_monster_sets(xml_root)

        # Parse maps
        self.maps = self.parse_maps(xml_root, os.path.join(data_path, xml_root.attrib['mapsPath']))

        # Parse dialog scripts
        for element in xml_root.findall("./DialogScripts/DialogScript"):
            dialog_script = self.parse_dialog(element)
            if dialog_script is not None:
                self.dialog_sequences[element.attrib['label']] = dialog_script

        # Parse death state
        death_state_element = xml_root.find('DeathState')
        if death_state_element is None:
            print('ERROR: DeathState element is missing', flush=True)
            raise Exception('Missing required DeathState element')
        self.death_map = death_state_element.attrib['map']
        self.death_hero_pos_dat_tile = self.get_location(self.death_map, death_state_element)
        self.death_hero_pos_dir = self.get_direction(self.death_map, death_state_element)
        self.death_dialog = self.parse_dialog(death_state_element)

    @staticmethod
    def static_init(base_path: str, game_xml_path: str, win_size_tiles: Point, tile_size_pixels: int) \
            -> Tuple[pygame.surface.Surface, str]:
        xml_root = ET.parse(game_xml_path).getroot()
        ETI.include(xml_root)

        data_path = os.path.join(base_path, xml_root.attrib['dataPath'])
        GameInfo.init_audio_player(xml_root, data_path)

        image_path = os.path.join(data_path, xml_root.attrib['imagePath'])
        font_names, dialog_border_image_filename = GameInfo.parse_dialogs_info(xml_root, image_path)
        GameDialog.static_init(win_size_tiles,
                               tile_size_pixels,
                               font_names,
                               dialog_border_image_filename)

        image_path = os.path.join(data_path, xml_root.attrib['imagePath'])
        return GameInfo.parse_title_info(xml_root, image_path)

    @staticmethod
    def init_audio_player(xml_root: ET.Element, data_path: str) -> None:
        audio_player = AudioPlayer()
        if 0 == len(audio_player.get_music_tracks()) and 0 == len(audio_player.get_sound_tracks()):
            # On the first initialization pass, just add the tracks
            GameInfo.init_audio_player_music(xml_root, data_path)
            GameInfo.init_audio_player_sounds(xml_root, data_path)
        else:
            # Stage all the tracks on the second go around
            audio_player.stage_all_tracks()

    @staticmethod
    def init_audio_player_music(xml_root: ET.Element, data_path: str) -> None:
        music_path = os.path.join(data_path, xml_root.attrib['musicPath'])

        # Set the audio player music path
        audio_player = AudioPlayer()
        audio_player.set_music_path(music_path)

        # Parse music mappings and add to the audio player
        for element in xml_root.findall("./MusicMappings"):
            name_to_music_track_mapping: Dict[str, MusicTrack] = {}

            base_path = music_path
            if 'path' in element.attrib:
                base_path = os.path.join(base_path, element.attrib['path'])
            try:
                if not os.path.exists(base_path):
                    os.mkdir(base_path)
            except Exception:
                print('ERROR: Failed to create directory', base_path)

            package_name: Optional[str] = None
            if 'name' in element.attrib:
                package_name = os.path.join(base_path, element.attrib['name'])
            package_link: Optional[str] = None
            if 'link' in element.attrib:
                package_link = element.attrib['link']

            for track_element in element.findall("./Track"):
                name = track_element.attrib['name']
                source = os.path.join(base_path, track_element.attrib['source'])
                source2: Optional[str] = None
                if 'source2' in track_element.attrib:
                    source2 = os.path.join(base_path, track_element.attrib['source2'])
                link: Optional[str] = None
                if 'link' in track_element.attrib:
                    link = track_element.attrib['link']
                link2: Optional[str] = None
                if 'link2' in track_element.attrib:
                    link2 = track_element.attrib['link2']
                start_play1_sec = 0.0
                if 'startPlay1' in track_element.attrib:
                    start_play1_sec = float(track_element.attrib['startPlay1'])
                start_play2_sec = 0.0
                if 'startPlay2' in track_element.attrib:
                    start_play2_sec = float(track_element.attrib['startPlay2'])

                name_to_music_track_mapping[name] = MusicTrack(name,
                                                               source,
                                                               source2,
                                                               link,
                                                               link2,
                                                               start_play1_sec,
                                                               start_play2_sec,
                                                               track_element.attrib['credits'],
                                                               package_name,
                                                               package_link)

            audio_player.add_music_tracks(name_to_music_track_mapping)

    @staticmethod
    def init_audio_player_sounds(xml_root: ET.Element, data_path: str) -> None:
        sound_path = os.path.join(data_path, xml_root.attrib['soundPath'])

        # Set the audio player sound path
        audio_player = AudioPlayer()
        audio_player.set_sound_path(sound_path)

        # Parse sound mappings and add to the audio player
        for element in xml_root.findall("./SoundMappings"):
            name_to_sound_track_mapping: Dict[str, SoundTrack] = {}

            base_path = sound_path
            if 'path' in element.attrib:
                base_path = os.path.join(base_path, element.attrib['path'])
            try:
                if not os.path.exists(base_path):
                    os.mkdir(base_path)
            except Exception:
                print('ERROR: Failed to create directory', base_path)

            package_name: Optional[str] = None
            if 'name' in element.attrib:
                package_name = os.path.join(base_path, element.attrib['name'])
            package_link: Optional[str] = None
            if 'link' in element.attrib:
                package_link = element.attrib['link']

            for track_element in element.findall("./Track"):
                name = track_element.attrib['name']
                source = os.path.join(base_path, track_element.attrib['source'])
                link: Optional[str] = None
                if 'link' in track_element.attrib:
                    link = track_element.attrib['link']

                name_to_sound_track_mapping[name] = SoundTrack(name,
                                                               source,
                                                               link,
                                                               track_element.attrib['credits'],
                                                               package_name,
                                                               package_link)

            audio_player.add_sound_tracks(name_to_sound_track_mapping)

    @staticmethod
    def parse_title_info(xml_root: ET.Element, image_path: str) -> Tuple[pygame.surface.Surface, str]:
        title_element = xml_root.find('Title')
        if title_element is not None:
            title_music = title_element.attrib['music']
            title_image_file_name = os.path.join(image_path, title_element.attrib['image'])
            title_image = pygame.image.load(title_image_file_name).convert()

        return title_image, title_music

    @staticmethod
    def parse_dialogs_info(xml_root: ET.Element, image_path: str) -> Tuple[List[str], Optional[str]]:
        font_names: List[str] = []
        dialogs_element = xml_root.find('Dialogs')
        if dialogs_element is not None:
            for element in dialogs_element.findall(".//Font"):
                font_names.append(element.attrib['name'])
            dialog_border_image_filename = None
            if 'image' in dialogs_element.attrib:
                dialog_border_image_filename = os.path.join(image_path, dialogs_element.attrib['image'])
        return font_names, dialog_border_image_filename

    @staticmethod
    def parse_encounter_backgrounds(xml_root: ET.Element, image_path: str) -> Dict[str, EncounterBackground]:
        encounter_path = os.path.join(image_path, xml_root.attrib['encounterPath'])
        encounter_backgrounds: Dict[str, EncounterBackground] = {}
        for mappings_element in xml_root.findall("./EncounterBackgroundMappings"):
            element_encounter_path = os.path.join(encounter_path, mappings_element.attrib['path'])
            for image_element in mappings_element.findall("./Image"):
                encounter_background_name = image_element.attrib['name']
                if encounter_background_name in encounter_backgrounds:
                    # Favor the first image added
                    continue
                image_path = os.path.join(element_encounter_path, image_element.attrib['source'])

                # print('Loading', encounter_background_name, flush=True)
                try:
                    encounter_background_image = pygame.image.load(image_path)
                    encounter_backgrounds[encounter_background_name] = EncounterBackground(
                        encounter_background_name,
                        encounter_background_image,
                        image_path,
                        image_element.attrib['artist'] if 'artist' in image_element.attrib else 'Uncredited',
                        image_element.attrib['artist_url'] if 'artist_url' in image_element.attrib else None,
                        image_element.attrib['url'] if 'url' in image_element.attrib else None)
                except Exception:
                    print('ERROR: Failed to load', encounter_background_name, flush=True)
        return encounter_backgrounds

    @staticmethod
    def parse_map_locations(xml_root: ET.Element) -> Dict[str, Dict[str, NamedLocation]]:
        locations: Dict[str, Dict[str, NamedLocation]] = {}  # Map name -> Location name -> NamedLocation
        for element in xml_root.findall("./Maps//Map"):
            map_name = element.attrib['name']
            map_locations: Dict[str, NamedLocation] = {}
            for location_element in element.findall('MapLocation'):
                location_name = location_element.attrib['name']
                direction = None
                if 'dir' in location_element.attrib:
                    direction = Direction[location_element.attrib['dir']]
                map_locations[location_name] = NamedLocation(location_name,
                                                             Point(int(location_element.attrib['x']),
                                                                   int(location_element.attrib['y'])),
                                                             direction)
            locations[map_name] = map_locations
        return locations

    def parse_weapons(self, xml_root: ET.Element) -> Tuple[Dict[str, Weapon], Weapon]:
        weapons: Dict[str, Weapon] = {}
        for element in xml_root.findall("./Items/Weapons/Weapon"):
            item_name = element.attrib['name']
            use_dialog = self.parse_dialog(element)
            if use_dialog is None:
                print('ERROR: No use dialog for weapon', item_name, flush=True)
                continue
            target_type = TargetTypeEnum.SINGLE_ENEMY
            if 'target' in element.attrib:
                target_type = TargetTypeEnum[element.attrib['target']]
            weapons[item_name] = Weapon(
                item_name,
                int(element.attrib['attackBonus']),
                int(element.attrib['gp']),
                target_type,
                use_dialog)
            self.items[item_name] = weapons[item_name]

        # Get default weapon
        weapons_element = xml_root.find('Weapon')
        if weapons_element is not None and 'default' in weapons_element.attrib:
            default_weapon = weapons[weapons_element.attrib['default']]
        else:
            default_weapon = next(iter(weapons.values()))
        # The default weapon isn't actually an item so remove it from the weapon and item lists
        del weapons[default_weapon.name]
        del self.items[default_weapon.name]

        return weapons, default_weapon

    @staticmethod
    def parse_armors(xml_root: ET.Element, items: Dict[str, ItemType]) -> Dict[str, Armor]:
        armors: Dict[str, Armor] = {}
        for element in xml_root.findall("./Items/Armors/Armor"):
            item_name = element.attrib['name']

            hp_regen_tiles = None
            if 'hpRegenTiles' in element.attrib and 'none' != element.attrib['hpRegenTiles']:
                hp_regen_tiles = int(element.attrib['hpRegenTiles'])

            armors[item_name] = Armor(
                item_name,
                int(element.attrib['defenseBonus']),
                int(element.attrib['gp']),
                element.attrib['ignoresTilePenalties'] == 'yes',
                float(element.attrib['hurtDmgModifier']),
                float(element.attrib['fireDmgModifier']),
                float(element.attrib['stopspellResistance']),
                hp_regen_tiles)
            items[item_name] = armors[item_name]
        return armors

    @staticmethod
    def parse_shields(xml_root: ET.Element, items: Dict[str, ItemType]) -> Dict[str, Shield]:
        shields: Dict[str, Shield] = {}
        for element in xml_root.findall("./Items/Shields/Shield"):
            item_name = element.attrib['name']
            shields[item_name] = Shield(
                item_name,
                int(element.attrib['defenseBonus']),
                int(element.attrib['gp']))
            items[item_name] = shields[item_name]
        return shields

    def parse_tools(self, xml_root: ET.Element) -> Dict[str, Tool]:
        tools: Dict[str, Tool] = {}
        for element in xml_root.findall("./Items/Tools/Tool"):
            item_name = element.attrib['name']
            attack_bonus = 0
            defense_bonus = 0
            gp = 0
            if 'attackBonus' in element.attrib:
                attack_bonus = int(element.attrib['attackBonus'])
            if 'defenseBonus' in element.attrib:
                defense_bonus = int(element.attrib['defenseBonus'])
            if 'gp' in element.attrib:
                gp = int(element.attrib['gp'])
            target_type = TargetTypeEnum.SELF
            if 'target' in element.attrib:
                target_type = TargetTypeEnum[element.attrib['target']]

            tools[item_name] = Tool(
                item_name,
                attack_bonus,
                defense_bonus,
                gp,
                element.attrib['droppable'] == 'yes',
                element.attrib['equippable'] == 'yes',
                self.parse_dialog(element),
                target_type)
            self.items[item_name] = tools[item_name]
        return tools

    @staticmethod
    def parse_tiles(xml_root: ET.Element, image_path: str, tile_size_pixels: int) -> \
            Tuple[Dict[str, Tile], Dict[str, str], List[List[float]]]:
        tiles: Dict[str, Tile] = {}
        tile_symbols: Dict[str, str] = {}  # tile symbol to tile name map
        tile_probabilities: List[List[float]] = [[1.0]]

        element = xml_root.find('Tiles')
        if element is None:
            print('ERROR: Failed to parse any tiles', flush=True)
            return tiles, tile_symbols, tile_probabilities
        if 'imagePath' in element.attrib:
            tile_path = os.path.join(image_path, element.attrib['imagePath'])
        else:
            tile_path = image_path

        max_tile_variants = 1
        for element in xml_root.findall("./Tiles/Tile"):
            tile_name = element.attrib['name']
            tile_symbol = ''
            tile_image_file_name = ''
            tile_walkable = True
            can_talk_over = False
            hp_penalty = 0
            mp_penalty = 0
            speed = 1.0
            spawn_rate = 1.0
            tile_type = 'simple'
            if 'symbol' in element.attrib:
                tile_symbol = element.attrib['symbol']
            if 'image' in element.attrib and tile_path is not None:
                tile_image_file_name = os.path.join(tile_path, element.attrib['image'])
            else:
                tile_type = 'tiled'
            if 'walkable' in element.attrib:
                tile_walkable = element.attrib['walkable'] == 'yes'
            if 'canTalkOver' in element.attrib:
                can_talk_over = element.attrib['canTalkOver'] == 'yes'
            if 'hpPenalty' in element.attrib:
                hp_penalty = int(element.attrib['hpPenalty'])
            if 'mpPenalty' in element.attrib:
                mp_penalty = int(element.attrib['mpPenalty'])
            if 'speed' in element.attrib:
                speed = GameTypes.parse_float(element.attrib['speed'])
            if 'spawnRate' in element.attrib:
                spawn_rate = GameTypes.parse_float(element.attrib['spawnRate'])
            if 'type' in element.attrib:
                tile_type = element.attrib['type']

            # Load the tile image for tile types which are not exclusive to tiled maps
            tile_images_scaled: List[List[pygame.surface.Surface]] = []
            if tile_type != 'tiled':
                # print('Loading image', tileImageFileName, flush=True)
                tile_image_unscaled = pygame.image.load(tile_image_file_name).convert()

                if tile_type == 'complex':
                    image_index_translation = [[9, 8, 12, 13], [1, 0, 4, 5], [3, 2, 6, 7], [11, 10, 14, 15]]
                    for x in range(16):
                        tile_images_scaled.append([])
                    unscaled_size = tile_image_unscaled.get_height() / 4
                    tile_variants = tile_image_unscaled.get_width() // tile_image_unscaled.get_height()
                    max_tile_variants = max(max_tile_variants, tile_variants)
                    for y in range(4):
                        for x in range(4):
                            for z in range(tile_variants):
                                temp_surface = pygame.surface.Surface((tile_size_pixels, tile_size_pixels))
                                pygame.transform.scale(tile_image_unscaled.subsurface(
                                    pygame.Rect(x * unscaled_size + z * tile_image_unscaled.get_height(),
                                                y * unscaled_size, unscaled_size, unscaled_size)),
                                    (tile_size_pixels, tile_size_pixels),
                                    temp_surface)
                                tile_images_scaled[image_index_translation[y][x]].append(temp_surface)
                elif tile_type == 'simple':
                    tile_variants = tile_image_unscaled.get_width() // tile_image_unscaled.get_height()
                    max_tile_variants = max(max_tile_variants, tile_variants)
                    temp_surface_list: List[pygame.surface.Surface] = []
                    for z in range(tile_variants):
                        temp_surface_list.append(pygame.surface.Surface((tile_size_pixels, tile_size_pixels)))
                        pygame.transform.scale(tile_image_unscaled.subsurface(
                            pygame.Rect(z * tile_image_unscaled.get_height(),
                                        0,
                                        tile_image_unscaled.get_height(),
                                        tile_image_unscaled.get_height())),
                            (tile_size_pixels, tile_size_pixels),
                            temp_surface_list[-1])
                    tile_images_scaled = [temp_surface_list] * 16

            if len(tile_symbol) == 1:
                tile_symbols[tile_symbol] = tile_name
            tiles[tile_name] = Tile(tile_name,
                                    tile_symbol,
                                    tile_images_scaled,
                                    tile_walkable,
                                    can_talk_over,
                                    hp_penalty,
                                    mp_penalty,
                                    speed,
                                    spawn_rate)

        for x in range(2, max_tile_variants + 1):
            w = numpy.arange(x, 0, -1)
            w = w * numpy.transpose(w)
            w = w * numpy.transpose(w)
            p = w / sum(w)
            tile_probabilities.append([float(x) for x in p])

        return tiles, tile_symbols, tile_probabilities

    @staticmethod
    def parse_decoration(xml_root: ET.Element, image_path: str, tile_size_pixels: int) -> Dict[str, Decoration]:
        decorations: Dict[str, Decoration] = {}

        element = xml_root.find('Decorations')
        if element is None:
            print('ERROR: Failed to parse any decorations', flush=True)
            return decorations
        if 'imagePath' in element.attrib:
            decoration_path = os.path.join(image_path, element.attrib['imagePath'])
        else:
            decoration_path = image_path

        def load_decoration_image(image_filename: str) -> pygame.surface.Surface:
            decoration_image_filename = os.path.join(decoration_path, image_filename)
            # print('Loading image', decoration_image_filename, flush=True)
            image_unscaled = pygame.image.load(decoration_image_filename).convert_alpha()
            unscaled_size_pixels = Point(image_unscaled.get_size())
            max_scaled_size_pixels = Point(width_tiles, height_tiles) * tile_size_pixels
            scale_factor_point = (max_scaled_size_pixels / unscaled_size_pixels)
            scale_factor = max(scale_factor_point.w, scale_factor_point.h)
            scaled_size_pixels = (unscaled_size_pixels * scale_factor).floor()
            image_scaled = pygame.surface.Surface(scaled_size_pixels, flags=pygame.SRCALPHA)
            pygame.transform.scale(image_unscaled,
                                   scaled_size_pixels.get_as_int_tuple(),
                                   image_scaled)
            return image_scaled

        for element in xml_root.findall("./Decorations//Decoration"):
            decoration_name = element.attrib['name']
            width_tiles = 1
            height_tiles = 1
            walkable = None
            remove_with_search = False
            remove_with_open = False
            remove_with_key = False
            remove_sound = None
            can_talk_over = None
            if 'widthTiles' in element.attrib:
                width_tiles = int(element.attrib['widthTiles'])
            if 'heightTiles' in element.attrib:
                height_tiles = int(element.attrib['heightTiles'])
            if 'walkable' in element.attrib:
                if element.attrib['walkable'] == 'yes':
                    walkable = True
                elif element.attrib['walkable'] == 'no':
                    walkable = False
            if 'removeWithSearch' in element.attrib:
                remove_with_search = element.attrib['removeWithSearch'] == 'yes'
            if 'removeWithOpen' in element.attrib:
                remove_with_open = element.attrib['removeWithOpen'] == 'yes'
            if 'removeWithKey' in element.attrib:
                remove_with_key = element.attrib['removeWithKey'] == 'yes'
            if 'removeSound' in element.attrib:
                remove_sound = element.attrib['removeSound']
            if 'canTalkOver' in element.attrib:
                if element.attrib['canTalkOver'] == 'yes':
                    can_talk_over = True
                elif element.attrib['canTalkOver'] == 'no':
                    can_talk_over = False
            decoration_image_scaled = load_decoration_image(element.attrib['image'])
            decoration_removed_image_scaled: Optional[pygame.surface.Surface] = None
            if 'removed_image' in element.attrib:
                decoration_removed_image_scaled = load_decoration_image(element.attrib['removed_image'])

            decorations[decoration_name] = Decoration(decoration_name,
                                                      width_tiles,
                                                      height_tiles,
                                                      decoration_image_scaled,
                                                      walkable,
                                                      remove_with_search,
                                                      remove_with_open,
                                                      remove_with_key,
                                                      remove_sound,
                                                      decoration_removed_image_scaled,
                                                      can_talk_over)
        return decorations

    def parse_spells(self, xml_root: ET.Element) -> Dict[str, Spell]:
        spells: Dict[str, Spell] = {}
        for element in xml_root.findall("./Spells/Spell"):
            name = element.attrib['name']
            available_in_combat = True
            available_outside_combat = True
            available_inside = True
            available_outside = True
            target_type = TargetTypeEnum.SELF
            if 'availableInCombat' in element.attrib:
                available_in_combat = element.attrib['availableInCombat'] == 'yes'
            if 'availableOutsideCombat' in element.attrib:
                available_outside_combat = element.attrib['availableOutsideCombat'] == 'yes'
            if 'availableInside' in element.attrib:
                available_inside = element.attrib['availableInside'] == 'yes'
            if 'availableOutside' in element.attrib:
                available_outside = element.attrib['availableOutside'] == 'yes'
            if 'target' in element.attrib:
                target_type = TargetTypeEnum[element.attrib['target']]
            use_dialog = self.parse_dialog(element)
            if use_dialog is None:
                print('ERROR: No use dialog for spell', name, flush=True)
                continue

            spells[name] = Spell(
                name,
                int(element.attrib['mp']),
                available_in_combat,
                available_outside_combat,
                available_inside,
                available_outside,
                target_type,
                use_dialog)
        return spells

    @staticmethod
    def parse_levels(xml_root: ET.Element, spells: Dict[str, Spell]) -> Dict[str, List[Level]]:
        levels: Dict[str, List[Level]] = {}
        for element in xml_root.findall("./Levels//CharacterLevels"):
            character_type = element.attrib['type']
            levels[character_type] = []
            for level_element in element.findall("./Level"):
                level_name = level_element.attrib['name']
                level_number = len(levels[character_type])
                level_spell = None
                if 'spell' in level_element.attrib and level_element.attrib['spell'] in spells:
                    level_spell = spells[level_element.attrib['spell']]
                level = Level(
                    level_number,
                    level_name,
                    int(level_element.attrib['xp']),
                    int(level_element.attrib['strength']),
                    int(level_element.attrib['agility']),
                    int(level_element.attrib['hp']),
                    int(level_element.attrib['mp']),
                    level_spell)
                levels[character_type].append(level)
        return levels

    @staticmethod
    def parse_character_types(xml_root: ET.Element, image_path: str, spells: Dict[str, Spell], tile_size_pixels: int) \
            -> Dict[str, CharacterType]:
        character_path = os.path.join(image_path, xml_root.attrib['characterPath'])
        levels = GameInfo.parse_levels(xml_root, spells)
        character_types: Dict[str, CharacterType] = {}
        for element in xml_root.findall("./CharacterTypes//CharacterType"):
            character_type = element.attrib['type']
            character_levels: List[Level] = []
            if 'levels' in element.attrib and element.attrib['levels'] in levels:
                character_levels = levels[element.attrib['levels']]
            num_phases = 2
            if 'phases' in element.attrib:
                num_phases = int(element.attrib['phases'])
            movement_speed_factor = 1.0
            if 'speed' in element.attrib:
                movement_speed_factor = float(element.attrib['speed'])
            ticks_per_step = 30
            if 'frames_per_step' in element.attrib:
                ticks_per_step = int(element.attrib['frames_per_step'])
            ticks_between_npc_moves = 60
            if 'frames_between_moves' in element.attrib:
                ticks_between_npc_moves = int(element.attrib['frames_between_moves'])
            character_type_filename = os.path.join(character_path, element.attrib['image'])
            # print('Loading image', character_type_filename, flush=True)
            try:
                character_type_image = pygame.image.load(character_type_filename).convert_alpha()
            except FileNotFoundError:
                print('ERROR: Failed to load file', character_type_filename, flush=True)
                continue
            character_type_images = {}
            if character_type_image.get_width() == character_type_image.get_height() * 8 + 7:
                # Support for old style character images
                x_px = 0
                for direction in [Direction.SOUTH, Direction.EAST, Direction.NORTH, Direction.WEST]:
                    direction_character_type_images = {}
                    for phase in range(num_phases):
                        image = pygame.surface.Surface((tile_size_pixels, tile_size_pixels),
                                                       flags=pygame.SRCALPHA)
                        pygame.transform.scale(character_type_image.subsurface(x_px,
                                                                               0,
                                                                               character_type_image.get_height(),
                                                                               character_type_image.get_height()),
                                               (tile_size_pixels, tile_size_pixels),
                                               image)
                        direction_character_type_images[phase] = image
                        x_px += character_type_image.get_height() + 1
                    character_type_images[direction] = direction_character_type_images
            else:
                phase_image_size = Point(character_type_image.get_width() // num_phases,
                                         character_type_image.get_height() // 4)
                scale_factor = tile_size_pixels / max(phase_image_size.w, phase_image_size.h)
                phase_image_scaled_size = Point(int(scale_factor * phase_image_size.w),
                                                int(scale_factor * phase_image_size.h))
                dest_image_rect = pygame.Rect((tile_size_pixels - phase_image_scaled_size.w) // 2,
                                              (tile_size_pixels - phase_image_scaled_size.h) // 2,
                                              phase_image_scaled_size.w,
                                              phase_image_scaled_size.h)
                for (idx, direction) in enumerate([Direction.SOUTH, Direction.WEST, Direction.EAST, Direction.NORTH]):
                    y_px = idx * phase_image_size.h
                    direction_character_type_images = {}
                    for phase in range(num_phases):
                        x_px = phase * int(phase_image_size.w)
                        image = pygame.surface.Surface((tile_size_pixels, tile_size_pixels),
                                                       flags=pygame.SRCALPHA)
                        pygame.transform.scale(character_type_image.subsurface(x_px,
                                                                               y_px,
                                                                               phase_image_size.w,
                                                                               phase_image_size.h),
                                               phase_image_scaled_size.get_as_int_tuple(),
                                               image.subsurface(dest_image_rect))
                        direction_character_type_images[phase] = image
                    character_type_images[direction] = direction_character_type_images

            new_char = CharacterType(name=character_type,
                                     images=character_type_images,
                                     levels=character_levels,
                                     num_phases=num_phases,
                                     movement_speed_factor=movement_speed_factor,
                                     ticks_per_step=ticks_per_step,
                                     ticks_between_npc_moves=ticks_between_npc_moves)

            character_types[character_type] = new_char
        return character_types

    def parse_monster_actions(self, xml_root: ET.Element) -> Tuple[Dict[str, MonsterAction], MonsterAction]:
        # Parse monster actions
        monster_actions: Dict[str, MonsterAction] = {}
        for element in xml_root.findall("./MonsterActions/MonsterAction"):
            action_name = element.attrib['name']
            spell = None
            target_type = TargetTypeEnum.SINGLE_ENEMY
            if 'spell' in element.attrib and element.attrib['spell'] in self.spells:
                spell = self.spells[element.attrib['spell']]
                target_type = spell.target_type
                use_dialog: Optional[DialogType] = spell.use_dialog
            else:
                if 'target' in element.attrib:
                    target_type = TargetTypeEnum[element.attrib['target']]
                use_dialog = self.parse_dialog(element)
            if target_type is None:
                print('ERROR: No target type for monster action', action_name, flush=True)
                continue
            if use_dialog is None:
                print('ERROR: No use dialog for monster action', action_name, flush=True)
                continue
            monster_actions[action_name] = MonsterAction(action_name,
                                                         spell,
                                                         target_type,
                                                         use_dialog)

        # Get default monster action
        monster_actions_element = xml_root.find('MonsterActions')
        if monster_actions_element is not None and 'default' in monster_actions_element.attrib:
            default_monster_action = monster_actions[monster_actions_element.attrib['default']]
        else:
            default_monster_action = next(iter(monster_actions.values()))

        return monster_actions, default_monster_action

    def parse_monsters(self, xml_root: ET.Element, image_path: str, window_height: int) -> Dict[str, MonsterInfo]:
        monster_path = os.path.join(image_path, xml_root.attrib['monsterPath'])

        # Parse monster actions
        monster_actions, default_monster_action = self.parse_monster_actions(xml_root)

        # Scale monster images up assuming they are scaled to a Nintendo resolution of 240 vertical pixels
        monster_scale_factor = window_height / 240

        # import time
        # print('Starting to load monsters...', flush=True)
        # start_time = time.time()
        monsters: Dict[str, MonsterInfo] = {}
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = {executor.submit(GameInfo.parse_monster,
                                       element,
                                       monster_path,
                                       monster_scale_factor,
                                       monster_actions,
                                       default_monster_action):
                           element for element in xml_root.findall("./Monsters/Monster")}
            for future in concurrent.futures.as_completed(futures):
                try:
                    monster = future.result().to_monster_info()
                    monsters[monster.name] = monster
                except Exception as exc:
                    print(f'{futures[future]} throws {exc}', flush=True)
        # print(f'Time elapsed loading {len(monsters)} monsters: {time.time()-start_time}', flush=True)
        return monsters

    @staticmethod
    def parse_monster(element: ET.Element,
                      monster_path: str,
                      monster_scale_factor: float,
                      monster_actions: Dict[str, MonsterAction],
                      default_monster_action: MonsterAction) -> MonsterInfoPicklable:
        monster_name = element.attrib['name']

        monster_image_file_name = os.path.join(monster_path, element.attrib['image'])
        unscaled_monster_image = pygame.image.load(monster_image_file_name)

        black_border_pixels = 1
        if 0 == black_border_pixels:
            monster_image = pygame.transform.scale(unscaled_monster_image,
                                                   (unscaled_monster_image.get_width() * monster_scale_factor,
                                                    unscaled_monster_image.get_height() * monster_scale_factor))
        else:
            # First, scale up the monster images.
            # Then expand them a few pixels and put a thin black border around them to off contrast.
            scaled_monster_image = pygame.transform.scale(unscaled_monster_image,
                                                          (unscaled_monster_image.get_width() * monster_scale_factor,
                                                           unscaled_monster_image.get_height() * monster_scale_factor))
            monster_image = pygame.surface.Surface((scaled_monster_image.get_width() + 2 * black_border_pixels,
                                                    scaled_monster_image.get_height() + 2 * black_border_pixels),
                                                   pygame.SRCALPHA)

            # Fill the image with transparency, then perform 4 blits to create the border.
            # Convert the border to black a final fill multiplying the RGB values by 0.
            monster_image.fill(pygame.Color(0, 0, 0, 0))
            monster_image.blit(scaled_monster_image, (0, black_border_pixels))
            monster_image.blit(scaled_monster_image, (black_border_pixels, 0))
            monster_image.blit(scaled_monster_image, (black_border_pixels, 2*black_border_pixels))
            monster_image.blit(scaled_monster_image, (2*black_border_pixels, black_border_pixels))
            monster_image.fill('black', special_flags=pygame.BLEND_RGB_MULT)

            # Blit the main image into the center
            monster_image.blit(scaled_monster_image, (black_border_pixels, black_border_pixels))

        (min_hp, max_hp) = GameTypes.parse_int_range(element.attrib['hp'])
        (min_gp, max_gp) = GameTypes.parse_int_range(element.attrib['gp'])

        monster_action_rules = []
        for monster_action_rules_element in element.findall("./MonsterActionRule"):
            health_ratio_threshold = 1.0
            if 'healthRatioThreshold' in monster_action_rules_element.attrib:
                health_ratio_threshold = float(monster_action_rules_element.attrib['healthRatioThreshold'])
            monster_action_rules.append(MonsterActionRule(
                monster_actions[monster_action_rules_element.attrib['type']],
                float(monster_action_rules_element.attrib['probability']),
                health_ratio_threshold))
        monster_action_rules.append(MonsterActionRule(default_monster_action))

        allows_critical_hits = True
        if 'allowsCriticalHits' in element.attrib:
            allows_critical_hits = element.attrib['allowsCriticalHits'] == 'yes'

        may_run_away = True
        if 'mayRunAway' in element.attrib:
            may_run_away = element.attrib['mayRunAway'] == 'yes'

        return MonsterInfoPicklable(
            monster_name,
            SurfacePickable.from_surface(monster_image),
            int(element.attrib['strength']),
            int(element.attrib['agility']),
            min_hp,
            max_hp,
            GameTypes.parse_float(element.attrib['sleepResist']),
            GameTypes.parse_float(element.attrib['stopspellResist']),
            GameTypes.parse_float(element.attrib['hurtResist']),
            GameTypes.parse_float(element.attrib['dodge']),
            GameTypes.parse_float(element.attrib['blockFactor']),
            int(element.attrib['xp']),
            min_gp,
            max_gp,
            monster_action_rules,
            allows_critical_hits,
            may_run_away)

    @staticmethod
    def parse_monster_sets(xml_root: ET.Element) -> Dict[str, List[str]]:
        monster_sets: Dict[str, List[str]] = {}
        for element in xml_root.findall("./MonsterSets/MonsterSet"):
            monsters: List[str] = []
            for monster_element in element.findall("./Monster"):
                monsters.append(monster_element.attrib['name'])
            monster_sets[element.attrib['name']] = monsters
        return monster_sets

    def parse_maps(self, xml_root: ET.Element, maps_path: str) -> Dict[str, Map]:
        maps: Dict[str, Map] = {}
        for element in xml_root.findall("./Maps//Map"):
            map_name = element.attrib['name']
            self.map_being_parsed = map_name
            # print( 'mapName =', map_name, flush=True )
            music = element.attrib['music']
            light_diameter = None
            if 'lightDiameter' in element.attrib and element.attrib['lightDiameter'] != 'unlimited':
                light_diameter = int(element.attrib['lightDiameter'])
            is_outside = True
            if 'isOutside' in element.attrib:
                is_outside = element.attrib['isOutside'] == 'yes'
            origin = None
            if 'originX' in element.attrib and 'originY' in element.attrib:
                origin = Point(int(element.attrib['originX']), int(element.attrib['originY']))

            # Parse transitions
            # print('Parse transitions', flush=True)
            leaving_transition: Optional[OutgoingTransition] = None
            point_transitions: List[OutgoingTransition] = []
            incoming_transitions: List[IncomingTransition] = []
            transitions_by_map: Dict[str, AnyTransition] = {}
            transitions_by_map_and_name: Dict[str, Dict[str, AnyTransition]] = {}
            transitions_by_name: Dict[str, AnyTransition] = {}
            map_decorations: List[MapDecoration] = []

            def update_transitions_by_map(transition: AnyTransition) -> None:
                if transition.dest_map is not None:
                    transitions_by_map[transition.dest_map] = transition
                    if transition.name is not None:
                        if transition.dest_map not in transitions_by_map_and_name:
                            transitions_by_map_and_name[transition.dest_map] = {}
                        transitions_by_map_and_name[transition.dest_map][transition.name] = transition
                        transitions_by_name[transition.name] = transition

            def parse_incoming_transition(trans_element: ET.Element) -> IncomingTransition:
                name = None
                if 'name' in trans_element.attrib:
                    name = trans_element.attrib['name']
                progress_marker = None
                if 'progressMarker' in trans_element.attrib:
                    progress_marker = trans_element.attrib['progressMarker']
                inverse_progress_marker = None
                if 'inverseProgressMarker' in trans_element.attrib:
                    inverse_progress_marker = trans_element.attrib['inverseProgressMarker']
                transition = IncomingTransition(self.get_location(map_name, trans_element),
                                                self.get_direction(map_name, trans_element),
                                                name,
                                                trans_element.attrib['toMap'],
                                                progress_marker)
                update_transitions_by_map(transition)
                transition = IncomingTransition(self.get_location(map_name, trans_element),
                                                self.get_direction(map_name, trans_element),
                                                name,
                                                trans_element.attrib['toMap'],
                                                progress_marker,
                                                inverse_progress_marker)
                update_transitions_by_map(transition)
                if 'decoration' in trans_element.attrib and trans_element.attrib['decoration'] in self.decorations:
                    map_decorations.append(MapDecoration.create(self.decorations[trans_element.attrib['decoration']],
                                                                transition.point,
                                                                None,
                                                                progress_marker,
                                                                inverse_progress_marker))
                return transition

            def parse_outgoing_transition(trans_element: ET.Element) -> OutgoingTransition:
                name = None
                if 'name' in trans_element.attrib:
                    name = trans_element.attrib['name']
                dest_name = None
                if 'toName' in trans_element.attrib:
                    dest_name = trans_element.attrib['toName']
                respawn_decorations = False
                if 'respawnDecorations' in trans_element.attrib:
                    respawn_decorations = trans_element.attrib['respawnDecorations'] == 'yes'
                progress_marker = None
                if 'progressMarker' in trans_element.attrib:
                    progress_marker = trans_element.attrib['progressMarker']
                inverse_progress_marker = None
                if 'inverseProgressMarker' in trans_element.attrib:
                    inverse_progress_marker = trans_element.attrib['inverseProgressMarker']
                bounding_box = None
                if ('leftX' in trans_element.attrib and
                        'rightX' in trans_element.attrib and
                        'topY' in trans_element.attrib and
                        'bottomY' in trans_element.attrib):
                    left_x = int(trans_element.attrib['leftX'])
                    right_x = int(trans_element.attrib['rightX'])
                    top_y = int(trans_element.attrib['topY'])
                    bottom_y = int(trans_element.attrib['bottomY'])
                    bounding_box = pygame.Rect(left_x, top_y, right_x - left_x, bottom_y - top_y)
                transition = OutgoingTransition(self.get_location(map_name, trans_element),
                                                self.get_direction(map_name, trans_element),
                                                name,
                                                trans_element.attrib['toMap'],
                                                dest_name,
                                                respawn_decorations,
                                                progress_marker,
                                                inverse_progress_marker,
                                                bounding_box)
                update_transitions_by_map(transition)
                if 'decoration' in trans_element.attrib and trans_element.attrib['decoration'] in self.decorations:
                    map_decorations.append(MapDecoration.create(self.decorations[trans_element.attrib['decoration']],
                                                                transition.point,
                                                                None,
                                                                progress_marker,
                                                                inverse_progress_marker))
                return transition

            trans_element = element.find('.//LeavingTransition')
            if trans_element is not None:
                leaving_transition = parse_outgoing_transition(trans_element)
            for trans_element in element.findall('.//PointTransition'):
                point_transitions.append(parse_outgoing_transition(trans_element))
            for trans_element in element.findall('.//IncomingTransition'):
                incoming_transitions.append(parse_incoming_transition(trans_element))

            # Parse standalone decorations
            # print( 'Parse standalone decorations', flush=True )
            for decoration_element in element.findall('.//MapDecoration'):
                decoration = None
                if 'type' in decoration_element.attrib and decoration_element.attrib['type'] in self.decorations:
                    decoration = self.decorations[decoration_element.attrib['type']]
                progress_marker = None
                if 'progressMarker' in decoration_element.attrib:
                    progress_marker = decoration_element.attrib['progressMarker']
                inverse_progress_marker = None
                if 'inverseProgressMarker' in decoration_element.attrib:
                    inverse_progress_marker = decoration_element.attrib['inverseProgressMarker']
                map_decorations.append(MapDecoration.create(
                    decoration,
                    self.get_location(map_name, decoration_element),
                    self.parse_dialog(decoration_element),
                    progress_marker,
                    inverse_progress_marker))

            # Parse NPCs
            # print( 'Parse NPCs', flush=True )
            npcs: List[NpcInfo] = []
            for npc_element in element.findall('.//NonPlayerCharacter'):
                progress_marker = None
                name = None
                if 'name' in npc_element.attrib:
                    name = npc_element.attrib['name']
                if 'progressMarker' in npc_element.attrib:
                    progress_marker = npc_element.attrib['progressMarker']
                inverse_progress_marker = None
                if 'inverseProgressMarker' in npc_element.attrib:
                    inverse_progress_marker = npc_element.attrib['inverseProgressMarker']
                npcs.append(NpcInfo(self.character_types[npc_element.attrib['type']],
                                    self.get_location(map_name, npc_element),
                                    self.get_direction(map_name, npc_element),
                                    npc_element.attrib['walking'] == 'yes',
                                    self.parse_dialog(npc_element),
                                    progress_marker,
                                    inverse_progress_marker,
                                    name,
                                    self.parse_waypoints(map_name, npc_element)))

            # Parse special monsters
            # print( 'Parse special monsters', flush=True )
            special_monsters: List[SpecialMonster] = []
            for monster_element in element.findall('.//Monster'):
                # print( 'monster_element =', monster_element, flush=True )
                # print( 'monster_element.attrib =', monster_element.attrib, flush=True )
                approach_dialog = None
                approach_dialog_element = monster_element.find('ApproachDialog')
                if approach_dialog_element is not None:
                    approach_dialog = self.parse_dialog(approach_dialog_element)
                victory_dialog = None
                victory_dialog_element = monster_element.find('VictoryDialog')
                if victory_dialog_element is not None:
                    victory_dialog = self.parse_dialog(victory_dialog_element)
                run_away_dialog = None
                run_away_dialog_element = monster_element.find('RunAwayDialog')
                if run_away_dialog_element is not None:
                    run_away_dialog = self.parse_dialog(run_away_dialog_element)
                progress_marker = None
                if 'progressMarker' in monster_element.attrib:
                    progress_marker = monster_element.attrib['progressMarker']
                inverse_progress_marker = None
                if 'inverseProgressMarker' in monster_element.attrib:
                    inverse_progress_marker = monster_element.attrib['inverseProgressMarker']
                if monster_element.attrib['name'] not in self.monsters:
                    print(f'ERROR: Skipping special monster of unknown type {monster_element.attrib["name"]}',
                          flush=True)
                    continue
                special_monsters.append(SpecialMonster(
                    self.monsters[monster_element.attrib['name']],
                    self.get_location(map_name, monster_element),
                    approach_dialog,
                    victory_dialog,
                    run_away_dialog,
                    progress_marker,
                    inverse_progress_marker))

            # Load map dat file
            # print('Load map dat file', flush=True)
            map_dat_file_name = os.path.join(maps_path, element.attrib['tiles'])
            map_tiled_file_name = None
            map_dat = []
            map_overlay_dat = None
            if map_dat_file_name.endswith('.tmx'):
                map_tiled_file_name = map_dat_file_name
            else:
                with open(map_dat_file_name, 'r') as map_dat_file:
                    # Future: Could corner turn data from row,col (y,x) into col,row (x,y)
                    for line in map_dat_file:
                        line = line.strip('\n')
                        map_dat.append(line)
                        # TODO: Validate the map is rectangular and all tiles are defined
                map_dat_size = Point(len(map_dat[0]), len(map_dat))

                # Conditionally load map dat overlap file
                if 'overlayTiles' in element.attrib:
                    # print('Load map overlay dat file', flush=True)
                    map_overlay_dat = []
                    map_overlay_dat_file_name = os.path.join(maps_path, element.attrib['overlayTiles'])
                    with open(map_overlay_dat_file_name, 'r') as map_overlay_dat_file:
                        # Future: Could corner turn data from row,col (y,x) into col,row (x,y)
                        for line in map_overlay_dat_file:
                            line = line.strip('\n')
                            map_overlay_dat.append(line)
                            # TODO: Validate the map is rectangular and all tiles are defined
                    map_overlay_dat_size = Point(len(map_overlay_dat[0]), len(map_overlay_dat))
                    if map_dat_size != map_overlay_dat_size:
                        print('ERROR: Size mismatch between the map and map overlaps.  Map size =', map_dat_size,
                              '; Overlay size =', map_overlay_dat_size, flush=True)

            # Parse map monster info
            # print('Parse map monster info', flush=True)
            monster_zones = []
            if 'monsterSet' in element.attrib:
                monster_zones.append(MonsterZone(0,
                                                 0,
                                                 999999999,
                                                 999999999,
                                                 element.attrib['monsterSet']))
            else:
                for monster_zone_element in element.findall('.//MonsterZones/MonsterZone'):
                    monster_zones.append(MonsterZone(
                        int(monster_zone_element.attrib['x']),
                        int(monster_zone_element.attrib['y']),
                        int(monster_zone_element.attrib['w']),
                        int(monster_zone_element.attrib['h']),
                        monster_zone_element.attrib['set']))

            # Load the encounter image
            # print('Load the encounter image', flush=True)
            encounter_background = None
            if len(monster_zones) > 0 and 'encounterBackground' in element.attrib and \
                    element.attrib['encounterBackground'] in self.encounter_backgrounds:
                encounter_background = self.encounter_backgrounds[element.attrib['encounterBackground']]

            # Save the map information
            # print('Save the map information', flush=True)
            maps[map_name] = Map(map_name,
                                 map_tiled_file_name,
                                 map_dat,
                                 map_overlay_dat,
                                 music,
                                 light_diameter,
                                 leaving_transition,
                                 point_transitions,
                                 incoming_transitions,
                                 transitions_by_map,
                                 transitions_by_map_and_name,
                                 transitions_by_name,
                                 map_decorations,
                                 npcs,
                                 monster_zones,
                                 encounter_background,
                                 special_monsters,
                                 is_outside,
                                 origin)
            self.map_being_parsed = None
        return maps

    def get_location(self, map_name: Optional[str], element: ET.Element) -> Point:
        if map_name and 'location' in element.attrib:
            return self.locations[map_name][element.attrib['location']].point
        return Point(int(element.attrib['x']), int(element.attrib['y']))

    def get_direction(self, map_name: Optional[str], element: ET.Element) -> Direction:
        direction = self.get_optional_direction(map_name, element)
        if direction is None:
            direction = Direction.NORTH
        return direction

    def get_optional_direction(self, map_name: Optional[str], element: ET.Element) -> Optional[Direction]:
        if map_name and 'location' in element.attrib:
            location = self.locations[map_name][element.attrib['location']]
            if location.dir:
                return location.dir
        if 'dir' in element.attrib:
            return Direction[element.attrib['dir']]
        return None

    def parse_initial_game_state(self, pc_name: Optional[str] = None) -> None:
        # TODO: Introduce a game type to hold this information
        # TODO: Better yet, replace this method entirely with GameState.load as this is game state information and not
        #       generic game info information.

        self.pc_name = ''

        if pc_name is not None:
            self.pc_name = pc_name

        xml_root = ET.parse(self.game_xml_path).getroot()
        initial_state_element = xml_root.find('InitialState')
        if initial_state_element is None:
            print('ERROR: InitialState element is missing', flush=True)
            raise Exception('Missing required InitialState element')

        self.initial_map = initial_state_element.attrib['map']
        self.initial_hero_pos_dat_tile = self.get_location(self.initial_map, initial_state_element)
        self.initial_hero_pos_dir = self.get_direction(self.initial_map, initial_state_element)
        self.initial_state_dialog = self.parse_dialog(initial_state_element)

        if not self.pc_name:
            self.pc_name = initial_state_element.attrib['name']
        self.pc_xp = 0
        self.pc_gp = 0
        self.pc_hp = None
        self.pc_mp = None
        if 'hp' in initial_state_element.attrib:
            self.pc_hp = int(initial_state_element.attrib['hp'])
        if 'mp' in initial_state_element.attrib:
            self.pc_mp = int(initial_state_element.attrib['mp'])
        self.pc_weapon: Optional[Weapon] = None
        self.pc_armor: Optional[Armor] = None
        self.pc_shield: Optional[Shield] = None
        self.pc_other_equipped_items: List[Tool] = []
        for item_element in initial_state_element.findall("./EquippedItems/Item"):
            item_name = item_element.attrib['name']
            if item_name in self.weapons:
                self.pc_weapon = self.weapons[item_name]
            elif item_name in self.armors:
                self.pc_armor = self.armors[item_name]
            elif item_name in self.shields:
                self.pc_shield = self.shields[item_name]
            elif item_name in self.tools:
                self.pc_other_equipped_items.append(self.tools[item_name])
            else:
                print('ERROR: Unsupported item', item_name, flush=True)

        self.pc_unequipped_items: Dict[ItemType, int] = {}
        for item_element in initial_state_element.findall("./UnequippedItems/Item"):
            item_name = item_element.attrib['name']
            item_count = 1
            if 'count' in item_element.attrib:
                item_count = int(item_element.attrib['count'])
            if item_name in self.items:
                self.pc_unequipped_items[self.items[item_name]] = item_count
            else:
                print('ERROR: Unsupported item', item_name, flush=True)

        self.pc_progress_markers: List[str] = []
        for progress_marker_element in initial_state_element.findall("./ProgressMarkers/ProgressMarker"):
            self.pc_progress_markers.append(progress_marker_element.attrib['name'])
            # print('Loaded progress marker ' + progressMarkerElement.attrib['name'], flush=True)

        self.initial_map_decorations: List[MapDecoration] = []
        for decoration_element in initial_state_element.findall("./MapDecoration"):
            decoration = None
            if 'type' in decoration_element.attrib and decoration_element.attrib['type'] in self.decorations:
                decoration = self.decorations[decoration_element.attrib['type']]
            self.initial_map_decorations.append(MapDecoration.create(
                decoration,
                self.get_location(self.initial_map, decoration_element),
                self.parse_dialog(decoration_element),
                None,
                None))

    def parse_dialog(self, dialog_root_element: Optional[ET.Element]) -> Optional[DialogType]:
        if dialog_root_element is None:
            return None
        dialog: DialogType = []
        for element in dialog_root_element:
            # print('in parseDialog: element =', element, flush=True)

            label = None
            if 'label' in element.attrib and element.attrib['label'] != 'None':
                label = element.attrib['label']

            name = None
            if 'name' in element.attrib:
                name = element.attrib['name']

            count: Union[int, str] = 1
            if 'count' in element.attrib:
                if ('unlimited' == element.attrib['count']
                        or ('[' == element.attrib['count'][0] and ']' == element.attrib['count'][-1])):
                    count = element.attrib['count']
                else:
                    try:
                        count = int(element.attrib['count'])
                    except ValueError:
                        GameTypes.parse_int_range(element.attrib['count'])
                        count = element.attrib['count']

            map_name = self.map_being_parsed
            if 'map' in element.attrib:
                map_name = element.attrib['map']

            map_pos = None
            try:
                map_pos = self.get_location(map_name, element)
            except Exception:
                pass

            map_dir = None
            try:
                map_dir = self.get_optional_direction(map_name, element)
            except Exception:
                pass

            if element.tag == 'DialogGoTo':
                if label is not None:
                    dialog.append(DialogGoTo(label))

            elif element.tag == 'Dialog':
                if element.text is not None:
                    dialog.append(element.text)
                    if label is not None:
                        self.dialog_sequences[label] = [element.text]

            elif element.tag == 'DialogOptions':
                dialog_options = {}
                for option_element in element.findall("./DialogOption"):
                    dialog_option = self.parse_dialog(option_element)
                    if dialog_option is None:
                        dialog_option = []
                    if dialog_option is not None:
                        dialog_options[option_element.attrib['name']] = dialog_option
                        if 'label' in option_element.attrib and option_element.attrib['label'] is not None:
                            self.dialog_sequences[option_element.attrib['label']] = dialog_option
                if len(dialog_options) > 0:
                    dialog.append(dialog_options)
                    if label is not None:
                        self.dialog_sequences[label] = [dialog_options]

            elif element.tag == 'DialogVendorBuyOptions':
                if 'values' in element.attrib:
                    dialog_vendor_buy_options: DialogVendorBuyOptionsParamType = element.attrib['values']
                else:
                    dialog_vendor_buy_options = []
                    for option_element in element.findall("./DialogVendorBuyOption"):
                        item_name = option_element.attrib['name']
                        item_gp = str(self.items[item_name].gp)
                        if 'gp' in option_element.attrib:
                            item_gp = option_element.attrib['gp']
                        dialog_vendor_buy_options.append([item_name, item_gp])
                dialog.append(DialogVendorBuyOptions(dialog_vendor_buy_options))

            elif element.tag == 'DialogVendorSellOptions':
                if 'values' in element.attrib:
                    dialog_vendor_sell_options: DialogVendorSellOptionsParamType = element.attrib['values']
                else:
                    dialog_vendor_sell_options = []
                    for option_element in element.findall("./DialogVendorSellOption"):
                        dialog_vendor_sell_options.append(option_element.attrib['type'])
                dialog.append(DialogVendorSellOptions(dialog_vendor_sell_options))

            elif element.tag in ('DialogAssert', 'DialogCheck'):
                conditional_dialog = self.parse_dialog(element)
                dialog.append(DialogCheck(DialogCheckEnum[element.attrib['type']],
                                          dialog=conditional_dialog,
                                          name=name,
                                          count=count,
                                          map_name=map_name,
                                          map_pos=map_pos,
                                          is_assert=element.tag == 'DialogAssert'))
                if label is not None and conditional_dialog is not None:
                    self.dialog_sequences[label] = conditional_dialog

            elif element.tag == 'DialogAction':
                approach_dialog: Optional[DialogType] = None
                approach_dialog_element = element.find('ApproachDialog')
                if approach_dialog_element is not None:
                    approach_dialog = self.parse_dialog(approach_dialog_element)

                victory_dialog: Optional[DialogType] = None
                victory_dialog_element = element.find('VictoryDialog')
                if victory_dialog_element is not None:
                    victory_dialog = self.parse_dialog(victory_dialog_element)

                run_away_dialog: Optional[DialogType] = None
                run_away_dialog_element = element.find('RunAwayDialog')
                if run_away_dialog_element is not None:
                    run_away_dialog = self.parse_dialog(run_away_dialog_element)

                fade_dialog: Optional[DialogType] = None
                fade_dialog_element = element.find('FadeDialog')
                if fade_dialog_element is not None:
                    fade_dialog = self.parse_dialog(fade_dialog_element)

                encounter_music = None
                if 'encounterMusic' in element.attrib:
                    encounter_music = element.attrib['encounterMusic']

                bypass = False
                if 'bypass' in element.attrib:
                    bypass = element.attrib['bypass'] == 'yes'

                decay_steps = None
                if 'decay' in element.attrib and 'unlimited' != element.attrib['decay']:
                    decay_steps = int(element.attrib['decay'])

                category = ActionCategoryTypeEnum.PHYSICAL
                if 'category' in element.attrib:
                    category = ActionCategoryTypeEnum[element.attrib['category']]

                # For DAMAGE_TARGET count should NOT default to 1
                if (DialogActionEnum[element.attrib['type']] == DialogActionEnum.DAMAGE_TARGET
                        and 'count' not in element.attrib):
                    count = 'default'

                dialog.append(DialogAction(DialogActionEnum[element.attrib['type']],
                                           name=name,
                                           count=count,
                                           bypass=bypass,
                                           decay_steps=decay_steps,
                                           fade_dialog=fade_dialog,
                                           category=category,
                                           map_name=map_name,
                                           map_pos=map_pos,
                                           map_dir=map_dir,
                                           approach_dialog=approach_dialog,
                                           victory_dialog=victory_dialog,
                                           run_away_dialog=run_away_dialog,
                                           encounter_music=encounter_music))

            elif element.tag == 'DialogVariable':
                name = element.attrib['name']
                value = element.attrib['value']
                if value == 'ITEM_LIST':
                    value_for_dialog_vendor_buy_options: DialogVendorBuyOptionsParamWithoutReplacementType = []
                    for item_element in element.findall("./Item"):
                        item_name = item_element.attrib['name']
                        item_gp = str(self.items[item_name].gp)
                        if 'gp' in item_element.attrib:
                            item_gp = item_element.attrib['gp']
                        value_for_dialog_vendor_buy_options.append([item_name, item_gp])
                    dialog.append(DialogVendorBuyOptionsVariable(name, value_for_dialog_vendor_buy_options))
                elif value == 'INVENTORY_ITEM_TYPE_LIST':
                    value_for_dialog_vendor_sell_options: DialogVendorSellOptionsParamWithoutReplacementType = []
                    for item_type_element in element.findall("./InventoryItemType"):
                        value_for_dialog_vendor_sell_options.append(item_type_element.attrib['type'])
                    dialog.append(DialogVendorSellOptionsVariable(name, value_for_dialog_vendor_sell_options))
                else:
                    dialog.append(DialogVariable(name, value))

        if len(dialog) > 0:
            return dialog

        return None

    def parse_waypoints(self, map_name: Optional[str], waypoints_root_element: ET.Element) -> List[Point]:
        waypoints = []
        for waypoint_element in waypoints_root_element.findall("./Waypoint"):
            waypoints.append(self.get_location(map_name, waypoint_element))
        return waypoints

    def get_item(self, name: str) -> Optional[ItemType]:
        if name in self.items:
            return self.items[name]
        return None

    def random_tile_image(self, symbol: str, idx: int = 0) -> pygame.surface.Surface:
        images = self.tiles[self.tile_symbols[symbol]].images[idx]
        num_images = len(images)
        if 1 == num_images:
            random_index = 0
        else:
            random_index = numpy.random.choice(list(range(num_images)), p=self.tile_probabilities[num_images - 1])
        return images[random_index]
