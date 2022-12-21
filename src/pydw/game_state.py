#!/usr/bin/env python

from typing import Dict, List, Optional

import os
import pygame
import random
import xml.etree.ElementTree as ET
import xml.dom.minidom

from generic_utils.point import Point

from pygame_utils.audio_player import AudioPlayer
import pygame_utils.game_events as GameEvents

from pydw.combat_encounter import CombatEncounter
from pydw.game_dialog import GameDialog
from pydw.game_dialog_evaluator import GameDialogEvaluator
from pydw.game_types import (
    DialogReplacementVariables,
    DialogType,
    Direction,
    EncounterBackground,
    MapDecoration,
    MonsterInfo,
    OutgoingTransition,
    SpecialMonster,
    Tile,
)
from pydw.game_info import GameInfo
from pydw.game_map import GameMap
from pydw.game_state_interface import GameStateInterface
from pydw.hero_party import HeroParty
from pydw.hero_state import HeroState
from pydw.map_character_state import MapCharacterState
from pydw.monster_party import MonsterParty
from pydw.monster_state import MonsterState
from pydw.npc_state import NpcState


class GameState(GameStateInterface):
    game_map: GameMap

    def __init__(
        self,
        saves_path: str,
        base_path: str,
        game_xml_path: str,
        win_size_tiles: Point,
        tile_size_pixels: int,
    ) -> None:
        self.saves_path = saves_path
        self.win_size_tiles = win_size_tiles
        self.image_pad_tiles = self.win_size_tiles // 2
        self.win_size_pixels = self.win_size_tiles * tile_size_pixels
        self.__should_add_math_problems_in_combat = True

        super().__init__(pygame.display.get_surface())

        self.game_info = GameInfo(
            base_path, game_xml_path, tile_size_pixels, self.win_size_pixels
        )
        self.removed_decorations_by_map: Dict[str, List[MapDecoration]] = {}

        self.pending_dialog: Optional[DialogType] = None
        self.load()

        self.clock = pygame.time.Clock()
        self.tick_count = 0

        # TODO: Migrate these to here
        # self.message_dialog: Optional[GameDialog] = None
        self.combat_encounter: Optional[CombatEncounter] = None

    def set_map(
        self,
        new_map_name: str,
        one_time_decorations: Optional[List[MapDecoration]] = None,
        respawn_decorations: bool = False,
        init: bool = False,
    ) -> None:
        # print('setMap to', new_map_name, flush=True)
        old_map_name = ""
        if not init:
            old_map_name = self.get_map_name()

        # Set light diameter for the new map if there was not an old map or if the new default map
        # diameter is unlimited.  Also update the light diameter for the new map if the default light
        # diameters between the old and new maps are different and either the old map default light
        # diameters was unlimited or the current diameter is less than the default light diameter of the
        # new map.
        new_map_light_diameter = self.game_info.maps[new_map_name].light_diameter
        if (
            not old_map_name
            or new_map_light_diameter is None
            or (
                new_map_light_diameter
                != self.game_info.maps[old_map_name].light_diameter
                and (
                    self.game_info.maps[old_map_name].light_diameter is None
                    or (
                        self.hero_party.light_diameter is not None
                        and self.hero_party.light_diameter < new_map_light_diameter
                    )
                )
            )
        ):
            self.hero_party.light_diameter = new_map_light_diameter

        # If changing maps and set to respawn decorations, clear the history of removed decorations
        if respawn_decorations:
            self.removed_decorations_by_map = {}

        map_decorations = self.game_info.maps[new_map_name].map_decorations.copy()
        removed_map_decorations: List[MapDecoration] = []
        if one_time_decorations is not None:
            map_decorations += one_time_decorations
        # Prune out decorations where the progress marker conditions are not met
        for decoration in map_decorations[:]:
            if not self.check_progress_markers(
                decoration.progress_marker, decoration.inverse_progress_marker
            ):
                map_decorations.remove(decoration)
        # Prune out previously removed decorations
        if new_map_name in self.removed_decorations_by_map:
            for decoration in self.removed_decorations_by_map[new_map_name]:
                if decoration in map_decorations:
                    map_decorations.remove(decoration)
                    if (
                        decoration.type is not None
                        and decoration.type.removed_image is not None
                    ):
                        removed_map_decorations.append(decoration)

        if old_map_name == new_map_name:
            # If loading up the same map, should retain the NPC positions
            npcs = self.game_map.npcs

            # Remove any current NPCs which should be missing
            for npc_char in npcs[:]:
                if not self.check_progress_markers(
                    npc_char.npc_info.progress_marker,
                    npc_char.npc_info.inverse_progress_marker,
                ):
                    npcs.remove(npc_char)

            # Add missing NPCs
            for npc in self.game_info.maps[new_map_name].npcs:
                if not self.check_progress_markers(
                    npc.progress_marker, npc.inverse_progress_marker
                ):
                    continue
                is_missing = True
                for npc_char in npcs:
                    if npc_char.npc_info is not None and npc == npc_char.npc_info:
                        is_missing = False
                        break
                if is_missing:
                    npcs.append(NpcState(npc))
        else:
            # On a map change load NPCs from scratch
            npcs = []
            for npc in self.game_info.maps[new_map_name].npcs:
                if self.check_progress_markers(
                    npc.progress_marker, npc.inverse_progress_marker
                ):
                    npcs.append(NpcState(npc))

        self.game_map = GameMap(
            self, new_map_name, map_decorations, removed_map_decorations, npcs
        )

    def load(self, pc_name_or_file_name: Optional[str] = None) -> None:
        # Set character state for new game
        save_game_file_path: Optional[str] = None
        if pc_name_or_file_name is not None:
            if os.path.isfile(pc_name_or_file_name):
                save_game_file_path = pc_name_or_file_name
            else:
                save_game_file_path = os.path.join(
                    self.saves_path, pc_name_or_file_name + ".xml"
                )

        if save_game_file_path is None or not os.path.isfile(save_game_file_path):
            self.game_info.parse_initial_game_state(pc_name_or_file_name)

            self.pending_dialog = self.game_info.initial_state_dialog
            pc = HeroState(
                self.game_info.character_types["hero"],
                self.game_info.initial_hero_pos_dat_tile,
                self.game_info.initial_hero_pos_dir,
                self.game_info.pc_name,
                self.game_info.pc_xp,
            )
            if self.game_info.pc_hp is not None and self.game_info.pc_hp < pc.hp:
                pc.hp = self.game_info.pc_hp
            if self.game_info.pc_mp is not None and self.game_info.pc_mp < pc.mp:
                pc.mp = self.game_info.pc_mp
            pc.weapon = self.game_info.pc_weapon
            pc.armor = self.game_info.pc_armor
            pc.shield = self.game_info.pc_shield
            pc.other_equipped_items = self.game_info.pc_other_equipped_items
            pc.unequipped_items = self.game_info.pc_unequipped_items
            self.hero_party = HeroParty(pc)
            self.hero_party.gp = self.game_info.pc_gp
            self.hero_party.progress_markers = self.game_info.pc_progress_markers

            self.set_map(
                self.game_info.initial_map,
                self.game_info.initial_map_decorations,
                init=True,
            )
        else:
            xml_root = ET.parse(save_game_file_path).getroot()

            map = xml_root.attrib["map"]
            party_members: List[HeroState] = []

            # Local helper method for parsing party members
            def parse_party_member(member_element: ET.Element) -> None:
                member_type = self.game_info.character_types["hero"]
                if "type" in member_element.attrib:
                    member_type = self.game_info.character_types[
                        member_element.attrib["type"]
                    ]

                member_is_combat_character = True
                if "is_combat_character" in member_element.attrib:
                    member_is_combat_character = (
                        member_element.attrib["is_combat_character"] == "yes"
                    )

                member = HeroState(
                    member_type,
                    self.game_info.get_location(map, member_element),
                    self.game_info.get_direction(map, member_element),
                    member_element.attrib["name"],
                    int(member_element.attrib["xp"]),
                    member_is_combat_character,
                )
                if "hp" in member_element.attrib:
                    member.hp = int(member_element.attrib["hp"])
                if "mp" in member_element.attrib:
                    member.mp = int(member_element.attrib["mp"])

                for item_element in member_element.findall("./EquippedItems/Item"):
                    item_name = item_element.attrib["name"]
                    if item_name in self.game_info.weapons:
                        member.weapon = self.game_info.weapons[item_name]
                    elif item_name in self.game_info.armors:
                        member.armor = self.game_info.armors[item_name]
                    elif item_name in self.game_info.shields:
                        member.shield = self.game_info.shields[item_name]
                    elif item_name in self.game_info.tools:
                        member.other_equipped_items.append(
                            self.game_info.tools[item_name]
                        )
                    else:
                        print("ERROR: Unsupported item", item_name, flush=True)

                for item_element in member_element.findall("./UnequippedItems/Item"):
                    item_name = item_element.attrib["name"]
                    item_count = 1
                    if "count" in item_element.attrib:
                        item_count = int(item_element.attrib["count"])
                    if item_name in self.game_info.items:
                        member.unequipped_items[
                            self.game_info.items[item_name]
                        ] = item_count
                    else:
                        print("ERROR: Unsupported item", item_name, flush=True)

                party_members.append(member)

            # Parse the party members
            for member_element in xml_root.findall("./PartyMember"):
                parse_party_member(member_element)
            if 0 == len(party_members):
                # This is an old save, attempt to parse the root element as if it were a PartyMember
                parse_party_member(xml_root)

            # Create the hero party from the party members
            self.hero_party = HeroParty(party_members[0])
            for member in party_members[1:]:
                self.hero_party.add_member(member)
            self.hero_party.set_main_character(xml_root.attrib["name"])

            # Parse properties of the entire party
            self.hero_party.gp = int(xml_root.attrib["gp"])

            # Load state related to repel monsters
            if "repel_monsters" in xml_root.attrib:
                self.hero_party.repel_monsters = (
                    xml_root.attrib["repel_monsters"] == "yes"
                )
            if "repel_monsters_decay_steps_remaining" in xml_root.attrib:
                self.hero_party.repel_monsters_decay_steps_remaining = int(
                    xml_root.attrib["repel_monsters_decay_steps_remaining"]
                )
            if "repel_monster_fade_dialog" in xml_root.attrib:
                self.hero_party.repel_monster_fade_dialog = [
                    xml_root.attrib["repel_monster_fade_dialog"]
                ]

            # Load state related to last outside position
            if "last_outside_map" in xml_root.attrib:
                self.hero_party.last_outside_map_name = xml_root.attrib[
                    "last_outside_map"
                ]
                self.hero_party.last_outside_pos_dat_tile = Point(
                    int(xml_root.attrib["last_outside_x"]),
                    int(xml_root.attrib["last_outside_y"]),
                )
                self.hero_party.last_outside_dir = Direction[
                    xml_root.attrib["last_outside_dir"]
                ]

            # Load state related to removed decorations
            for removed_decoration_element in xml_root.findall(
                "./RemovedDecorations/RemovedDecoration"
            ):
                removed_decoration_map_name = removed_decoration_element.attrib["map"]
                removed_decoration_x = int(removed_decoration_element.attrib["x"])
                removed_decoration_y = int(removed_decoration_element.attrib["y"])
                removed_decoration_type_name = (
                    None
                    if "type" not in removed_decoration_element.attrib
                    else removed_decoration_element.attrib["type"]
                )

                # Find the removed map decoration and insert it into self.removed_decorations_by_map
                for decoration in self.game_info.maps[
                    removed_decoration_map_name
                ].map_decorations:
                    decoration_type_name = (
                        None if decoration.type is None else decoration.type.name
                    )
                    if (
                        decoration_type_name == removed_decoration_type_name
                        and decoration.point.x == removed_decoration_x
                        and decoration.point.y == removed_decoration_y
                    ):
                        if (
                            removed_decoration_map_name
                            not in self.removed_decorations_by_map
                        ):
                            self.removed_decorations_by_map[
                                removed_decoration_map_name
                            ] = []
                        self.removed_decorations_by_map[
                            removed_decoration_map_name
                        ].append(decoration)
                        break

            # Parse the progress markers
            for progress_marker_element in xml_root.findall(
                "./ProgressMarkers/ProgressMarker"
            ):
                self.hero_party.progress_markers.append(
                    progress_marker_element.attrib["name"]
                )
                # print('Loaded progress marker ' + progressMarkerElement.attrib['name'], flush=True)

            self.set_map(map, init=True)

            # Load state related to light diameter
            if "light_diameter" in xml_root.attrib:
                self.hero_party.light_diameter = int(xml_root.attrib["light_diameter"])
            if "light_diameter_decay_steps" in xml_root.attrib:
                self.hero_party.light_diameter_decay_steps = int(
                    xml_root.attrib["light_diameter_decay_steps"]
                )
            if "light_diameter_decay_steps_remaining" in xml_root.attrib:
                self.hero_party.light_diameter_decay_steps_remaining = int(
                    xml_root.attrib["light_diameter_decay_steps_remaining"]
                )

            self.pending_dialog = self.game_info.parse_dialog(xml_root)

        # TODO: Remove Mocha from party
        """
        mocha = HeroState(self.game_info.character_types['mocha'],
                          self.game_info.initial_hero_pos_dat_tile,
                          self.game_info.initial_hero_pos_dir,
                          'Mocha',
                          0)
        self.hero_party.add_member(mocha)
        """

        # Initialize the default dialog font color based on the state of the hero party
        gde = GameDialogEvaluator(self.game_info, self)
        gde.update_default_dialog_font_color()

    def save(self, quick_save: bool = False) -> None:
        # Save the overall state of the party
        xml_root = ET.Element("SaveState")
        xml_root.attrib["name"] = self.hero_party.main_character.name
        xml_root.attrib["map"] = self.get_map_name()
        xml_root.attrib["gp"] = str(self.hero_party.gp)

        # Save state related to light diameter
        if self.hero_party.light_diameter is not None:
            xml_root.attrib["light_diameter"] = str(self.hero_party.light_diameter)
        if self.hero_party.light_diameter_decay_steps is not None:
            xml_root.attrib["light_diameter_decay_steps"] = str(
                self.hero_party.light_diameter_decay_steps
            )
        if self.hero_party.light_diameter_decay_steps_remaining is not None:
            xml_root.attrib["light_diameter_decay_steps_remaining"] = str(
                self.hero_party.light_diameter_decay_steps_remaining
            )

        # Save state related to repel monsters
        xml_root.attrib["repel_monsters"] = (
            "yes" if self.hero_party.repel_monsters else "no"
        )
        if self.hero_party.repel_monsters_decay_steps_remaining is not None:
            xml_root.attrib["repel_monsters_decay_steps_remaining"] = str(
                self.hero_party.repel_monsters_decay_steps_remaining
            )
        if self.hero_party.repel_monster_fade_dialog is not None and isinstance(
            self.hero_party.repel_monster_fade_dialog, str
        ):
            xml_root.attrib["repel_monster_fade_dialog"] = str(
                self.hero_party.repel_monster_fade_dialog
            )

        # Save state related to last outside position
        if "" != self.hero_party.last_outside_map_name:
            xml_root.attrib["last_outside_map"] = self.hero_party.last_outside_map_name
            xml_root.attrib["last_outside_x"] = str(
                self.hero_party.last_outside_pos_dat_tile.x
            )
            xml_root.attrib["last_outside_y"] = str(
                self.hero_party.last_outside_pos_dat_tile.y
            )
            xml_root.attrib["last_outside_dir"] = self.hero_party.last_outside_dir.name

        # Save state related to removed decorations
        removed_decorations_element = ET.SubElement(xml_root, "RemovedDecorations")
        for map_name, removed_decorations in self.removed_decorations_by_map.items():
            for decoration in removed_decorations:
                removed_decoration_element = ET.SubElement(
                    removed_decorations_element, "RemovedDecoration"
                )
                removed_decoration_element.attrib["map"] = map_name
                removed_decoration_element.attrib["x"] = str(decoration.point.x)
                removed_decoration_element.attrib["y"] = str(decoration.point.y)
                if decoration.type is not None:
                    removed_decoration_element.attrib["type"] = decoration.type.name

        # Save state for member of the hero party
        for member in self.hero_party.members:
            member_element = ET.SubElement(xml_root, "PartyMember")
            member_element.attrib["name"] = member.name
            member_element.attrib["type"] = member.character_type.name
            member_element.attrib["x"] = str(member.curr_pos_dat_tile.x)
            member_element.attrib["y"] = str(member.curr_pos_dat_tile.y)
            member_element.attrib["dir"] = member.direction.name
            member_element.attrib["xp"] = str(member.xp)
            member_element.attrib["hp"] = str(member.hp)
            member_element.attrib["mp"] = str(member.mp)
            member_element.attrib["is_combat_character"] = (
                "yes" if member.is_combat_character else "no"
            )

            items_element = ET.SubElement(member_element, "EquippedItems")
            if member.weapon is not None:
                item_element = ET.SubElement(items_element, "Item")
                item_element.attrib["name"] = member.weapon.name
            if member.armor is not None:
                item_element = ET.SubElement(items_element, "Item")
                item_element.attrib["name"] = member.armor.name
            if member.shield is not None:
                item_element = ET.SubElement(items_element, "Item")
                item_element.attrib["name"] = member.shield.name
            for tool in member.other_equipped_items:
                item_element = ET.SubElement(items_element, "Item")
                item_element.attrib["name"] = tool.name

            items_element = ET.SubElement(member_element, "UnequippedItems")
            for item, item_count in member.unequipped_items.items():
                if item_count > 0:
                    item_element = ET.SubElement(items_element, "Item")
                    item_element.attrib["name"] = item.name
                    item_element.attrib["count"] = str(item_count)

        progress_markers_element = ET.SubElement(xml_root, "ProgressMarkers")
        for progress_marker in self.hero_party.progress_markers:
            progress_marker_element = ET.SubElement(
                progress_markers_element, "ProgressMarker"
            )
            progress_marker_element.attrib["name"] = progress_marker

        # TODO: This should all be captured in game.xml
        if not quick_save:
            dialog_element = ET.SubElement(xml_root, "Dialog")
            dialog_element.text = (
                '"I am glad thou hast returned.  All our hopes are riding on thee."'
            )
            dialog_element = ET.SubElement(xml_root, "Dialog")
            dialog_element.text = (
                '"Before reaching thy next level of experience thou must gain [NEXT_LEVEL_XP] '
                'experience points.  See me again when thy level has increased."'
            )
            dialog_element = ET.SubElement(xml_root, "Dialog")
            dialog_element.text = (
                '"Goodbye now, [NAME].  Take care and tempt not the Fates."'
            )

        xml_string = xml.dom.minidom.parseString(ET.tostring(xml_root)).toprettyxml(
            indent="   "
        )

        save_game_file_path = os.path.join(
            self.saves_path, self.hero_party.main_character.name + ".xml"
        )

        # Archive off the old save, if one is present
        self.archive_saved_game_file(save_game_file_path)

        # Save the game
        try:
            if not os.path.isdir(self.saves_path):
                os.makedirs(self.saves_path)
            with open(save_game_file_path, "w") as save_game_file:
                save_game_file.write(xml_string)

            print("Saved game to file", save_game_file_path, flush=True)
        except Exception as exc:
            print(
                "ERROR: Exception encountered while attempting to save game file:",
                exc,
                flush=True,
            )

    def archive_saved_game_file(
        self, save_game_file_path: str, archive_dir_name: str = "archive"
    ) -> None:
        if os.path.isfile(save_game_file_path):
            # Archive old save game files
            archive_dir = os.path.join(self.saves_path, archive_dir_name)
            from datetime import datetime

            timestamp = datetime.fromtimestamp(
                os.path.getmtime(save_game_file_path)
            ).strftime("%Y%m%d%H%M%S")
            rename_file_path = os.path.join(
                archive_dir,
                self.hero_party.main_character.name + "_" + timestamp + ".xml",
            )
            try:
                if not os.path.isdir(archive_dir):
                    os.makedirs(archive_dir)
                if not os.path.isfile(rename_file_path):
                    os.rename(save_game_file_path, rename_file_path)
                else:
                    print("ERROR: File already exists:", rename_file_path, flush=True)
            except Exception as exc:
                print(
                    "ERROR: Exception encountered while attempting to archived saved game file:",
                    exc,
                    flush=True,
                )

    def get_tile_info(self, tile: Optional[Point] = None) -> Tile:
        return self.game_map.get_tile_info(tile)

    # Find point transitions for either the specified point or the current position of the player character.
    # If auto is true, only look for automatic point transitions
    def get_point_transition(
        self,
        tile: Optional[Point] = None,
        filter_to_automatic_transitions: bool = False,
    ) -> Optional[OutgoingTransition]:
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for point_transition in self.game_info.maps[
            self.get_map_name()
        ].point_transitions:
            if point_transition.point == tile and self.check_progress_markers(
                point_transition.progress_marker,
                point_transition.inverse_progress_marker,
            ):
                if filter_to_automatic_transitions:
                    if (
                        point_transition.is_automatic is None
                        and not self.is_light_restricted()
                    ):
                        # By default, make transitions manual in dark places
                        return point_transition
                    elif point_transition.is_automatic:
                        return point_transition
                else:
                    return point_transition
        return None

    def get_encounter_background(
        self, tile: Optional[Point] = None
    ) -> Optional[EncounterBackground]:
        return self.game_map.get_encounter_background(tile)

    def get_decorations(self, tile: Optional[Point] = None) -> List[MapDecoration]:
        return self.game_map.get_decorations(tile)

    def get_npc_to_talk_to(self) -> Optional[NpcState]:
        return self.game_map.get_npc_to_talk_to()

    def get_npc_by_name(self, name: str) -> Optional[MapCharacterState]:
        return self.game_map.get_npc_by_name(name)

    def get_special_monster(
        self, tile: Optional[Point] = None
    ) -> Optional[SpecialMonster]:
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for special_monster in self.game_info.maps[
            self.get_map_name()
        ].special_monsters:
            if special_monster.point == tile and self.check_progress_markers(
                special_monster.progress_marker, special_monster.inverse_progress_marker
            ):
                # print('Found monster at point: ', tile, flush=True)
                return special_monster
        return None

    # Return True if progress_markers satisfied, else False
    def check_progress_markers(
        self, progress_marker: Optional[str], inverse_progress_marker: Optional[str]
    ) -> bool:
        if progress_marker is None:
            progress_marker_eval = True
        else:
            progress_marker_eval = self.evaluate_progress_marker_string(progress_marker)

        if inverse_progress_marker is None:
            inverse_progress_marker_eval = False
        else:
            inverse_progress_marker_eval = self.evaluate_progress_marker_string(
                inverse_progress_marker
            )

        return progress_marker_eval and not inverse_progress_marker_eval

    def evaluate_progress_marker_string(self, progress_marker_string: str) -> bool:
        progress_marker_term_string = progress_marker_string
        logical_tokens = ["(", ")", " and ", " or ", " not ", "&", "|", "!"]
        for strip_term in logical_tokens:
            progress_marker_term_string = progress_marker_term_string.replace(
                strip_term, " "
            )
        stripped_logical_tokens = [x.strip() for x in logical_tokens]
        for term in filter(None, progress_marker_term_string.split(" ")):
            if term in stripped_logical_tokens:
                continue
            progress_marker_string = progress_marker_string.replace(
                term, str(term in self.hero_party.progress_markers)
            )
        if eval(progress_marker_string):
            return True
        return False

    def can_move_to_tile(
        self,
        tile: Point,
        enforce_npc_hp_penalty_limit: bool = False,
        enforce_npc_dof_limit: bool = False,
        is_npc: bool = False,
        prev_tile: Optional[Point] = None,
    ) -> bool:
        return self.game_map.can_move_to_tile(
            tile, enforce_npc_hp_penalty_limit, enforce_npc_dof_limit, is_npc, prev_tile
        )

    def get_tile_monsters(self, tile: Optional[Point] = None) -> List[str]:
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for mz in self.game_info.maps[self.get_map_name()].monster_zones:
            if mz.x <= tile.x <= mz.x + mz.w and mz.y <= tile.y <= mz.y + mz.h:
                # print('in monsterZone of set ' + mz.setName + ':', self.gameInfo.monsterSets[mz.setName], flush=True)
                return self.game_info.monster_sets[mz.name]
        return self.game_map.get_tile_monsters(tile)

    def is_light_restricted(self) -> bool:
        return (
            self.hero_party.light_diameter is not None
            and self.hero_party.light_diameter <= self.win_size_tiles.w
            and self.hero_party.light_diameter <= self.win_size_tiles.h
        )

    def is_outside(self) -> bool:
        return self.game_info.maps[self.get_map_name()].is_outside

    def is_inside(self) -> bool:
        return not self.is_outside()

    def make_map_transition(self, transition: Optional[OutgoingTransition]) -> bool:
        if transition is None:
            return False

        src_map = self.game_info.maps[self.get_map_name()]
        dest_map = self.game_info.maps[transition.dest_map]

        # Find the destination transition corresponding to this transition
        if transition.dest_name is None:
            try:
                dest_transition = dest_map.transitions_by_map[self.get_map_name()]
            except KeyError:
                print("Failed to find destination transition by dest_map", flush=True)
                return False
        else:
            try:
                dest_transition = dest_map.transitions_by_map_and_name[
                    self.get_map_name()
                ][transition.dest_name]
            except KeyError:
                try:
                    dest_transition = dest_map.transitions_by_name[transition.dest_name]
                except KeyError:
                    print(
                        "Failed to find destination transition by dest_name", flush=True
                    )
                    return False

        # If transitioning from outside to inside, save off last outside position
        if src_map.is_outside and not dest_map.is_outside:
            self.hero_party.set_last_outside_pos(
                self.get_map_name(),
                self.hero_party.get_curr_pos_dat_tile(),
                self.hero_party.get_direction(),
            )

        # Make the transition and draw the map
        AudioPlayer().play_sound("walk_away")
        self.hero_party.set_pos(dest_transition.point, dest_transition.dir)
        self.set_map(
            transition.dest_map, respawn_decorations=transition.respawn_decorations
        )
        self.draw_map(True)

        # Slight pause on a map transition
        pygame.time.wait(250)

        return True

    def is_facing_locked_item(self) -> bool:
        return self.game_map.is_facing_locked_item()

    def is_facing_openable_item(self) -> bool:
        return self.game_map.is_facing_openable_item()

    def open_locked_item(self) -> Optional[MapDecoration]:
        removed_decoration = self.game_map.open_locked_item()
        if removed_decoration:
            if self.get_map_name() not in self.removed_decorations_by_map:
                self.removed_decorations_by_map[self.get_map_name()] = []
            self.removed_decorations_by_map[self.get_map_name()].append(
                removed_decoration
            )
        return removed_decoration

    def remove_decoration(self, decoration: MapDecoration) -> None:
        removed_decoration = self.game_map.remove_decoration(decoration)
        if removed_decoration:
            if self.get_map_name() not in self.removed_decorations_by_map:
                self.removed_decorations_by_map[self.get_map_name()] = []
            self.removed_decorations_by_map[self.get_map_name()].append(
                removed_decoration
            )

    def draw_map(
        self,
        flip_buffer: bool = True,
        draw_background: bool = True,
        draw_combat: bool = True,
        draw_status: bool = True,
        draw_only_character_sprites: bool = False,
    ) -> None:
        if draw_only_character_sprites:
            self.game_map.draw_character_sprites()
            return

        # Draw the map to the screen
        if draw_background:
            self.game_map.draw()

        # If in combat, refresh the background image and render the monsters.
        if draw_combat and self.combat_encounter is not None:
            self.combat_encounter.background_image = self.screen.copy()
            self.combat_encounter.render_monsters()
        elif draw_status:
            GameDialog.create_persistent_status_dialog(self.hero_party).blit(
                self.screen, False
            )

        # Flip the screen buffer
        if flip_buffer:
            pygame.display.flip()

    def advance_tick(
        self,
        update_map: bool = True,
        draw_map: bool = True,
        advance_time: bool = True,
        flip_buffer: bool = True,
    ) -> None:
        if update_map:
            self.game_map.update()

        if draw_map:
            self.draw_map(flip_buffer=False)

        if advance_time:
            # Allow pygame to process internal events for interacting with the OS every frame
            pygame.event.pump()

            self.clock.tick(30)
            # self.tick_count += 1
            # if 10 == self.tick_count % 100:
            #     print(f'FPS = {self.clock.get_fps()}', flush=True)

        if flip_buffer:
            pygame.display.flip()

    def get_game_info(self) -> GameInfo:
        return self.game_info

    def get_image_pad_tiles(self) -> Point:
        return self.image_pad_tiles

    def get_hero_party(self) -> HeroParty:
        return self.hero_party

    def get_dialog_replacement_variables(self) -> DialogReplacementVariables:
        variables = DialogReplacementVariables()
        variables.generic["[NAME]"] = self.hero_party.main_character.get_name()
        variables.generic["[NEXT_LEVEL_XP]"] = str(
            self.hero_party.main_character.calc_xp_to_next_level()
        )
        map_origin = self.game_info.maps[self.get_map_name()].origin
        if map_origin is not None:
            map_coord = self.hero_party.get_curr_pos_dat_tile() - map_origin
            variables.generic["[X]"] = str(abs(map_coord.x))
            variables.generic["[Y]"] = str(abs(map_coord.y))
            if map_coord.x < 0:
                variables.generic["[X_DIR]"] = "East"
            else:
                variables.generic["[X_DIR]"] = "West"
            if map_coord.y < 0:
                variables.generic["[Y_DIR]"] = "South"
            else:
                variables.generic["[Y_DIR]"] = "North"
        return variables

    def is_in_combat(self) -> bool:
        return self.combat_encounter is not None

    def is_combat_allowed(self) -> bool:
        return len(self.get_tile_monsters()) > 0

    def get_map_name(self) -> str:
        return self.game_map.map.name

    def get_win_size_pixels(self) -> Point:
        return self.win_size_pixels

    def initiate_encounter(
        self,
        monster_info: Optional[MonsterInfo] = None,
        approach_dialog: Optional[DialogType] = None,
        victory_dialog: Optional[DialogType] = None,
        run_away_dialog: Optional[DialogType] = None,
        encounter_music: Optional[str] = None,
        message_dialog: Optional[GameDialog] = None,
    ) -> None:
        # TODO: Make the conditions for no monsters configurable
        if self.hero_party.has_item("Ball of Light"):
            return

        # Determine the monster party for the encounter
        if monster_info is None:
            # Check for special monsters
            special_monster_info = self.get_special_monster()
            if special_monster_info is not None:
                monster_party = MonsterParty([MonsterState(special_monster_info)])
                approach_dialog = special_monster_info.approach_dialog
                victory_dialog = special_monster_info.victory_dialog
                run_away_dialog = special_monster_info.run_away_dialog
            else:
                random_monster = random.choice(self.get_tile_monsters())
                if random_monster not in self.game_info.monsters:
                    print(
                        f"ERROR: Failed to initiate combat encounter due to lack of monster {random_monster}",
                        flush=True,
                    )
                    return
                monster_info = self.game_info.monsters[random_monster]
                monster_party = MonsterParty([MonsterState(monster_info)])
        else:
            monster_party = MonsterParty([MonsterState(monster_info)])

        if self.hero_party.is_monster_party_repelled(monster_party, self.is_outside()):
            return

        # A combat encounter requires an encounter background
        encounter_background = self.game_info.maps[
            self.get_map_name()
        ].encounter_background
        if encounter_background is None:
            encounter_background = self.get_encounter_background()
            if encounter_background is None:
                print(
                    "ERROR: Failed to initiate combat encounter due to lack of encounter image in map",
                    self.get_map_name(),
                    flush=True,
                )
                return

        # Perform the combat encounter
        CombatEncounter.static_init("combat")
        self.combat_encounter = CombatEncounter(
            game_info=self.game_info,
            game_state=self,
            monster_party=monster_party,
            encounter_background=encounter_background,
            message_dialog=message_dialog,
            approach_dialog=approach_dialog,
            victory_dialog=victory_dialog,
            run_away_dialog=run_away_dialog,
            encounter_music=encounter_music,
        )
        self.combat_encounter.encounter_loop()
        self.combat_encounter = None

        # Play the music for the current map
        AudioPlayer().play_music(self.game_info.maps[self.get_map_name()].music)

        # Clear event queue
        GameEvents.clear_events()

    def handle_death(self, message_dialog: Optional[GameDialog] = None) -> None:
        if not self.hero_party.has_surviving_members():
            # Player death
            self.hero_party.main_character.hp = 0
            AudioPlayer().stop_music()
            AudioPlayer().play_sound("player_died")
            GameDialog.create_encounter_status_dialog(self.hero_party).blit(
                self.screen, False
            )
            gde = GameDialogEvaluator(self.game_info, self)
            if message_dialog is None:
                message_dialog = GameDialog.create_message_dialog()
            else:
                message_dialog.add_message("")
            gde.add_and_wait_for_message("Thou art dead.", message_dialog)
            gde.wait_for_acknowledgement(message_dialog)
            for hero in self.hero_party.members:
                hero.curr_pos_dat_tile = (
                    hero.dest_pos_dat_tile
                ) = self.game_info.death_hero_pos_dat_tile
                hero.curr_pos_offset_img_px = Point(0, 0)
                hero.direction = self.game_info.death_hero_pos_dir
                hero.hp = hero.level.hp
                hero.mp = hero.level.mp
            gde.update_default_dialog_font_color()
            self.pending_dialog = self.game_info.death_dialog
            self.hero_party.gp = self.hero_party.gp // 2
            self.set_map(self.game_info.death_map, respawn_decorations=True)

    def handle_quit(self, force: bool = False) -> None:
        AudioPlayer().play_sound("select")
        if force:
            self.is_running = False

        # Save off initial background image
        background_surface = self.screen.copy()

        menu_dialog = GameDialog.create_yes_no_menu(
            Point(1, 1), "Do you really want to quit?"
        )
        menu_dialog.blit(self.screen, flip_buffer=True)
        menu_result = GameDialogEvaluator(self.game_info, self).get_menu_result(
            menu_dialog, allow_quit=False
        )
        if menu_result is not None and menu_result == "YES":
            self.is_running = False

        # Restore initial background image
        menu_dialog.erase(self.screen, background_surface, flip_buffer=True)

    def should_add_math_problems_in_combat(self) -> bool:
        return self.__should_add_math_problems_in_combat

    def toggle_should_add_math_problems_in_combat(self) -> None:
        self.__should_add_math_problems_in_combat = (
            not self.__should_add_math_problems_in_combat
        )
