#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

from dataclasses import dataclass
from enum import Enum
import pygame
import random

from Point import Point


class GameTypes:
    @staticmethod
    def parse_float(value: Union[str, float, int]) -> float:
        if isinstance(value, str) and '/' in value:
            ret_val = int(value.split('/')[0]) / int(value.split('/')[1])
        else:
            ret_val = float(value)
        return ret_val

    @staticmethod
    def parse_int_range(value: Union[str, int]) -> Tuple[int, int]:
        if isinstance(value, str) and '-' in value:
            min_val = int(value.split('-')[0])
            max_val = int(value.split('-')[1])
        else:
            min_val = max_val = int(value)
        return min_val, max_val

    @staticmethod
    def get_int_value(value: Union[str, int]) -> int:
        (minVal, maxVal) = GameTypes.parse_int_range(value)
        return random.randint(minVal, maxVal)

    @staticmethod
    def dialog_contains_action(dialog: DialogType, action: DialogActionEnum) -> bool:
        return GameTypes.get_dialog_action(dialog, action) is not None

    @staticmethod
    def get_dialog_action(dialog: DialogType, action: DialogActionEnum) -> Optional[DialogAction]:
        # Not checking sub-trees and the like.  The use dialog for spells and monster action should always be linear.
        for element in dialog:
            if isinstance(element, DialogAction):
                if element.type == action:
                    return element
        return None

    @staticmethod
    def dialog_contains_action_category(dialog: DialogType, category: ActionCategoryTypeEnum) -> bool:
        # Not checking sub-trees and the like.  The use dialog for spells and monster action should always be linear.
        for element in dialog:
            if isinstance(element, DialogAction):
                if category == element.category:
                    return True
        return False


class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

    def get_vector(self) -> Point:
        if Direction.NORTH == self:
            vector = Point(0, -1)
        elif Direction.SOUTH == self:
            vector = Point(0, 1)
        elif Direction.EAST == self:
            vector = Point(1, 0)
        else:
            vector = Point(-1, 0)
        return vector

    def get_opposite(self) -> Direction:
        if Direction.NORTH == self:
            opposite = Direction.SOUTH
        elif Direction.SOUTH == self:
            opposite = Direction.NORTH
        elif Direction.EAST == self:
            opposite = Direction.WEST
        else:
            opposite = Direction.EAST
        return opposite

    @staticmethod
    def get_direction(input: Union[Point, int]) -> Optional[Direction]:
        if isinstance(input, Point):
            # Input is a vector
            vector = input
            for direction in Direction:
                if direction.get_vector() == vector:
                    return direction
        elif isinstance(input, int):
            # Input is a pygame_key
            pygame_key = input
            if pygame.K_UP == pygame_key:
                return Direction.NORTH
            elif pygame.K_DOWN == pygame_key:
                return Direction.SOUTH
            elif pygame.K_RIGHT == pygame_key:
                return Direction.EAST
            elif pygame.K_LEFT == pygame_key:
                return Direction.WEST
        return None


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
    IS_AT_COORDINATES = 7              # attributes: map, x, y (x and y may be pulled from location)
    IS_IN_COMBAT = 8                   # attributes: name
    IS_NOT_IN_COMBAT = 9               # attributes: <none>
    IS_COMBAT_ALLOWED = 10             # attributes: <none>
    IS_COMBAT_DISALLOWED = 11          # attributes: <none>
    IS_TARGET_HERO = 12                # attributes: <none>
    IS_TARGET_MONSTER = 13             # attributes: <none>
    IS_DEFINED = 14                    # attributes: name - returns true if the name is a defined variable
    IS_NOT_DEFINED = 15                # attributes: name - returns true if the name is NOT a defined variable


# Actions that can be triggered from dialog
class DialogActionEnum(Enum):
    SAVE_GAME = 1                      # attributes: <none>
    MAGIC_RESTORE = 2                  # attributes: count (number, range, or unlimited), category,
    #                                                bypass (to bypass any dialog or updating the screen)
    HEALTH_RESTORE = 3                 # attributes: count (number, range, or unlimited), category,
    #                                                bypass (to bypass any dialog or updating the screen)
    LOSE_ITEM = 4                      # attributes: item (if unknown name, treated as a progress marker),
    #                                                count (defaults to 1), bypass (to bypass updating the screen)
    GAIN_ITEM = 5                      # attributes: item (if unknown name, treated as a progress marker),
    #                                                count (defaults to 1), bypass (to bypass updating the screen)
    SET_LIGHT_DIAMETER = 6             # attributes: count, decay (number or unlimited)
    REPEL_MONSTERS = 7                 # attributes: decay, fade_dialog
    GOTO_COORDINATES = 8               # attributes: map, x, y, dir
    GOTO_LAST_OUTSIDE_COORDINATES = 9  # attributes: <none>
    PLAY_SOUND = 10                    # attributes: name
    PLAY_MUSIC = 11                    # attributes: name (play it once and return to looping on the prior music)
    VISUAL_EFFECT = 12                 # attributes: name (fadeToBlackAndBack, flickering, rainbowEffect, darkness)
    START_ENCOUNTER = 13               # attributes: name, approach_dialog, victory_dialog, run_away_dialog,
    #                                                encounterMusic
    OPEN_DOOR = 14                     # attributes: <none>
    SLEEP = 15                         # attributes: bypass (to bypass resistances), category
    STOPSPELL = 16                     # attributes: bypass (to bypass resistances), category
    DAMAGE_TARGET = 17                 # attributes: count (number, range, unlimited, or default), category
    #                                                bypass (to bypass resistances and damage modifiers)
    WAIT = 18                          # attributes: count (number of milliseconds to wait)
    SET_LEVEL = 19                     # attributes: name, bypass (to bypass updating the screen)


