#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Dict, List, NamedTuple, Optional, Union

import pygame

from dataclasses import dataclass
from enum import Enum
from Point import Point


class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

    def get_direction_vector(self) -> Point:
        if Direction.NORTH == self:
            vector = Point(0, -1)
        elif Direction.SOUTH == self:
            vector = Point(0, 1)
        elif Direction.EAST == self:
            vector = Point(1, 0)
        else:
            vector = Point(-1, 0)
        return vector

    def get_opposite_direction(self) -> Direction:
        if Direction.NORTH == self:
            opposite = Direction.SOUTH
        elif Direction.SOUTH == self:
            opposite = Direction.NORTH
        elif Direction.EAST == self:
            opposite = Direction.WEST
        else:
            opposite = Direction.EAST
        return opposite


class Phase(Enum):
    A = 1
    B = 2


# Conditionals supported for dialog checks
class DialogCheckEnum(Enum):
    HAS_ITEM = 1                       # attributes: name (if unknown name, treated as a progress marker),
    #                                                count (defaults to 1)
    LACKS_ITEM = 2                     # attributes: name (if unknown name, treated as a progress marker),
    #                                                count (defaults to 1)
    IS_FACING_DOOR = 3                 # attributes: <none>
    IS_OUTSIDE = 4                     # attributes: count (number, range, or unlimited)
    IS_INSIDE = 5                      # attributes: count (number, range, or unlimited)
    IS_DARK = 6                        # attributes: <none>
    IS_AT_COORDINATES = 7              # attributes: map, x, y
    IS_IN_COMBAT = 8                   # attributes: name (optional name of monster)
    IS_NOT_IN_COMBAT = 9               # attributes: <none>


# Actions that can be triggered from dialog
class DialogActionEnum(Enum):
    SAVE_GAME = 1                      # attributes: <none>
    MAGIC_RESTORE = 2                  # attributes: count (number, range, or unlimited)
    HEALTH_RESTORE = 3                 # attributes: count (number, range, or unlimited)
    LOSE_ITEM = 4                      # attributes: item (if unknown name, treated as a progress marker),
    #                                                count (defaults to 1)
    GAIN_ITEM = 5                      # attributes: item (if unknown name, treated as a progress marker),
    #                                                count (defaults to 1)
    SET_LIGHT_DIAMETER = 6             # attributes: count, decay (number or unlimited)
    REPEL_MONSTERS = 7                 # attributes: decay
    GOTO_COORDINATES = 8               # attributes: map, x, y, dir
    GOTO_LAST_OUTSIDE_COORDINATES = 9  # attributes: <none>
    PLAY_SOUND = 10                    # attributes: name
    PLAY_MUSIC = 11                    # attributes: name (play it once and return to looping on the prior music)
    VISUAL_EFFECT = 12                 # attributes: name (fadeToBlackAndBack, flickering, rainbowEffect, darkness)
    ATTACK_MONSTER = 13                # attributes: name, victoryDialog (victoryDialogScript in XML),
    #                                                runAwayDialog (runAwayDialogScript in XML), encounterMusic
    OPEN_DOOR = 14                     # attributes: <none>
    MONSTER_SLEEP = 15                 # attributes: bypass (to bypass resistances)
    MONSTER_STOP_SPELL = 16            # attributes: bypass (to bypass resistances)


# Alternate options to attacking (or attempting to run away) which may be attempted by a monster
class MonsterActionEnum(Enum):
    HEAL = 1
    HURT = 2
    SLEEP = 3
    STOPSPELL = 4
    HEALMORE = 5
    HURTMORE = 6
    BREATH_FIRE = 7
    BREATH_STRONG_FIRE = 8
    ATTACK = 9


# Dialog type
DialogType = List[Union[str,
                        Dict[str, 'DialogType'],
                        'DialogVariable',
                        'DialogGoTo',
                        'DialogVendorBuyOptions',
                        'DialogVendorBuyOptionsVariable',
                        'DialogVendorSellOptions',
                        'DialogVendorSellOptionsVariable',
                        'DialogCheck',
                        'DialogAction']]


# Set a variable to be used in substitution for the remainder of the dialog session
@dataclass
class DialogVariable:
    name: str
    value: str


# Dialog to branch to a labeled dialog state
@dataclass
class DialogGoTo:
    label: str


# List of items that can be bought from the vendor where each item is a 2 element list
# consisting of item name and gold cost (as str)
# Optionally could also be a string for replacement by a DialogVariable
DialogVendorBuyOptionsParamWithoutReplacementType = List[List[str]]
DialogVendorBuyOptionsParamType = Union[DialogVendorBuyOptionsParamWithoutReplacementType, str]


# Dialog for a list of vendor buy options
@dataclass
class DialogVendorBuyOptions:
    name_and_gp_row_data: DialogVendorBuyOptionsParamType


# List of the classes of items that can be sold to the vendor
# Optionally could also be a string for replacement by a DialogVariable
DialogVendorSellOptionsParamWithoutReplacementType = List[str]
DialogVendorSellOptionsParamType = Union[DialogVendorSellOptionsParamWithoutReplacementType, str]


@dataclass
class DialogVendorBuyOptionsVariable:
    name: str
    value: DialogVendorBuyOptionsParamWithoutReplacementType


# Dialog for a list of vendor sell options
@dataclass
class DialogVendorSellOptions:
    item_types: DialogVendorSellOptionsParamType


@dataclass
class DialogVendorSellOptionsVariable:
    name: str
    value: DialogVendorSellOptionsParamWithoutReplacementType


