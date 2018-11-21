#!/usr/bin/env python

import os
import xml.etree.ElementTree
import xml.dom.minidom
import random

import pygame

# from CombatEncounter import CombatEncounter
# from GameDialog import GameDialog
from GameTypes import *
from GameInfo import GameInfo
from MapCharacterState import MapCharacterState
from HeroParty import HeroParty
from HeroState import HeroState
from NpcState import NpcState


class GameState:
    PHASE_TICKS = 20
    NPC_MOVE_STEPS = 60

    def __init__(self,
                 base_path: str,
                 game_xml_path: str,
                 desired_win_size_pixels: Optional[Point],
                 tile_size_pixels: int,
                 saved_game_file: Optional[str] = None) -> None:

        if desired_win_size_pixels is None:
            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.HWSURFACE)
            win_size_pixels = Point(self.screen.get_size())
            self.win_size_tiles = (win_size_pixels / tile_size_pixels).floor()
        else:
            self.win_size_tiles = (desired_win_size_pixels / tile_size_pixels).floor()

        self.image_pad_tiles = self.win_size_tiles // 2
        self.win_size_pixels = self.win_size_tiles * tile_size_pixels

        if desired_win_size_pixels is not None:
            self.screen = pygame.display.set_mode(
                self.win_size_pixels,
                pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.HWSURFACE)

        self.is_running = True
        self.phase = Phase.A
        self.tick_count = 1
        self.game_info = GameInfo(base_path, game_xml_path, tile_size_pixels, saved_game_file)
        self.removed_decorations_by_map: Dict[str, List[MapDecoration]] = {}

        # Set character state for new game
        self.pending_dialog = self.game_info.initial_state_dialog
        pc = HeroState('hero_sword_and_shield',
                       self.game_info.initial_hero_pos_dat_tile,
                       self.game_info.initial_hero_pos_dir,
                       self.game_info.pc_name,
                       HeroState.calc_level(self.game_info.levels, self.game_info.pc_xp))
        pc.xp = self.game_info.pc_xp
        pc.gp = self.game_info.pc_gp
        if self.game_info.pc_hp is not None and self.game_info.pc_hp < pc.hp:
            pc.hp = self.game_info.pc_hp
        if self.game_info.pc_mp is not None and self.game_info.pc_mp < pc.mp:
            pc.mp = self.game_info.pc_mp
        pc.weapon = self.game_info.pc_weapon
        pc.armor = self.game_info.pc_armor
        pc.shield = self.game_info.pc_shield
        pc.other_equipped_items = self.game_info.pc_otherEquippedItems
        pc.unequipped_items = self.game_info.pc_unequippedItems
        pc.progress_markers = self.game_info.pc_progressMarkers
        self.hero_party = HeroParty(pc)

        # TODO: Remove Mocha from party
        mocha = HeroState('mocha',
                          self.game_info.initial_hero_pos_dat_tile,
                          self.game_info.initial_hero_pos_dir,
                          'Mocha',
                          self.game_info.levels[0])
        self.hero_party.add_member(mocha)

        self.map_decorations: List[MapDecoration] = []
        self.npcs: List[NpcState] = []
        self.light_diameter: Optional[float] = None  # None indicates the light diameter is unlimited

        # map_state, exterior_map_image, and interior_map_image are initialized with meaningful values in set_map
        self.map_state = MapImageInfo.create_null()
        self.exterior_map_image = self.interior_map_image = pygame.Surface((0, 0))
        self.set_map(self.game_info.initial_map, self.game_info.initial_map_decorations)

        # TODO: Migrate these to here
        # self.message_dialog: Optional[GameDialog] = None
        # self.combat_encounter: Optional[CombatEncounter] = None

    def set_map(self,
                new_map_name: str,
                one_time_decorations: Optional[List[MapDecoration]] = None,
                respawn_decorations: bool = False) -> None:
        # print( 'setMap to', newMapName, flush=True )
        old_map_name = None
        try:
            old_map_name = self.map_state.name
        except:
            pass

        # Set light diameter for the new map if there was not an old map or if the new default map
        # diameter is unlimited.  Also update the light diameter for the new map if the default light
        # diameters between the old and new maps are different and either the old map default light
        # diameters was unlimited or the current diameter is less than the default light diameter of the
        # new map.
        new_map_light_diameter = self.game_info.maps[new_map_name].light_diameter
        if (old_map_name is None or new_map_light_diameter is None or
                (new_map_light_diameter != self.game_info.maps[old_map_name].light_diameter
                 and (self.game_info.maps[old_map_name].light_diameter is None
                      or (self.light_diameter is not None
                          and self.light_diameter < new_map_light_diameter)))):
            self.light_diameter = new_map_light_diameter

        # If changing maps and set to respawn decorations, clear the history of removed decorations
        if respawn_decorations:
            self.removed_decorations_by_map = {}

        self.map_decorations = self.game_info.maps[new_map_name].map_decorations
        if one_time_decorations is not None:
            self.map_decorations += one_time_decorations
        # Prune out decorations where the progress marker conditions are not met
        for decoration in self.map_decorations[:]:
            if (decoration.progress_marker is not None
                    and decoration.progress_marker not in self.hero_party.progress_markers):
                self.map_decorations.remove(decoration)
            elif (decoration.inverse_progress_marker is not None
                  and decoration.inverse_progress_marker in self.hero_party.progress_markers):
                self.map_decorations.remove(decoration)
        # Prune out previously removed decorations
        if new_map_name in self.removed_decorations_by_map:
            for decoration in self.removed_decorations_by_map[new_map_name]:
                if decoration in self.map_decorations:
                    self.map_decorations.remove(decoration)
        self.map_state = self.game_info.get_map_image_info(new_map_name, self.image_pad_tiles, self.map_decorations)

        if old_map_name == new_map_name:
            # If loading up the same map, should retain the NPC positions

            # Remove any current NPCs which should be missing
            for npc_char in self.npcs[:]:
                if (npc_char.npc_info is not None
                        and npc_char.npc_info.progress_marker is not None
                        and npc_char.npc_info.progress_marker not in self.hero_party.progress_markers):
                    self.npcs.remove(npc_char)
                elif (npc_char.npc_info is not None
                      and npc_char.npc_info.inverse_progress_marker is not None
                      and npc_char.npc_info.inverse_progress_marker in self.hero_party.progress_markers):
                    self.npcs.remove(npc_char)

            # Add missing NPCs
            for npc in self.game_info.maps[new_map_name].npcs:
                if npc.progress_marker is not None and npc.progress_marker not in self.hero_party.progress_markers:
                    continue
                if (npc.inverse_progress_marker is not None
                        and npc.inverse_progress_marker in self.hero_party.progress_markers):
                    continue
                is_missing = True
                for npc_char in self.npcs:
                    if npc_char.npc_info is not None and npc == npc_char.npc_info:
                        is_missing = False
                        break
                if is_missing:
                    self.npcs.append(NpcState(npc))
        else:
            # On a map change load NPCs from scratch
            self.npcs = []
            for npc in self.game_info.maps[new_map_name].npcs:
                if npc.progress_marker is not None and npc.progress_marker not in self.hero_party.progress_markers:
                    continue
                if (npc.inverse_progress_marker is not None
                        and npc.inverse_progress_marker in self.hero_party.progress_markers):
                    continue
                self.npcs.append(NpcState(npc))

        # Bounds checking to ensure a valid hero/center position
        self.bounds_check_pc_position()

        # Get exterior and interior map images
        self.exterior_map_image = GameInfo.get_exterior_image(self.map_state)
        self.interior_map_image = GameInfo.get_interior_image(self.map_state)

    def save(self) -> None:
        # TODO: Save data for multiple party members
        xml_root = xml.etree.ElementTree.Element('SaveState')
        xml_root.attrib['name'] = self.hero_party.main_character.name
        xml_root.attrib['map'] = self.map_state.name
        xml_root.attrib['x'] = str(self.hero_party.main_character.curr_pos_dat_tile.x)
        xml_root.attrib['y'] = str(self.hero_party.main_character.curr_pos_dat_tile.y)
        xml_root.attrib['dir'] = self.hero_party.main_character.direction.name
        xml_root.attrib['xp'] = str(self.hero_party.main_character.xp)
        xml_root.attrib['gp'] = str(self.hero_party.gp)
        xml_root.attrib['hp'] = str(self.hero_party.main_character.hp)
        xml_root.attrib['mp'] = str(self.hero_party.main_character.mp)

        items_element = xml.etree.ElementTree.SubElement(xml_root, 'EquippedItems')
        if self.hero_party.main_character.weapon is not None:
            item_element = xml.etree.ElementTree.SubElement(items_element, 'Item')
            item_element.attrib['name'] = self.hero_party.main_character.weapon.name
        if self.hero_party.main_character.armor is not None:
            item_element = xml.etree.ElementTree.SubElement(items_element, 'Item')
            item_element.attrib['name'] = self.hero_party.main_character.armor.name
        if self.hero_party.main_character.shield is not None:
            item_element = xml.etree.ElementTree.SubElement(items_element, 'Item')
            item_element.attrib['name'] = self.hero_party.main_character.shield.name
        for tool in self.hero_party.main_character.other_equipped_items:
            item_element = xml.etree.ElementTree.SubElement(items_element, 'Item')
            item_element.attrib['name'] = tool.name

        items_element = xml.etree.ElementTree.SubElement(xml_root, 'UnequippedItems')
        for item in self.hero_party.main_character.unequipped_items:
            if self.hero_party.main_character.unequipped_items[item] > 0:
                item_element = xml.etree.ElementTree.SubElement(items_element, 'Item')
                item_element.attrib['name'] = item.name
                item_element.attrib['count'] = str(self.hero_party.main_character.unequipped_items[item])

        progress_markers_element = xml.etree.ElementTree.SubElement(xml_root, 'ProgressMarkers')
        for progress_marker in self.hero_party.progress_markers:
            progress_marker_element = xml.etree.ElementTree.SubElement(progress_markers_element, 'ProgressMarker')
            progress_marker_element.attrib['name'] = progress_marker

        dialog_element = xml.etree.ElementTree.SubElement(xml_root, 'Dialog')
        dialog_element.text = '"I am glad thou hast returned.  All our hopes are riding on thee."'
        dialog_element = xml.etree.ElementTree.SubElement(xml_root, 'Dialog')
        dialog_element.text = '"Before reaching thy next level of experience thou must gain [NEXT_LEVEL_XP] ' \
                              'experience points.  See me again when thy level has increased."'
        dialog_element = xml.etree.ElementTree.SubElement(xml_root, 'Dialog')
        dialog_element.text = '"Goodbye now, [NAME].  Take care and tempt not the Fates."'

        xml_string = xml.dom.minidom.parseString(xml.etree.ElementTree.tostring(xml_root)).toprettyxml(indent="   ")

        save_game_file_path = os.path.join(self.game_info.saves_path, self.hero_party.main_character.name + '.xml')
        save_game_file = open(save_game_file_path, 'w')
        save_game_file.write(xml_string)
        save_game_file.close()

    def get_castable_combat_spell_names(self) -> List[str]:  # TODO: This should be a method in HeroState
        return self.game_info.get_castable_spell_names(
            True,
            self.hero_party.main_character.level,
            self.hero_party.main_character.mp,
            self.map_state.name)

    def get_castable_non_combat_spell_names(self) -> List[str]:  # TODO: This should be a method in HeroState
        return self.game_info.get_castable_spell_names(
            False,
            self.hero_party.main_character.level,
            self.hero_party.main_character.mp,
            self.map_state.name)

    def get_available_spell_names(self) -> List[str]:  # TODO: This should be a method in HeroState
        return self.game_info.get_available_spell_names(self.hero_party.main_character.level)

    def get_map_image_rect(self) -> pygame.Rect:
        # Always rendering to the entire screen but need to determine the
        # rectangle from the image which is to be scaled to the screen
        curr_pos_dat_tile = self.hero_party.get_curr_pos_dat_tile()
        curr_pos_offset_img_px = self.hero_party.get_curr_pos_offset_img_px()
        return pygame.Rect(
            (self.image_pad_tiles[0] + curr_pos_dat_tile[0] - self.win_size_tiles[
                0] / 2 + 0.5) * self.game_info.tile_size_pixels + curr_pos_offset_img_px.x,
            (self.image_pad_tiles[1] + curr_pos_dat_tile[1] - self.win_size_tiles[
                1] / 2 + 0.5) * self.game_info.tile_size_pixels + curr_pos_offset_img_px.y,
            self.win_size_pixels[0],
            self.win_size_pixels[1])

    def get_tile_image_rect(self,
                            tile: Point,
                            offset: Point = Point(0, 0)) -> pygame.Rect:
        return self.get_tile_region_image_rect(tile, 0.5, offset)

    def get_tile_region_image_rect(self,
                                   center_tile: Point,
                                   tile_radius: float,
                                   offset: Point = Point(0, 0)) -> pygame.Rect:
        return pygame.Rect(
            (self.image_pad_tiles[0] + center_tile[0] + 0.5 - tile_radius) * self.game_info.tile_size_pixels + offset.x,
            (self.image_pad_tiles[1] + center_tile[1] + 0.5 - tile_radius) * self.game_info.tile_size_pixels + offset.y,
            (2 * tile_radius) * self.game_info.tile_size_pixels,
            (2 * tile_radius) * self.game_info.tile_size_pixels)

    def get_tile_screen_rect(self,
                             tile: Point,
                             offset: Point = Point(0, 0)) -> pygame.Rect:
        return self.get_tile_region_screen_rect(tile, 0.5, offset)

    def get_tile_region_screen_rect(self,
                                    center_tile: Point,
                                    tile_radius: float,
                                    offset: Point = Point(0, 0)) -> pygame.Rect:
        # Hero is always in the center of the screen
        curr_pos_dat_tile = self.hero_party.get_curr_pos_dat_tile()
        curr_pos_offset_img_px = self.hero_party.get_curr_pos_offset_img_px()
        return pygame.Rect(
            (self.win_size_tiles[0] / 2 + center_tile[0] - curr_pos_dat_tile[
                0] - tile_radius) * self.game_info.tile_size_pixels + offset.x - curr_pos_offset_img_px.x,
            (self.win_size_tiles[1] / 2 + center_tile[1] - curr_pos_dat_tile[
                1] - tile_radius) * self.game_info.tile_size_pixels + offset.y - curr_pos_offset_img_px.y,
            (2 * tile_radius) * self.game_info.tile_size_pixels,
            (2 * tile_radius) * self.game_info.tile_size_pixels)

    def get_tile_info(self, tile: Optional[Point]) -> Tile:
        if tile is None:
            tile = self.hero_party.main_character.curr_pos_dat_tile
        return self.game_info.tiles[
            self.game_info.tile_symbols[self.game_info.maps[self.map_state.name].dat[int(tile.y)][int(tile.x)]]]

    def get_point_transition(self, tile: Optional[Point] = None) -> Optional[PointTransition]:
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for pointTransition in self.game_info.maps[self.map_state.name].point_transitions:
            if pointTransition.src_point == tile:
                if (pointTransition.progress_marker is not None
                        and pointTransition.progress_marker not in self.hero_party.progress_markers):
                    continue
                if (pointTransition.inverse_progress_marker is not None
                        and pointTransition.inverse_progress_marker in self.hero_party.progress_markers):
                    continue
                # print ('Found transition at point: ', tile, flush=True)
                return pointTransition
        return None

    def get_decorations(self, tile: Optional[Point] = None) -> List[MapDecoration]:
        decorations = []
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for decoration in self.map_decorations:
            if decoration.point == tile:
                if (decoration.progress_marker is not None
                        and decoration.progress_marker not in self.hero_party.progress_markers):
                    continue
                if (decoration.inverse_progress_marker is not None
                        and decoration.inverse_progress_marker in self.hero_party.progress_markers):
                    continue
                # print ('Found decoration at point: ', tile, flush=True)
                decorations.append(decoration)
        return decorations

    def get_special_monster(self, tile: Optional[Point] = None) -> Optional[SpecialMonster]:
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for specialMonster in self.game_info.maps[self.map_state.name].special_monsters:
            if specialMonster.point == tile:
                if (specialMonster.progress_marker is not None
                        and specialMonster.progress_marker not in self.hero_party.progress_markers):
                    continue
                if (specialMonster.inverse_progress_marker is not None
                        and specialMonster.inverse_progress_marker in self.hero_party.progress_markers):
                    continue
                # print ('Found monster at point: ', tile, flush=True)
                return specialMonster
        return None

    def get_tile_degrees_of_freedom(self,
                                    tile: Point,
                                    enforce_npc_hp_penalty_limit: bool,
                                    prev_tile: Optional[Point]) -> int:
        degrees_of_freedom = 0
        for x in [tile.x - 1, tile.x + 1]:
            if self.can_move_to_tile(Point(x, tile.y), enforce_npc_hp_penalty_limit, False, True, prev_tile):
                degrees_of_freedom += 1
        for y in [tile.y - 1, tile.y + 1]:
            if self.can_move_to_tile(Point(tile.x, y), enforce_npc_hp_penalty_limit, False, True, prev_tile):
                degrees_of_freedom += 1
        # print('DOF for tile', tile, 'is', degrees_of_freedom, flush=True)
        return degrees_of_freedom

    def can_move_to_tile(self,
                         tile: Point,
                         enforce_npc_hp_penalty_limit: bool = False,
                         enforce_npc_dof_limit: bool = False,
                         is_npc: bool = False,
                         prev_tile: Optional[Point] = None) -> bool:
        movement_allowed = False

        # Check if native tile allows movement
        if (0 <= tile.x < self.game_info.maps[self.map_state.name].size.w
                and 0 <= tile.y < self.game_info.maps[self.map_state.name].size.h
                and self.get_tile_info(tile).walkable):
            movement_allowed = True

        # Check if decoration changes the allowed movement of the native tile
        if movement_allowed:
            for decoration in self.map_decorations:
                if (tile == decoration.point
                        and decoration.type is not None
                        and not self.game_info.decorations[decoration.type].walkable):
                    movement_allowed = False
                    # print('Movement not allowed: decoration not walkable', decoration, flush=True)
                    break
        else:
            for decoration in self.map_decorations:
                if (tile == decoration.point
                        and decoration.type is not None
                        and self.game_info.decorations[decoration.type].walkable):
                    movement_allowed = True
                    # print('Movement allowed: decoration walkable', decoration, flush=True)
                    break

        if movement_allowed:
            if movement_allowed and enforce_npc_hp_penalty_limit and self.get_tile_info(tile).hp_penalty != 0:
                movement_allowed = False
                # print('Movement not allowed: NPC HP penalty limited', flush=True)
            if movement_allowed and enforce_npc_hp_penalty_limit and prev_tile is not None and self.is_interior(
                    tile) != self.is_interior(prev_tile):
                movement_allowed = False
                # print('Movement not allowed: NPC cannot move between interior and exterior tiles', flush=True)
            if (movement_allowed
                    and enforce_npc_dof_limit
                    and self.get_tile_degrees_of_freedom(tile, enforce_npc_hp_penalty_limit, prev_tile) < 2):
                movement_allowed = False
                # print('Movement not allowed: NPC degree-of-freedom limit not met', flush=True)
            if movement_allowed and is_npc:
                for hero in self.hero_party.members:
                    if tile == hero.curr_pos_dat_tile or tile == hero.dest_pos_dat_tile:
                        movement_allowed = False
                        # print('Movement not allowed: PC in the way', flush=True)
                        break
            if movement_allowed:
                for npc in self.npcs:
                    if tile == npc.curr_pos_dat_tile or tile == npc.dest_pos_dat_tile:
                        movement_allowed = False
                        # print('Movement not allowed: NPC in the way', flush=True)
                        break
        # else:
        #   print('Movement not allowed: tile not walkable', flush=True)

        return movement_allowed

    def get_tile_monsters(self, tile: Optional[Point] = None) -> List[str]:
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for mz in self.game_info.maps[self.map_state.name].monster_zones:
            if mz.x <= tile.x <= mz.x + mz.w and mz.y <= tile.y <= mz.y + mz.h:
                # print('in monsterZone of set ' + mz.setName + ':', self.gameInfo.monsterSets[mz.setName], flush=True)
                return self.game_info.monster_sets[mz.name]
        return []

    def erase_characters(self) -> None:
        # Erase PCs
        for hero in self.hero_party.members:
            self.erase_character(hero)

        # Erase NPCs
        for npc in self.npcs:
            self.erase_character(npc)

    def erase_character(self, character: MapCharacterState) -> None:
        pc = self.hero_party.members[0]
        if character == pc or self.is_interior(pc.curr_pos_dat_tile) == self.is_interior(character.curr_pos_dat_tile):
            self.screen.blit(
                self.get_map_image().subsurface(
                    self.get_tile_image_rect(
                        character.curr_pos_dat_tile,
                        character.curr_pos_offset_img_px)),
                self.get_tile_screen_rect(
                    character.curr_pos_dat_tile,
                    character.curr_pos_offset_img_px))

    def draw_characters(self) -> None:
        # Draw PCs
        for hero in reversed(self.hero_party.members):
            self.draw_character(hero)

        # Draw NPCs
        for npc in self.npcs:
            self.draw_character(npc)

    def draw_character(self, character: MapCharacterState) -> None:
        pc = self.hero_party.members[0]
        if character == pc or self.is_interior(pc.curr_pos_dat_tile) == self.is_interior(
                character.curr_pos_dat_tile):
            if character == self.hero_party.main_character:
                # TODO: Configurable way to handle the PC image mappings
                if self.hero_party.main_character.has_item('PM_Carrying_Princess'):
                    character_images = self.game_info.character_types['hero_carrying_princess'].images
                elif (self.hero_party.main_character.weapon is not None
                      and self.hero_party.main_character.shield is not None):
                    character_images = self.game_info.character_types['hero_sword_and_shield'].images
                elif self.hero_party.main_character.weapon is not None:
                    character_images = self.game_info.character_types['hero_sword'].images
                elif self.hero_party.main_character.shield is not None:
                    character_images = self.game_info.character_types['hero_shield'].images
                else:
                    character_images = self.game_info.character_types['hero'].images
            else:
                character_images = self.game_info.character_types[character.type_name].images
            self.screen.blit(
                character_images[character.direction][self.phase],
                self.get_tile_screen_rect(
                    character.curr_pos_dat_tile,
                    character.curr_pos_offset_img_px))
        if character == pc and self.is_exterior(pc.curr_pos_dat_tile) and self.is_interior(pc.dest_pos_dat_tile):
            # If moving inside should disappear as moving
            self.screen.blit(
                self.exterior_map_image.subsurface(self.get_tile_image_rect(pc.dest_pos_dat_tile)),
                self.get_tile_screen_rect(pc.dest_pos_dat_tile))

    def is_light_restricted(self) -> bool:
        return (self.light_diameter is not None
                and self.light_diameter <= self.win_size_tiles.w
                and self.light_diameter <= self.win_size_tiles.h)

    def is_outside(self) -> bool:
        return self.game_info.maps[self.map_state.name].is_outside

    def make_map_transition(self,
                            transition: Optional[Union[LeavingTransition, PointTransition]]) -> bool:
        if transition is not None:
            self.hero_party.set_pos(transition.dest_point, transition.dest_dir)
            map_changing = transition.dest_map != self.map_state.name
            self.set_map(transition.dest_map, respawn_decorations=transition.respawn_decorations)
            if not map_changing:
                self.draw_map(True)
        return transition is not None

    def bounds_check_pc_position(self) -> None:
        # Bounds checking to ensure a valid hero/center position
        curr_pos_dat_tile = self.hero_party.get_curr_pos_dat_tile()
        if (curr_pos_dat_tile is None
                or curr_pos_dat_tile[0] < 1
                or curr_pos_dat_tile[0] < 1
                or curr_pos_dat_tile[0] > self.game_info.maps[self.map_state.name].size[0] - 1
                or curr_pos_dat_tile[1] > self.game_info.maps[self.map_state.name].size[1] - 1):
            print('ERROR: Invalid hero position, defaulting to middle tile', flush=True)
            self.hero_party.set_pos(Point(self.game_info.maps[self.map_state.name].size[0] // 2,
                                          self.game_info.maps[self.map_state.name].size[1] // 2),
                                    Direction.SOUTH)

    def is_interior(self, pos_dat_tile: Point) -> bool:
        overlay_dat = self.game_info.maps[self.map_state.name].overlay_dat
        return (overlay_dat is not None
                and overlay_dat[int(pos_dat_tile.y)][int(pos_dat_tile.x)] in self.game_info.tile_symbols)

    def is_exterior(self, pos_dat_tile: Point) -> bool:
        return not self.is_interior(pos_dat_tile)

    def get_map_image(self) -> pygame.Surface:
        if self.is_interior(self.hero_party.get_curr_pos_dat_tile()):
            return self.interior_map_image
        return self.exterior_map_image

    def is_facing_door(self) -> bool:
        door_open_dest_dat_tile = self.hero_party.get_curr_pos_dat_tile() \
                                  + self.hero_party.get_direction().get_vector()
        for decoration in self.map_decorations:
            if (door_open_dest_dat_tile == decoration.point
                    and decoration.type is not None
                    and self.game_info.decorations[decoration.type].removeWithKey):
                return True
        return False

    def open_door(self) -> None:
        door_open_dest_dat_tile = self.hero_party.get_curr_pos_dat_tile() \
                                  + self.hero_party.get_direction().get_vector()
        for decoration in self.map_decorations:
            if (door_open_dest_dat_tile == decoration.point
                    and decoration.type is not None
                    and self.game_info.decorations[decoration.type].removeWithKey):
                self.remove_decoration(decoration)

    def remove_decoration(self, decoration: MapDecoration) -> None:
        # Remove the decoration from the map (if present)
        if decoration in self.map_decorations:
            self.map_decorations.remove(decoration)
            if self.map_state.name not in self.removed_decorations_by_map:
                self.removed_decorations_by_map[self.map_state.name] = []
            self.removed_decorations_by_map[self.map_state.name].append(decoration)
            self.map_state = self.game_info.get_map_image_info(self.map_state.name,
                                                               self.image_pad_tiles,
                                                               self.map_decorations)

            # Get exterior and interior map images
            self.exterior_map_image = GameInfo.get_exterior_image(self.map_state)
            self.interior_map_image = GameInfo.get_interior_image(self.map_state)

            # Draw the map to the screen
            self.draw_map()

    def set_clipping_for_light_diameter(self) -> None:
        # TODO: Rework for parties
        if self.is_light_restricted() and self.light_diameter is not None:
            self.screen.set_clip(
                self.get_tile_region_screen_rect(
                    self.hero_party.get_curr_pos_dat_tile(),
                    self.light_diameter / 2,
                    self.hero_party.get_curr_pos_offset_img_px()))
        else:
            self.set_clipping_for_window()

    def set_clipping_for_window(self) -> None:
        self.screen.set_clip(pygame.Rect(0,
                                         0,
                                         self.win_size_pixels.x,
                                         self.win_size_pixels.y))

    def draw_map(self, flip_buffer: bool = True) -> None:
        # Implement light diameter via clipping
        if self.is_light_restricted():
            self.screen.fill(pygame.Color('black'))
        self.set_clipping_for_light_diameter()

        # Draw the map to the screen
        self.screen.blit(self.get_map_image().subsurface(self.get_map_image_rect()), (0, 0))

        # Draw the hero and NPCs to the screen
        self.draw_characters()

        # Restore clipping for entire window
        self.set_clipping_for_window()

        # Flip the screen buffer
        if flip_buffer:
            pygame.display.flip()

    def advance_tick(self, characters_erased: bool = False) -> None:
        phase_changed = False
        if self.tick_count % GameState.PHASE_TICKS == 0:
            phase_changed = True
            if self.phase == Phase.A:
                self.phase = Phase.B
            else:
                self.phase = Phase.A

        # Implement light diameter via clipping
        self.set_clipping_for_light_diameter()

        if phase_changed and not characters_erased:
            characters_erased = True
            self.erase_characters()

        redraw_map = False
        draw_all_characters = characters_erased

        # Move NPCs
        # NOTE: tile_size_pixels must be divisible by image_px_step_size
        image_px_step_size = self.game_info.tile_size_pixels // 8
        for npc in self.npcs:
            if npc.npc_info is None:
                continue

            if npc.npc_info.walking:

                # Start moving NPC by setting a destination tile
                if self.tick_count % GameState.NPC_MOVE_STEPS == 0:
                    # TODO: Determine where to move instead of blindly moving forward
                    npc.direction = random.choice(list(Direction))
                    dest_tile = npc.curr_pos_dat_tile + npc.direction.get_vector()
                    if self.can_move_to_tile(dest_tile, True, True, True, npc.curr_pos_dat_tile):
                        npc.dest_pos_dat_tile = dest_tile

                # Move the NPC in steps to the destination tile
                if npc.curr_pos_dat_tile != npc.dest_pos_dat_tile:
                    if not characters_erased:
                        self.erase_character(npc)
                    direction_vector = npc.direction.get_vector()
                    npc.curr_pos_offset_img_px += direction_vector * image_px_step_size
                    if npc.curr_pos_offset_img_px / self.game_info.tile_size_pixels == direction_vector:
                        npc.curr_pos_dat_tile = npc.dest_pos_dat_tile
                        npc.curr_pos_offset_img_px = Point(0, 0)
                    if not draw_all_characters:
                        self.draw_character(npc)
                        redraw_map = True

            elif npc.direction != npc.npc_info.direction:
                # Stationary characters should resume looking in the default
                # direction after talking to the player
                self.erase_character(npc)
                npc.direction = npc.npc_info.direction
                self.draw_character(npc)

        if draw_all_characters:
            self.draw_characters()
            redraw_map = True

        # Restore clipping for entire window
        self.set_clipping_for_window()

        if redraw_map:
            pygame.display.flip()

        self.tick_count += 1
        pygame.time.Clock().tick(40)


def main() -> None:
    print('Not implemented', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