class ActionCategoryTypeEnum(Enum):
    PHYSICAL = 1
    MAGICAL = 2
    FIRE = 3
    ICE = 4


class TargetTypeEnum(Enum):
    SINGLE_ALLY = 1
    ALL_ALLIES = 2
    SINGLE_ENEMY = 3
    ALL_ENEMIES = 4
    SELF = 5


# Alternate options to attacking (or attempting to run away) which may be attempted by a monster
# TODO: Get rid of this in favor of actions defined in XML
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

    def is_spell(self) -> bool:
        return (MonsterActionEnum.HEAL == self
                or MonsterActionEnum.HURT == self
                or MonsterActionEnum.SLEEP == self
                or MonsterActionEnum.STOPSPELL == self
                or MonsterActionEnum.HEALMORE == self
                or MonsterActionEnum.HURTMORE == self)

    def is_heal_spell(self) -> bool:
        return MonsterActionEnum.HEAL == self or MonsterActionEnum.HEALMORE == self

    def is_hurt_spell(self) -> bool:
        return MonsterActionEnum.HURT == self or MonsterActionEnum.HURTMORE == self

    def get_spell(self, spells: Dict[str, Spell]) -> Optional[Spell]:
        if self.name.capitalize() in spells:
            return spells[self.name.capitalize()]
        return None

    def requires_target(self) -> bool:
        return (MonsterActionEnum.ATTACK == self
                or self.is_hurt_spell()
                or self.is_fire_attack())

    def is_fire_attack(self) -> bool:
        return MonsterActionEnum.BREATH_FIRE == self or MonsterActionEnum.BREATH_STRONG_FIRE == self