# Conditionally branch dialog if the check condition is not met
@dataclass
class DialogCheck:
    type: DialogCheckEnum
    failed_check_dialog: Optional[DialogType]
    name: Optional[str] = None
    count: Union[int, str] = 1
    map_name: Optional[str] = None
    map_pos: Optional[Point] = None


# Conditionally branch dialog if the check condition is not met
@dataclass
class DialogAction:
    type: DialogActionEnum
    name: Optional[str] = None
    count: Union[int, str] = 1
    decay_steps: Optional[int] = None
    map_name: Optional[str] = None
    map_pos: Optional[Point] = None
    map_dir: Optional[Direction] = None
    victory_dialog: Optional[DialogType] = None
    run_away_dialog: Optional[DialogType] = None
    encounter_music: Optional[str] = None


class Tile(NamedTuple):
    name: str
    symbol: str
    image: Union[pygame.Surface, List[pygame.Surface]]
    walkable: bool
    can_talk_over: bool
    hp_penalty: int
    mp_penalty: int
    speed: float
    spawn_rate: float
    special_edges: bool


class Decoration(NamedTuple):
    name: str
    image: pygame.Surface
    walkable: bool
    remove_with_search: bool
    removeWithKey: bool


class CharacterType(NamedTuple):
    type: str
    images: Dict[Direction, Dict[Phase, pygame.Surface]]


class LeavingTransition(NamedTuple):
    dest_map: str
    dest_point: Point
    dest_dir: Direction
    respawn_decorations: bool


class PointTransition(NamedTuple):
    src_point: Point
    dest_map: str
    dest_point: Point
    dest_dir: Direction
    respawn_decorations: bool
    progress_marker: Optional[str] = None
    inverse_progress_marker: Optional[str] = None


class NpcInfo(NamedTuple):
    type: str
    point: Point
    direction: Direction
    walking: bool
    dialog: Optional[DialogType] = None
    progress_marker: Optional[str] = None
    inverse_progress_marker: Optional[str] = None


class MapDecoration(NamedTuple):
    type: Optional[str]
    point: Point
    dialog: Optional[DialogType] = None
    progress_marker: Optional[str] = None
    inverse_progress_marker: Optional[str] = None


class SpecialMonster(NamedTuple):
    name: str  # TODO: Change to Monster reference instead of storing the monster name
    point: Point
    approach_dialog: Optional[DialogType] = None
    victory_dialog: Optional[DialogType] = None
    run_away_dialog: Optional[DialogType] = None
    progress_marker: Optional[str] = None
    inverse_progress_marker: Optional[str] = None


class Map(NamedTuple):
    name: str
    dat: List[str]
    overlay_dat: Optional[List[str]]
    size: Point
    music: str
    light_diameter: Optional[int]
    leaving_transition: Optional[LeavingTransition]
    point_transitions: List[PointTransition]
    npcs: List[NpcInfo]
    map_decorations: List[MapDecoration]
    monster_zones: List[MonsterZone]
    encounter_image: Optional[pygame.Surface]
    special_monsters: List[SpecialMonster]
    is_outside: bool
    origin: Optional[Point] = None


class MonsterAction(NamedTuple):
    type: MonsterActionEnum
    probability: float
    health_ratio_threshold: float


class MonsterInfo(NamedTuple):
    name: str
    image: pygame.Surface
    dmg_image: pygame.Surface
    strength: int
    agility: int
    min_hp: int
    max_hp: int
    sleep_resist: float
    stopspell_resist: float
    hurt_resist: float
    dodge: float
    block_factor: float
    xp: int
    min_gp: int
    max_gp: int
    monster_actions: List[MonsterAction]
    allows_critical_hits: bool


class MonsterZone(NamedTuple):
    x: int
    y: int
    w: int
    h: int
    name: str


class Level(NamedTuple):
    number: int
    name: str
    xp: int
    strength: int
    agility: int
    hp: int
    mp: int


class Spell(NamedTuple):
    name: str
    level: Level
    mp: int
    available_in_combat: bool
    available_outside_combat: bool
    min_hp_recover: int
    max_hp_recover: int
    min_damage_by_hero: int
    max_damage_by_hero: int
    min_damage_by_monster: int
    max_damage_by_monster: int
    excluded_map: Optional[str]
    included_map: Optional[str]


class Weapon(NamedTuple):
    name: str
    attack_bonus: int
    gp: int


class Helm(NamedTuple):
    name: str
    defense_bonus: int
    gp: int


class Armor(NamedTuple):
    name: str
    defense_bonus: int
    gp: int
    ignores_tile_penalties: bool
    hurt_dmg_modifier: float
    fire_dmg_modifier: float
    stopspell_resistance: float
    hp_regen_tiles: int


class Shield(NamedTuple):
    name: str
    defense_bonus: int
    gp: int


@dataclass
class Tool:
    name: str
    attack_bonus: int = 0
    defense_bonus: int = 0
    gp: int = 0
    droppable: bool = True
    equippable: bool = False
    use_dialog: Optional[DialogType] = None

    def __hash__(self) -> int:
        return hash('Tool:' + self.name)


ItemType = Union[Weapon, Helm, Armor, Shield, Tool]


class MapImageInfo(NamedTuple):
    name: str
    image: pygame.Surface
    size_tiles: Point
    size_pixels: Point
    overlay_image: Optional[pygame.Surface] = None

    @staticmethod
    def create_null() -> MapImageInfo:
        return MapImageInfo('null',
                            pygame.Surface((0, 0)),
                            Point(),
                            Point())


def main() -> None:
    pass


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
