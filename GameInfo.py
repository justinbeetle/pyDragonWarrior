#!/usr/bin/env python

from typing import Dict, List, Optional, Union

import os
import pygame
import numpy
import xml.etree.ElementTree

from AudioPlayer import AudioPlayer
from GameTypes import ActionCategoryTypeEnum, Armor, CharacterType, Decoration, DialogAction, DialogActionEnum, \
    DialogCheck, DialogCheckEnum, DialogGoTo, DialogType, DialogVariable, DialogVendorBuyOptions, \
    DialogVendorBuyOptionsParamWithoutReplacementType,  DialogVendorBuyOptionsParamType, \
    DialogVendorBuyOptionsVariable, DialogVendorSellOptions, DialogVendorSellOptionsParamWithoutReplacementType, \
    DialogVendorSellOptionsParamType, DialogVendorSellOptionsVariable, Direction, GameTypes, ItemType, \
    LeavingTransition, Level, Map, MapDecoration, MapImageInfo, MonsterAction, MonsterActionRule, \
    MonsterInfo, MonsterZone, NpcInfo, Phase, PointTransition, Shield, SpecialMonster, Spell, TargetTypeEnum, Tile, \
    Tool, Weapon
from Point import Point


class GameInfo:
    TRANSPARENT_COLOR = pygame.Color(0, 128, 128)
   
    def __init__(self,
                 base_path: str,
                 game_xml_path: str,
                 tile_size_pixels: int,
                 saved_game_file: Optional[str] = None) -> None:

        self.tile_size_pixels = tile_size_pixels
        self.dialog_sequences: Dict[str, DialogType] = {}

        # TODO: Need to determine a method for determining how much to scale the monster images
        monster_scale_factor = 4

        # Parse XML
        xml_root = xml.etree.ElementTree.parse(game_xml_path).getroot()
        self.saves_path = os.path.join(base_path, xml_root.attrib['savesPath'])
        data_path = os.path.join(base_path, xml_root.attrib['dataPath'])
        image_path = os.path.join(data_path, xml_root.attrib['imagePath'])
        music_path = os.path.join(data_path, xml_root.attrib['musicPath'])
        sound_path = os.path.join(data_path, xml_root.attrib['soundPath'])
        tile_path = os.path.join(image_path, xml_root.attrib['tilePath'])
        maps_path = os.path.join(data_path, xml_root.attrib['mapsPath'])
        decoration_path = os.path.join(image_path, xml_root.attrib['decorationPath'])
        character_path = os.path.join(image_path, xml_root.attrib['characterPath'])
        monster_path = os.path.join(image_path, xml_root.attrib['monsterPath'])
        encounter_path = os.path.join(image_path, xml_root.attrib['encounterPath'])

        # Initialize the music player
        audio_player = AudioPlayer()
        audio_player.set_music_path(music_path)
        audio_player.set_sound_path(sound_path)

        # Parse items
        self.items: Dict[str, ItemType] = {}

        # Parse weapons
        self.weapons: Dict[str, Weapon] = {}
        for element in xml_root.findall("./Items/Weapons/Weapon"):
            item_name = element.attrib['name']
            use_dialog = self.parse_dialog(element)
            if use_dialog is None:
                print('ERROR: No use dialog for weapon', item_name, flush=True)
                continue
            target_type = TargetTypeEnum.SINGLE_ENEMY
            if 'target' in element.attrib:
                target_type = TargetTypeEnum[element.attrib['target']]
            self.weapons[item_name] = Weapon(
                item_name,
                int(element.attrib['attackBonus']),
                int(element.attrib['gp']),
                target_type,
                use_dialog)
            self.items[item_name] = self.weapons[item_name]

        # Get default weapon
        weapons_element = xml_root.find('Weapon')
        if weapons_element is not None and 'default' in weapons_element.attrib:
            self.default_weapon = self.weapons[weapons_element.attrib['default']]
        else:
            self.default_weapon = next(iter(self.weapons.values()))
        # The default weapon isn't actually an item so remove it from the weapon and item lists
        del self.weapons[self.default_weapon.name]
        del self.items[self.default_weapon.name]
         
        # Parse armors
        self.armors: Dict[str, Armor] = {}
        for element in xml_root.findall("./Items/Armors/Armor"):
            item_name = element.attrib['name']

            hp_regen_tiles = None
            if 'hpRegenTiles' in element.attrib and 'none' != element.attrib['hpRegenTiles']:
                hp_regen_tiles = int(element.attrib['hpRegenTiles'])

            self.armors[item_name] = Armor(
                item_name,
                int(element.attrib['defenseBonus']),
                int(element.attrib['gp']),
                element.attrib['ignoresTilePenalties'] == 'yes',
                float(element.attrib['hurtDmgModifier']),
                float(element.attrib['fireDmgModifier']),
                float(element.attrib['stopspellResistance']),
                hp_regen_tiles)
            self.items[item_name] = self.armors[item_name]
         
        # Parse shields
        self.shields: Dict[str, Shield] = {}
        for element in xml_root.findall("./Items/Shields/Shield"):
            item_name = element.attrib['name']
            self.shields[item_name] = Shield(
                item_name,
                int(element.attrib['defenseBonus']),
                int(element.attrib['gp']))
            self.items[item_name] = self.shields[item_name]
         
        # Parse tools
        self.tools: Dict[str, Tool] = {}
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

            self.tools[item_name] = Tool(
                item_name,
                attack_bonus,
                defense_bonus,
                gp,
                element.attrib['droppable'] == 'yes',
                element.attrib['equippable'] == 'yes',
                self.parse_dialog(element),
                target_type)
            self.items[item_name] = self.tools[item_name]

        # Parse tiles
        self.tile_symbols: Dict[str, str] = {}  # tile symbol to tile name map
        self.tiles: Dict[str, Tile] = {}
        max_tile_variants = 1
        for element in xml_root.findall("./Tiles/Tile"):
            tile_name = element.attrib['name']
            tile_symbol = element.attrib['symbol']
            tile_image_file_name = os.path.join(tile_path, element.attrib['image'])
            tile_walkable = True
            can_talk_over = False
            hp_penalty = 0
            mp_penalty = 0
            speed = 1.0
            spawn_rate = 1.0
            tile_type = 'simple'
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
            
            # print('Loading image', tileImageFileName, flush=True)
            tile_image_unscaled = pygame.image.load(tile_image_file_name).convert()
            if tile_type == 'complex' or tile_image_unscaled.get_height() > self.tile_size_pixels:
                image_index_translation = [[9, 8, 12, 13], [1, 0, 4, 5], [3, 2, 6, 7], [11, 10, 14, 15]]
                tile_images_scaled: List[List[pygame.Surface]] = []
                for x in range(16):
                    tile_images_scaled.append([])
                unscaled_size = tile_image_unscaled.get_height()/4
                tile_variants = tile_image_unscaled.get_width() // tile_image_unscaled.get_height()
                max_tile_variants = max(max_tile_variants, tile_variants)
                for y in range(4):
                    for x in range(4):
                        for z in range(tile_variants):
                            temp = pygame.Surface((self.tile_size_pixels, self.tile_size_pixels))
                            pygame.transform.scale(tile_image_unscaled.subsurface(
                                pygame.Rect(x*unscaled_size + z*tile_image_unscaled.get_height(),
                                            y*unscaled_size, unscaled_size, unscaled_size)),
                                (self.tile_size_pixels, self.tile_size_pixels),
                                temp)
                            tile_images_scaled[image_index_translation[y][x]].append(temp)
            else:
                tile_variants = tile_image_unscaled.get_width() // tile_image_unscaled.get_height()
                max_tile_variants = max(max_tile_variants, tile_variants)
                temp = []
                for z in range(tile_variants):
                    temp.append(pygame.Surface((self.tile_size_pixels, self.tile_size_pixels)))
                    pygame.transform.scale(tile_image_unscaled.subsurface(
                        pygame.Rect(z*tile_image_unscaled.get_height(),
                                    0,
                                    tile_image_unscaled.get_height(),
                                    tile_image_unscaled.get_height())),
                        (self.tile_size_pixels, self.tile_size_pixels),
                        temp[-1])
                tile_images_scaled = [temp] * 16
         
            self.tile_symbols[tile_symbol] = tile_name
            self.tiles[tile_name] = Tile(tile_name,
                                         tile_symbol,
                                         tile_images_scaled,
                                         tile_walkable,
                                         can_talk_over,
                                         hp_penalty,
                                         mp_penalty,
                                         speed,
                                         spawn_rate)
        self.tile_probabilities: List[List[float]] = [[1.0]]
        for x in range(2, max_tile_variants + 1):
            w = numpy.arange(x, 0, -1)
            w = w * numpy.transpose(w)
            w = w * numpy.transpose(w)
            p = w / sum(w)
            self.tile_probabilities.append(p)

        # Parse decorations
        self.decorations: Dict[str, Decoration] = {}
        for element in xml_root.findall("./Decorations/Decoration"):
            decoration_name = element.attrib['name']
            width_tiles = 1
            height_tiles = 1
            walkable = True
            remove_with_search = False
            remove_with_key = False
            remove_sound = None
            if 'widthTiles' in element.attrib:
                width_tiles = int(element.attrib['widthTiles'])
            if 'heightTiles' in element.attrib:
                height_tiles = int(element.attrib['heightTiles'])
            if 'walkable' in element.attrib:
                walkable = element.attrib['walkable'] == 'yes'
            if 'removeWithSearch' in element.attrib:
                remove_with_search = element.attrib['removeWithSearch'] == 'yes'
            if 'removeWithKey' in element.attrib:
                remove_with_key = element.attrib['removeWithKey'] == 'yes'
            if 'removeSound' in element.attrib:
                remove_sound = element.attrib['removeSound']
            
            decoration_image_filename = os.path.join(decoration_path, element.attrib['image'])
            # print('Loading image', decoration_image_filename, flush=True)
            decoration_image_unscaled = pygame.image.load(decoration_image_filename).convert()
            unscaled_size_pixels = Point(decoration_image_unscaled.get_size())
            max_scaled_size_pixels = Point(width_tiles, height_tiles) * self.tile_size_pixels
            scale_factor_point = (max_scaled_size_pixels / unscaled_size_pixels).floor()
            scale_factor = max(scale_factor_point.w, scale_factor_point.h)
            scaled_size_pixels = unscaled_size_pixels * scale_factor
            decoration_image_scaled = pygame.Surface(scaled_size_pixels)
            pygame.transform.scale(decoration_image_unscaled, scaled_size_pixels, decoration_image_scaled)
            decoration_image_scaled.set_colorkey(GameInfo.TRANSPARENT_COLOR)
            self.decorations[decoration_name] = Decoration(decoration_name,
                                                           decoration_image_scaled,
                                                           walkable,
                                                           remove_with_search,
                                                           remove_with_key,
                                                           remove_sound)

        # Parse spells
        self.spells: Dict[str, Spell] = {}
        for element in xml_root.findall("./Spells/Spell"):
            spell_name = element.attrib['name']
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
                print('ERROR: No use dialog for spell', spell_name, flush=True)
                continue

            self.spells[spell_name] = Spell(
                spell_name,
                int(element.attrib['mp']),
                available_in_combat,
                available_outside_combat,
                available_inside,
                available_outside,
                target_type,
                use_dialog)

        # Parse levels
        levels: Dict[str, List[Level]] = {}
        for element in xml_root.findall("./Levels/CharacterLevels"):
            character_type = element.attrib['type']
            levels[character_type] = []
            for level_element in element.findall("./Level"):
                level_name = level_element.attrib['name']
                level_number = len(levels[character_type])
                level_spell = None
                if 'spell' in level_element.attrib and level_element.attrib['spell'] in self.spells:
                    level_spell = self.spells[level_element.attrib['spell']]
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

        # Parse characters
        self.character_types: Dict[str, CharacterType] = {}
        for element in xml_root.findall("./CharacterTypes/CharacterType"):
            character_type = element.attrib['type']
            character_levels: List[Level] = []
            if 'levels' in element.attrib and element.attrib['levels'] in levels:
                character_levels = levels[element.attrib['levels']]
            character_type_filename = os.path.join(character_path, element.attrib['image'])
            # print('Loading image', character_type_filename, flush=True)
            character_type_image = pygame.image.load(character_type_filename).convert()
            character_type_images = {}
            x_px = 0
            for direction in [Direction.SOUTH, Direction.EAST, Direction.NORTH, Direction.WEST]:
                direction_character_type_images = {}
                for phase in [Phase.A, Phase.B]:
                    image = pygame.Surface((self.tile_size_pixels, self.tile_size_pixels))
                    pygame.transform.scale(character_type_image.subsurface(x_px,
                                                                           0,
                                                                           character_type_image.get_height(),
                                                                           character_type_image.get_height()),
                                           (self.tile_size_pixels, self.tile_size_pixels),
                                           image)
                    image.set_colorkey(GameInfo.TRANSPARENT_COLOR)
                    direction_character_type_images[phase] = image
                    x_px += character_type_image.get_height() + 1
                character_type_images[direction] = direction_character_type_images
            self.character_types[character_type] = CharacterType(character_type,
                                                                 character_type_images,
                                                                 character_levels)

        # Parse monster actions
        monster_actions: Dict[str, MonsterAction] = {}
        for element in xml_root.findall("./MonsterActions/MonsterAction"):
            action_name = element.attrib['name']
            spell = None
            target_type = TargetTypeEnum.SINGLE_ENEMY
            if 'spell' in element.attrib and element.attrib['spell'] in self.spells:
                spell = self.spells[element.attrib['spell']]
                target_type = spell.target_type
                use_dialog = spell.use_dialog
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
            self.default_monster_action = monster_actions[monster_actions_element.attrib['default']]
        else:
            self.default_monster_action = next(iter(monster_actions.values()))

        # Parse monsters
        self.monsters: Dict[str, MonsterInfo] = {}
        for element in xml_root.findall("./Monsters/Monster"):
            monster_name = element.attrib['name']

            monster_image_file_name = os.path.join(monster_path, element.attrib['image'])
            unscaled_monster_image = pygame.image.load(monster_image_file_name).convert()
            monster_image = pygame.transform.scale(unscaled_monster_image,
                                                   (unscaled_monster_image.get_width() * monster_scale_factor,
                                                    unscaled_monster_image.get_height() * monster_scale_factor))
            monster_image.set_colorkey(GameInfo.TRANSPARENT_COLOR)

            dmg_image = monster_image.copy()
            for x in range(dmg_image.get_width()):
                for y in range(dmg_image.get_height()):
                    if dmg_image.get_at((x, y)) != GameInfo.TRANSPARENT_COLOR:
                        dmg_image.set_at((x, y), pygame.Color('red'))

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

            allows_critical_hits = True
            if 'allowsCriticalHits' in element.attrib:
                allows_critical_hits = element.attrib['allowsCriticalHits'] == 'yes'

            self.monsters[monster_name] = MonsterInfo(
                monster_name,
                monster_image,
                dmg_image,
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
                allows_critical_hits)

        # Parse monster sets
        self.monster_sets: Dict[str, List[str]] = {}
        for element in xml_root.findall("./MonsterSets/MonsterSet"):
            monsters: List[str] = []
            for monster_element in element.findall("./Monster"):
                monsters.append(monster_element.attrib['name'])
            self.monster_sets[element.attrib['name']] = monsters
            self.monster_sets[element.attrib['name']] = monsters

        # Parse maps
        self.maps: Dict[str, Map] = {}
        for element in xml_root.findall("./Maps/Map"):
            map_name = element.attrib['name']
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
            # print( 'Parse transitions', flush=True )
            leaving_transition = None
            point_transitions: List[PointTransition] = []
            map_decorations: List[MapDecoration] = []
            trans_element = element.find('LeavingTransition')
            if trans_element is not None:
                respawn_decorations = False
                if 'respawnDecorations' in trans_element.attrib:
                    respawn_decorations = trans_element.attrib['respawnDecorations'] == 'yes'
                leaving_transition = LeavingTransition(trans_element.attrib['toMap'],
                                                       Point(int(trans_element.attrib['toX']),
                                                             int(trans_element.attrib['toY'])),
                                                       Direction[trans_element.attrib['toDir']],
                                                       respawn_decorations)
            for trans_element in element.findall('PointTransition'):
                respawn_decorations = False
                if 'respawnDecorations' in trans_element.attrib:
                    respawn_decorations = trans_element.attrib['respawnDecorations'] == 'yes'
                from_point = Point(int(trans_element.attrib['fromX']),
                                   int(trans_element.attrib['fromY']))
                progress_marker = None
                if 'progressMarker' in trans_element.attrib:
                    progress_marker = trans_element.attrib['progressMarker']
                inverse_progress_marker = None
                if 'inverseProgressMarker' in trans_element.attrib:
                    inverse_progress_marker = trans_element.attrib['inverseProgressMarker']
                point_transitions.append(PointTransition(from_point,
                                                         trans_element.attrib['toMap'],
                                                         Point(int(trans_element.attrib['toX']),
                                                               int(trans_element.attrib['toY'])),
                                                         Direction[trans_element.attrib['toDir']],
                                                         respawn_decorations,
                                                         progress_marker,
                                                         inverse_progress_marker))
                if 'decoration' in trans_element.attrib and trans_element.attrib['decoration'] in self.decorations:
                    map_decorations.append(MapDecoration(self.decorations[trans_element.attrib['decoration']],
                                                         from_point,
                                                         None,
                                                         progress_marker,
                                                         inverse_progress_marker))

            # Parse NPCs
            # print( 'Parse NPCs', flush=True )
            npcs: List[NpcInfo] = []
            for npc_element in element.findall('NonPlayerCharacter'):
                progress_marker = None
                if 'progressMarker' in npc_element.attrib:
                    progress_marker = npc_element.attrib['progressMarker']
                inverse_progress_marker = None
                if 'inverseProgressMarker' in npc_element.attrib:
                    inverse_progress_marker = npc_element.attrib['inverseProgressMarker']
                npcs.append(NpcInfo(self.character_types[npc_element.attrib['type']],
                                    Point(int(npc_element.attrib['x']),
                                          int(npc_element.attrib['y'])),
                                    Direction[npc_element.attrib['dir']],
                                    npc_element.attrib['walking'] == 'yes',
                                    self.parse_dialog(npc_element),
                                    progress_marker,
                                    inverse_progress_marker))

            # Parse standalone decorations
            # print( 'Parse standalone decorations', flush=True )
            for decoration_element in element.findall('MapDecoration'):
                decoration = None
                if 'type' in decoration_element.attrib and decoration_element.attrib['type'] in self.decorations:
                    decoration = self.decorations[decoration_element.attrib['type']]
                progress_marker = None
                if 'progressMarker' in decoration_element.attrib:
                    progress_marker = decoration_element.attrib['progressMarker']
                inverse_progress_marker = None
                if 'inverseProgressMarker' in decoration_element.attrib:
                    inverse_progress_marker = decoration_element.attrib['inverseProgressMarker']
                map_decorations.append(MapDecoration(
                    decoration,
                    Point(int(decoration_element.attrib['x']),
                          int(decoration_element.attrib['y'])),
                    self.parse_dialog(decoration_element),
                    progress_marker,
                    inverse_progress_marker))

            # Parse special monsters
            # print( 'Parse special monsters', flush=True )
            special_monsters: List[SpecialMonster] = []
            for monster_element in element.findall('Monster'):
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
                special_monsters.append(SpecialMonster(
                    self.monsters[monster_element.attrib['name']],
                    Point(int(monster_element.attrib['x']),
                          int(monster_element.attrib['y'])),
                    approach_dialog,
                    victory_dialog,
                    run_away_dialog,
                    progress_marker,
                    inverse_progress_marker))
         
            # Load map dat file
            # print('Load map dat file', flush=True)
            map_dat = []
            map_dat_file_name = os.path.join(maps_path, element.attrib['tiles'])
            map_dat_file = open(map_dat_file_name, 'r')
            # Future: Could corner turn data from row,col (y,x) into col,row (x,y)
            for line in map_dat_file:
                line = line.strip('\n')
                map_dat.append(line)
                # TODO: Validate the map is rectangular and all tiles are defined
            map_dat_file.close()
            map_dat_size = Point(len(map_dat[0]), len(map_dat))

            # Conditionally load map dat overlap file
            map_overlay_dat = None
            if 'overlayTiles' in element.attrib:
                # print('Load map overlay dat file', flush=True)
                map_overlay_dat = []
                map_overlay_dat_file_name = os.path.join(maps_path, element.attrib['overlayTiles'])
                map_overlay_dat_file = open(map_overlay_dat_file_name, 'r')
                # Future: Could corner turn data from row,col (y,x) into col,row (x,y)
                for line in map_overlay_dat_file:
                    line = line.strip('\n')
                    map_overlay_dat.append(line)
                    # TODO: Validate the map is rectangular and all tiles are defined
                map_overlay_dat_file.close()
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
                                                 int(map_dat_size.w),
                                                 int(map_dat_size.h),
                                                 element.attrib['monsterSet']))
            else:
                for monsterZoneElement in element.findall('MonsterZones/MonsterZone'):
                    monster_zones.append(MonsterZone(
                        int(monsterZoneElement.attrib['x']),
                        int(monsterZoneElement.attrib['y']),
                        int(monsterZoneElement.attrib['w']),
                        int(monsterZoneElement.attrib['h']),
                        monsterZoneElement.attrib['set']))

            # Load the encounter image
            # print('Load the encounter image', flush=True)
            encounter_image = None
            if len(monster_zones):
                encounter_image_file_name = os.path.join(encounter_path, element.attrib['encounterBackground'])
                unscaled_encounter_image = pygame.image.load(encounter_image_file_name).convert()
                encounter_image = pygame.transform.scale(unscaled_encounter_image,
                                                         (unscaled_encounter_image.get_width() * monster_scale_factor,
                                                          unscaled_encounter_image.get_height() * monster_scale_factor))

            # Save the map information
            # print('Save the map information', flush=True)
            self.maps[map_name] = Map(map_name,
                                      map_dat,
                                      map_overlay_dat,
                                      map_dat_size,
                                      music,
                                      light_diameter,
                                      leaving_transition,
                                      point_transitions,
                                      npcs,
                                      map_decorations,
                                      monster_zones,
                                      encounter_image,
                                      special_monsters,
                                      is_outside,
                                      origin)

        # Parse dialog scripts
        for element in xml_root.findall("./DialogScripts/DialogScript"):
            dialog_script = self.parse_dialog(element)
            if dialog_script is not None:
                self.dialog_sequences[element.attrib['label']] = dialog_script
         
        # Parse initial game state
        self.pc_name = ''
        initial_state_element = xml_root.find('InitialState')
        if saved_game_file is not None:
            if os.path.isfile(saved_game_file):
                save_game_file_path = saved_game_file
            else:
                save_game_file_path = os.path.join(self.saves_path, saved_game_file + '.xml')
            if os.path.isfile(save_game_file_path):
                print('Loading save game from file ' + save_game_file_path, flush=True)
                initial_state_element = xml.etree.ElementTree.parse(save_game_file_path).getroot()
            else:
                self.pc_name = saved_game_file
        if initial_state_element is None:
            print('ERROR: InitialState element is missing', flush=True)
            raise Exception('Missing required InitialState element')
         
        self.initial_map = initial_state_element.attrib['map']
        self.initial_hero_pos_dat_tile = Point(int(initial_state_element.attrib['x']),
                                               int(initial_state_element.attrib['y']))
        self.initial_hero_pos_dir = Direction[initial_state_element.attrib['dir']]
        self.initial_state_dialog = self.parse_dialog(initial_state_element)

        if not self.pc_name:
            self.pc_name = initial_state_element.attrib['name']
        self.pc_xp = int(initial_state_element.attrib['xp'])
        self.pc_gp = int(initial_state_element.attrib['gp'])
        self.pc_hp = None
        self.pc_mp = None
        if 'hp' in initial_state_element.attrib:
            self.pc_hp = int(initial_state_element.attrib['hp'])
        if 'mp' in initial_state_element.attrib:
            self.pc_mp = int(initial_state_element.attrib['mp'])
        self.pc_weapon: Optional[Weapon] = None
        self.pc_armor: Optional[Armor] = None
        self.pc_shield: Optional[Shield] = None
        self.pc_otherEquippedItems: List[Tool] = []
        for item_element in initial_state_element.findall("./EquippedItems/Item"):
            item_name = item_element.attrib['name']
            if item_name in self.weapons:
                self.pc_weapon = self.weapons[item_name]
            elif item_name in self.armors:
                self.pc_armor = self.armors[item_name]
            elif item_name in self.shields:
                self.pc_shield = self.shields[item_name]
            elif item_name in self.tools:
                self.pc_otherEquippedItems.append(self.tools[item_name])
            else:
                print('ERROR: Unsupported item', item_name, flush=True)
            
        self.pc_unequippedItems: Dict[ItemType, int] = {}
        for item_element in initial_state_element.findall("./UnequippedItems/Item"):
            item_name = item_element.attrib['name']
            item_count = 1
            if 'count' in item_element.attrib:
                item_count = int(item_element.attrib['count'])
            if item_name in self.items:
                self.pc_unequippedItems[self.items[item_name]] = item_count
            else:
                print('ERROR: Unsupported item', item_name, flush=True)

        self.pc_progressMarkers: List[str] = []
        for progress_marker_element in initial_state_element.findall("./ProgressMarkers/ProgressMarker"):
            self.pc_progressMarkers.append(progress_marker_element.attrib['name'])
            # print('Loaded progress marker ' + progressMarkerElement.attrib['name'], flush=True)
      
        self.initial_map_decorations: List[MapDecoration] = []
        for decoration_element in initial_state_element.findall("./MapDecoration"):
            decoration = None
            if 'type' in decoration_element.attrib and decoration_element.attrib['type'] in self.decorations:
                decoration = self.decorations[decoration_element.attrib['type']]
            self.initial_map_decorations.append(MapDecoration(
                decoration,
                Point(int(decoration_element.attrib['x']),
                      int(decoration_element.attrib['y'])),
                self.parse_dialog(decoration_element),
                None,
                None))

        # Parse death state
        death_state_element = xml_root.find('DeathState')
        if death_state_element is None:
            print('ERROR: DeathState element is missing', flush=True)
            raise Exception('Missing required DeathState element')
        self.death_map = death_state_element.attrib['map']
        self.death_hero_pos_dat_tile = Point(int(death_state_element.attrib['x']),
                                             int(death_state_element.attrib['y']))
        self.death_hero_pos_dir = Direction[death_state_element.attrib['dir']]
        self.death_dialog = self.parse_dialog(death_state_element)

    def parse_dialog(self, dialog_root_element: Optional[xml.etree.ElementTree.Element]) -> Optional[DialogType]:
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
                  
            map_name = None
            if 'map' in element.attrib:
                map_name = element.attrib['map']
            
            map_pos = None
            if 'x' in element.attrib and 'y' in element.attrib:
                map_pos = Point(int(element.attrib['x']), int(element.attrib['y']))
         
            map_dir = None
            if 'dir' in element.attrib:
                map_dir = Direction[element.attrib['dir']]
               
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

            elif element.tag == 'DialogAssert' or element.tag == 'DialogCheck':
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
                victory_dialog: Optional[DialogType] = None
                if 'victoryDialogScript' in element.attrib:
                    victory_dialog = [DialogGoTo(element.attrib['victoryDialogScript'])]

                run_away_dialog: Optional[DialogType] = None
                if 'runAwayDialogScript' in element.attrib:
                    run_away_dialog = [DialogGoTo(element.attrib['runAwayDialogScript'])]

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
                                           category=category,
                                           map_name=map_name,
                                           map_pos=map_pos,
                                           map_dir=map_dir,
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
                    for itemTypeElement in element.findall("./InventoryItemType"):
                        value_for_dialog_vendor_sell_options.append(itemTypeElement.attrib['type'])
                    dialog.append(DialogVendorSellOptionsVariable(name, value_for_dialog_vendor_sell_options))
                else:
                    dialog.append(DialogVariable(name, value))

        if len(dialog) > 0:
            return dialog
      
        return None

    def get_item(self, name: str) -> Optional[ItemType]:
        if name in self.items:
            return self.items[name]
        return None

    def get_map_image_info(self,
                           map_name: str,
                           image_pad_tiles: Point = Point(0, 0),
                           map_decorations: Optional[List[MapDecoration]] = None) -> MapImageInfo:
      
        # Determine the size of the map image then initialize
        # The size of the image is padded by imagePad_tiles in all directions
        map_image_size_tiles = self.maps[map_name].size + 2 * image_pad_tiles
        map_image_size_pixels = map_image_size_tiles * self.tile_size_pixels

        if map_decorations is None:
            map_decorations = self.maps[map_name].map_decorations
      
        map_image = self.get_map_image(
            map_name,
            image_pad_tiles,
            map_decorations,
            map_image_size_pixels,
            self.maps[map_name].dat,
            pygame.Color('pink'))  # Fill with a color to make is easier to identify any gaps

        overlay_dat = self.maps[map_name].overlay_dat
        if overlay_dat is not None:
            map_overlay_image = self.get_map_image(
                map_name,
                image_pad_tiles,
                [],
                map_image_size_pixels,
                overlay_dat,
                GameInfo.TRANSPARENT_COLOR)
            map_overlay_image.set_colorkey(GameInfo.TRANSPARENT_COLOR)
        else:
            map_overlay_image = None
         
        # Return the map image info
        return MapImageInfo(map_name, map_image, map_image_size_tiles, map_image_size_pixels, map_overlay_image)

    def get_map_image(self,
                      map_name: str,
                      image_pad_tiles: Point,
                      map_decorations: Optional[List[MapDecoration]],
                      map_image_size_pixels: Point,
                      dat: List[str],
                      fill_color: pygame.Color) -> pygame.Surface:
        map_image = pygame.Surface(map_image_size_pixels)
        map_image.fill(fill_color)

        # Blit the padded portions of the image
        import zlib
        numpy.random.seed(zlib.crc32(map_name.encode()) % (2**32 - 1))
        last_c = self.maps[map_name].size[0] - 1
        last_r = self.maps[map_name].size[1] - 1
        for x in range(int(image_pad_tiles.x)):
            x_w_px = int(x * self.tile_size_pixels)
            x_e_px = int((x + image_pad_tiles.x + self.maps[map_name].size[0]) * self.tile_size_pixels)
            for y in range(int(image_pad_tiles.y)):
                # Blit corners
                y_n_px = y * self.tile_size_pixels
                y_s_px = (y + image_pad_tiles.y + self.maps[map_name].size[1]) * self.tile_size_pixels
                # NW pad
                if dat[0][0] in self.tile_symbols:
                    map_image.blit(self.random_tile_image(dat[0][0]), (x_w_px, y_n_px))
                # NE pad
                if dat[0][last_c] in self.tile_symbols:
                    map_image.blit(self.random_tile_image(dat[0][last_c]), (x_e_px, y_n_px))
                # SW pad
                if dat[last_r][0] in self.tile_symbols:
                    map_image.blit(self.random_tile_image(dat[last_r][0]), (x_w_px, y_s_px))
                # SE pad
                if dat[last_r][last_c] in self.tile_symbols:
                    map_image.blit(self.random_tile_image(dat[last_r][last_c]), (x_e_px, y_s_px))
            for y in range(self.maps[map_name].size[1]):
                # Blit sides
                y_px = int((y + image_pad_tiles.y) * self.tile_size_pixels)
                # W pad
                if dat[y][0] in self.tile_symbols:
                    map_image.blit(self.random_tile_image(dat[y][0]), (x_w_px, y_px))
                # E pad
                if dat[y][last_c] in self.tile_symbols:
                    map_image.blit(self.random_tile_image(dat[y][last_c]), (x_e_px, y_px))
        for y in range(int(image_pad_tiles.y)):
            y_n_px = int(y * self.tile_size_pixels)
            y_s_px = int((y + image_pad_tiles.y + self.maps[map_name].size[1]) * self.tile_size_pixels)
            for x in range(self.maps[map_name].size[0]):
                # Blit the top and bottom
                x_px = int((x + image_pad_tiles.x) * self.tile_size_pixels)
                # N pad
                if dat[0][x] in self.tile_symbols:
                    map_image.blit(self.random_tile_image(dat[0][x]), (x_px, y_n_px))
                # S pad
                if dat[last_r][x] in self.tile_symbols:
                    map_image.blit(self.random_tile_image(dat[last_r][x]), (x_px, y_s_px))

        # Blit the map data portion of the image
        for y, row_data in enumerate(dat):
            y_px = int((y + image_pad_tiles.y) * self.tile_size_pixels)
            for x, tile_symbol in enumerate(row_data):
                if tile_symbol not in self.tile_symbols:
                    continue
                x_px = int((x + image_pad_tiles.x) * self.tile_size_pixels)
                # Determine which image to use
                image_idx = 0
                # TODO: Fix hardcoded exception for the bridge tile_symbol of 'b'
                if y > 0 and dat[y-1][x] != tile_symbol and dat[y-1][x] != 'b':
                    image_idx += 8
                if y < len(dat)-1 and dat[y+1][x] != tile_symbol and dat[y+1][x] != 'b':
                    image_idx += 2
                if x > 0 and row_data[x-1] != tile_symbol and row_data[x-1] != 'b':
                    image_idx += 1
                if x < len(row_data)-1 and row_data[x+1] != tile_symbol and row_data[x+1] != 'b':
                    image_idx += 4
                map_image.blit(self.random_tile_image(tile_symbol, image_idx), (x_px, y_px))

        # Blit the decoration on the image
        if map_decorations is not None:
            for map_decoration in map_decorations:
                if map_decoration.type is None:
                    continue
                tile_position_px = (map_decoration.point + image_pad_tiles) * self.tile_size_pixels
                x_px = int(tile_position_px.x + (self.tile_size_pixels - map_decoration.type.image.get_width()) / 2)
                y_px = int(tile_position_px.y + self.tile_size_pixels - map_decoration.type.image.get_height())
                map_image.blit(map_decoration.type.image, (x_px, y_px))

        return map_image

    def random_tile_image(self, symbol: str, idx: int = 0) -> pygame.Surface:
        images = self.tiles[self.tile_symbols[symbol]].images[idx]
        if 1 == len(images):
            return images[0]
        return numpy.random.choice(images, p=self.tile_probabilities[len(images)-1])

    @staticmethod
    def get_exterior_image(map_image_info: MapImageInfo) -> pygame.Surface:
        map_image = map_image_info.image.copy()
        if map_image_info.overlay_image is not None:
            map_image.blit(map_image_info.overlay_image, (0, 0))
        return map_image

    @staticmethod
    def get_interior_image(map_image_info: MapImageInfo) -> pygame.Surface:
        map_image = None
        if map_image_info.overlay_image is not None:
            map_image = map_image_info.image.copy()
            pygame.transform.threshold(map_image,
                                       map_image_info.overlay_image,
                                       search_color=GameInfo.TRANSPARENT_COLOR,
                                       set_color=pygame.Color('black'),
                                       inverse_set=True)
        return map_image