# Dialog type
# The correct type for the branching dialog is Dict[str, 'DialogType'] but the type of Dict[str, Any] is used instead
# since mypy does not yet support recursive types and cannot handle the correct type.
DialogType = List[Union[str,  # a string of dialog
                        Dict[str, Any],  # branching dialog, actual type is Dict[str, 'DialogType']
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

    # Some variables may specify an int range that needs to be evaluated to resolve to a random value in that range
    def evaluate(self) -> str:
        value = self.value
        try:
            value = str(GameTypes.get_int_value(value))
        except ValueError:
            pass
        return value


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
    dialog: Optional[DialogType]
    name: Optional[str] = None
    count: Union[int, str] = 1
    map_name: Optional[str] = None
    map_pos: Optional[Point] = None
    is_assert: bool = True


# Conditionally branch dialog if the check condition is not met
@dataclass
class DialogAction:
    type: DialogActionEnum
    name: Optional[str] = None
    count: Union[int, str] = 1
    bypass: bool = False
    decay_steps: Optional[int] = None
    fade_dialog: Optional[DialogType] = None
    map_name: Optional[str] = None
    map_pos: Optional[Point] = None
    map_dir: Optional[Direction] = None
    approach_dialog: Optional[DialogType] = None
    victory_dialog: Optional[DialogType] = None
    run_away_dialog: Optional[DialogType] = None
    encounter_music: Optional[str] = None
    category: ActionCategoryTypeEnum = ActionCategoryTypeEnum.PHYSICAL  # TODO: Change to list of categories?
    target_type: TargetTypeEnum = TargetTypeEnum.SINGLE_ALLY
    problem: Optional[Problem] = None


# Type to aggregate all the different dialog replacement variables
class DialogReplacementVariables:
    def __init__(self) -> None:
        self.generic: Dict[str, str] = {}
        self.vendor_buy_options: Dict[str, DialogVendorBuyOptionsParamWithoutReplacementType] = {}
        self.vendor_sell_options: Dict[str, DialogVendorSellOptionsParamWithoutReplacementType] = {}


class Tile(NamedTuple):
    name: str
    symbol: str
    images: List[List[pygame.surface.Surface]]
    walkable: bool
    can_talk_over: bool
    hp_penalty: int
    mp_penalty: int
    speed: float
    spawn_rate: float


class Decoration(NamedTuple):
    name: str
    width_tiles: int
    height_tiles: int
    image: pygame.surface.Surface
    walkable: bool = True
    remove_with_search: bool = False
    remove_with_open: bool = False
    remove_with_key: bool = False
    remove_sound: Optional[str] = None


class CharacterType(NamedTuple):
    name: str
    images: Dict[Direction, Dict[int, pygame.surface.Surface]]
    levels: List[Level] = []
    num_phases: int = 2

    @staticmethod
    def create_null(name: str = 'null') -> CharacterType:
        return CharacterType(name, {})


class IncomingTransition(NamedTuple):
    point: Point                       # Location of PC on incoming transit; trigger point for outgoing point transit
    dir: Direction                     # Direction of the PC on incoming transit
    name: Optional[str]                # Name of transition (where needed due to keep transits unambiguous)
    dest_map: Optional[str] = None     # Name of map to which the transition connects


class OutgoingTransition(NamedTuple):
    point: Point                       # Location of PC on incoming transit; trigger point for outgoing point transit
    dir: Direction                     # Direction of the PC on incoming transit
    name: Optional[str]                # Name of transition (where needed to keep transits unambiguous)
    dest_map: str                      # Name of map to which the transition connects
    dest_name: Optional[str] = None    # Name of destination transition in the destination map
    respawn_decorations: bool = False  # Do removable decorations (ie doors, chests) get respawned when transit occurs
    progress_marker: Optional[str] = None
    inverse_progress_marker: Optional[str] = None

    # Bounding rectangle for the map.  When outside this box, a leaving transition is toggled.
    bounding_box: Optional[ pygame.Rect] = None

    # For point transitions, is the transit automatic or must it be player initiated.
    # If None, default behavior is automatic if light not restricted, else manual.
    # CHANGED DEFAULT TO TRUE AS THE STAIRS COMMAND HAS BEEN REMOVED
    is_automatic: Optional[bool] = True


AnyTransition = Union[IncomingTransition, OutgoingTransition]


class NpcInfo(NamedTuple):
    character_type: CharacterType
    point: Point
    direction: Direction
    walking: bool
    dialog: Optional[DialogType] = None
    progress_marker: Optional[str] = None
    inverse_progress_marker: Optional[str] = None

    @staticmethod
    def create_null(name: str = 'null') -> NpcInfo:
        return NpcInfo(CharacterType.create_null(name), Point(), Direction.SOUTH, False)


class MapDecoration(NamedTuple):
    type: Optional[Decoration]
    point: Point  # Specifies the bottom, center tile of the decoration
    collision_rect: pygame.Rect
    dialog: Optional[DialogType] = None
    progress_marker: Optional[str] = None
    inverse_progress_marker: Optional[str] = None

    @staticmethod
    def create(type: Optional[Decoration],
               point: Point,
               dialog: Optional[DialogType] = None,
               progress_marker: Optional[str] = None,
               inverse_progress_marker: Optional[str] = None) -> MapDecoration:
        width_tiles = 1
        height_tiles = 1
        if type is not None:
            width_tiles = type.width_tiles
            height_tiles = type.height_tiles
        collision_rect = pygame.Rect(point.x-width_tiles//2, point.y-height_tiles+1, width_tiles, height_tiles)
        return MapDecoration(type, point, collision_rect, dialog, progress_marker, inverse_progress_marker)

    def overlaps(self, tile: Point) -> bool:
        return bool(self.collision_rect.collidepoint(tile.getAsIntTuple()))


class SpecialMonster(NamedTuple):
    monster_info: MonsterInfo
    point: Point
    approach_dialog: Optional[DialogType] = None
    victory_dialog: Optional[DialogType] = None
    run_away_dialog: Optional[DialogType] = None
    progress_marker: Optional[str] = None
    inverse_progress_marker: Optional[str] = None


class Map(NamedTuple):
    name: str
    tiled_filename: Optional[str]
    dat: List[str]
    overlay_dat: Optional[List[str]]
    music: str
    light_diameter: Optional[int]
    leaving_transition: Optional[OutgoingTransition]
    point_transitions: List[OutgoingTransition]
    transitions_by_map: Dict[str, AnyTransition]
    transitions_by_map_and_name: Dict[str, Dict[str, AnyTransition]]
    transitions_by_name: Dict[str, AnyTransition]
    map_decorations: List[MapDecoration]
    npcs: List[NpcInfo]
    monster_zones: List[MonsterZone]
    encounter_image: Optional[pygame.surface.Surface]
    special_monsters: List[SpecialMonster]
    is_outside: bool
    origin: Optional[Point] = None

    @staticmethod
    def create(name: str,
               dat: List[str]) -> Map:
        return Map(name,
                   None,
                   dat,
                   None,
                   '',
                   None,
                   None,
                   [],
                   {},
                   {},
                   {},
                   [],
                   [],
                   [],
                   None,
                   [],
                   False)


class MonsterAction(NamedTuple):
    name: str
    spell: Optional[Spell]
    target_type: TargetTypeEnum
    use_dialog: DialogType

    def is_spell(self) -> bool:
        return GameTypes.dialog_contains_action_category(self.use_dialog, ActionCategoryTypeEnum.MAGICAL)

    def is_damage_action(self) -> bool:
        return GameTypes.dialog_contains_action(self.use_dialog, DialogActionEnum.DAMAGE_TARGET)

    def is_heal_action(self) -> bool:
        return GameTypes.dialog_contains_action(self.use_dialog, DialogActionEnum.HEALTH_RESTORE)

    def is_sleep_action(self) -> bool:
        return GameTypes.dialog_contains_action(self.use_dialog, DialogActionEnum.SLEEP)

    def is_stopspell_action(self) -> bool:
        return GameTypes.dialog_contains_action(self.use_dialog, DialogActionEnum.STOPSPELL)

    def is_fire_attack(self) -> bool:
        return GameTypes.dialog_contains_action_category(self.use_dialog, ActionCategoryTypeEnum.FIRE)

    def get_damage_range(self) -> Tuple[int, int]:
        dialog_action = GameTypes.get_dialog_action(self.use_dialog, DialogActionEnum.DAMAGE_TARGET)
        if dialog_action is not None:
            return GameTypes.parse_int_range(dialog_action.count)
        return 0, 0


class MonsterActionRule(NamedTuple):
    action: MonsterAction
    probability: float
    health_ratio_threshold: float


class MonsterInfo(NamedTuple):
    name: str
    image: pygame.surface.Surface
    dmg_image: pygame.surface.Surface
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
    monster_action_rules: List[MonsterActionRule]
    allows_critical_hits: bool
    may_run_away: bool


class MonsterZone(NamedTuple):
    x: int
    y: int
    w: int
    h: int
    name: str


class NamedLocation(NamedTuple):
    name: str
    point: Point
    dir: Optional[Direction] = None


class Level(NamedTuple):
    number: int
    name: str
    xp: int
    strength: int
    agility: int
    hp: int
    mp: int
    spell: Optional[Spell] = None

    @staticmethod
    def create_null(name: str = 'null') -> Level:
        return Level(0, name, 0, 0, 0, 1, 0, None)


class Spell(NamedTuple):
    name: str
    mp: int
    available_in_combat: bool
    available_outside_combat: bool
    available_inside: bool
    available_outside: bool
    target_type: TargetTypeEnum
    use_dialog: DialogType


class Weapon(NamedTuple):
    name: str
    attack_bonus: int
    gp: int
    target_type: TargetTypeEnum = TargetTypeEnum.SINGLE_ENEMY
    use_dialog: DialogType = ['[ACTOR] attacks!', DialogAction(DialogActionEnum.DAMAGE_TARGET, count='default')]

    def __hash__(self) -> int:
        return hash('Weapon:' + self.name)


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
    hp_regen_tiles: Optional[int]


class Shield(NamedTuple):
    name: str
    defense_bonus: int
    gp: int


class Tool(NamedTuple):
    name: str
    attack_bonus: int = 0
    defense_bonus: int = 0
    gp: int = 0
    droppable: bool = True
    equippable: bool = False
    use_dialog: Optional[DialogType] = None
    target_type: TargetTypeEnum = TargetTypeEnum.SELF

    def __hash__(self) -> int:
        return hash('Tool:' + self.name)


ItemType = Union[Weapon, Helm, Armor, Shield, Tool]


class MapImageInfo(NamedTuple):
    name: str
    image: pygame.surface.Surface
    size_tiles: Point
    size_pixels: Point
    overlay_image: Optional[pygame.surface.Surface] = None

    @staticmethod
    def create_null() -> MapImageInfo:
        return MapImageInfo('',
                            pygame.surface.Surface((0, 0)),
                            Point(),
                            Point())


class EncounterBackground(NamedTuple):
    name: str
    image: pygame.surface.Surface


class Problem(NamedTuple):
    problem: str
    answer: str
    answer_allowed_characters: Optional[str] = None


def main() -> None:
    print(MonsterActionEnum.ATTACK.name)
    print(MonsterActionEnum.ATTACK.value)

    print('SOUTH' in Direction.__members__)
    print(Direction.SOUTH in Direction)


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