def main() -> None:

    import SurfaceEffects

    # Initialize pygame
    pygame.init()
    audio_player = AudioPlayer()

    # Setup to draw maps
    win_size_pixels = Point(1280, 960)
    tile_size_pixels = 16
    win_size_tiles = (win_size_pixels / tile_size_pixels).ceil()
    image_pad_tiles = win_size_tiles // 2
    win_size_pixels = win_size_tiles * tile_size_pixels
    screen = pygame.display.set_mode(win_size_pixels, pygame.SRCALPHA | pygame.HWSURFACE)
    clock = pygame.time.Clock()
   
    # Initialize GameInfo
    base_path = os.path.split(os.path.abspath(__file__))[0]
    game_xml_path = os.path.join(base_path, 'game.xml')
    game_info = GameInfo(base_path, game_xml_path, tile_size_pixels)
   
    # Iterate through and render the different maps
    is_running = True
    for map_name in game_info.maps:
        audio_player.play_music(game_info.maps[map_name].music)
        map_image_info = game_info.get_map_image_info(map_name, image_pad_tiles)

        render_types = ['exterior']
        if map_image_info.overlay_image is not None:
            render_types.append('interior')

        for render_type in render_types:
            if render_type == 'exterior':
                map_image = GameInfo.get_exterior_image(map_image_info)
            else:
                map_image = GameInfo.get_interior_image(map_image_info)
            
            # Always rendering to the entire window but need to determine the
            # rectangle from the image which is to be scaled to the screen
            map_image_rect = pygame.Rect(0, 0, win_size_pixels.x, win_size_pixels.y)
            screen.set_clip(pygame.Rect(0, 0, win_size_pixels.x, win_size_pixels.y))
            screen.blit(map_image.subsurface(map_image_rect), (0, 0))
            pygame.display.flip()

            pygame.key.set_repeat(10, 10)

            done_with_map = False
            while is_running and not done_with_map:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            is_running = False
                        elif event.key == pygame.K_RETURN:
                            done_with_map = True
                        elif event.key == pygame.K_DOWN:
                            SurfaceEffects.scroll_view(
                                screen, map_image, Direction.SOUTH, map_image_rect, 1, tile_size_pixels, True)
                        elif event.key == pygame.K_UP:
                            SurfaceEffects.scroll_view(
                                screen, map_image, Direction.NORTH, map_image_rect, 1, tile_size_pixels, True)
                        elif event.key == pygame.K_LEFT:
                            SurfaceEffects.scroll_view(
                                screen, map_image, Direction.WEST,  map_image_rect, 1, tile_size_pixels, True)
                        elif event.key == pygame.K_RIGHT:
                            SurfaceEffects.scroll_view(
                                screen, map_image, Direction.EAST,  map_image_rect, 1, tile_size_pixels, True)
                    elif event.type == pygame.QUIT:
                        is_running = False
                    else:
                        print('event.type =', event.type, flush=True)
                clock.tick(30)

    # Terminate pygame
    audio_player.terminate()
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
