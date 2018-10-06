#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Any, Dict, List, NamedTuple, Optional, Union

from dataclasses import dataclass
from collections import namedtuple
from enum import Enum
from Point import Point

class Direction(Enum):
   NORTH = 1
   SOUTH = 2
   WEST = 3
   EAST = 4

   def getDirectionVector( self ) -> Point:
      if Direction.NORTH == self:
         vector = Point( 0, -1 )
      elif Direction.SOUTH == self:
         vector = Point( 0, 1 )
      elif Direction.EAST == self:
         vector = Point( 1, 0 )
      else:
         vector = Point( -1, 0 )
      return vector

   def getOppositeDirection( self ) -> Direction:
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
   HAS_ITEM = 1                      # attributes: name (if unknown name, treated as a progress marker), count (defaults to 1)
   LACKS_ITEM = 2                    # attributes: name (if unknown name, treated as a progress marker), count (defaults to 1)
   IS_FACING_DOOR = 3                # attributes: <none>
   IS_OUTSIDE = 4                    # attributes: count (number, range, or unlimited)
   IS_INSIDE = 5                     # attributes: count (number, range, or unlimited)
   IS_DARK = 6                       # attributes: <none>
   IS_AT_COORDINATES = 7             # attributes: map, x, y
   IS_IN_COMBAT = 8                  # attributes: name (optional name of monster)
   IS_NOT_IN_COMBAT = 9              # attributes: <none>

# Actions that can be triggered from dialog
class DialogActionEnum(Enum):
   SAVE_GAME = 1                     # attributes: <none>
   MAGIC_RESTORE = 2                 # attributes: count (number, range, or unlimited)
   HEALTH_RESTORE = 3                # attributes: count (number, range, or unlimited)
   LOSE_ITEM = 4                     # attributes: item (if unknown name, treated as a progress marker), count (defaults to 1)
   GAIN_ITEM = 5                     # attributes: item (if unknown name, treated as a progress marker), count (defaults to 1)
   SET_LIGHT_DIAMETER = 6            # attributes: count, decay (number or unlimited)
   REPEL_MONSTERS = 7                # attributes: decay
   GOTO_COORDINATES = 8              # attributes: map, x, y, dir
   GOTO_LAST_OUTSIDE_COORDINATES = 9 # attributes: <none>
   PLAY_SOUND = 10                   # attributes: name
   PLAY_MUSIC = 11                   # attributes: name (currently play it once and return to looping on the prior music)
   VISUAL_EFFECT = 12                # attributes: name (fadeToBlackAndBack, flickering, rainbowEffect, darkness)
   ATTACK_MONSTER = 13               # attributes: name, victoryDialog (victoryDialogScript in XML), runAwayDialog (runAwayDialogScript in XML), encounterMusic
   OPEN_DOOR = 14                    # attributes: <none>
   MONSTER_SLEEP = 15                # attributes: bypass (to bypass resistances)
   MONSTER_STOP_SPELL = 16           # attributes: bypass (to bypass resistances)

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

# Set a variaable to be used in substitution for the remainder of the dialog session
@dataclass
class DialogVariable:
   name: str
   value: str
   
# Dialog to branch to a labeled dialog state
@dataclass
class DialogGoTo:
   label: str

# Dialog for a list of vendor buy options
@dataclass
class DialogVendorBuyOptions:
   # List of items that can be bought from the vendor where each item is a 2 element list: item name and gold cost (as str)
   # Optionally could also be a string for replacement by a DialogVariable
   DialogVendorBuyOptionsParamWithoutReplacementType = List[List[str]]
   DialogVendorBuyOptionsParamType = Union[DialogVendorBuyOptionsParamWithoutReplacementType, str]
   nameAndGpRowData: DialogVendorBuyOptionsParamType
   
@dataclass
class DialogVendorBuyOptionsVariable:
   name: str
   value: DialogVendorBuyOptions.DialogVendorBuyOptionsParamWithoutReplacementType
   
# Dialog for a list of vendor sell options
@dataclass
class DialogVendorSellOptions:
   # List of the classes of items that can be sold to the vendor
   # Optionally could also be a string for replacement by a DialogVariable
   DialogVendorSellOptionsParamWithoutReplacemenType = List[str]
   DialogVendorSellOptionsParamType = Union[DialogVendorSellOptionsParamWithoutReplacemenType, str]
   itemTypes: DialogVendorSellOptionsParamType

@dataclass
class DialogVendorSellOptionsVariable:
   name: str
   value: DialogVendorSellOptions.DialogVendorSellOptionsParamWithoutReplacemenType

# Conditionally branch dialog if the check condition is not met
@dataclass
class DialogCheck:
   type: DialogCheckEnum
   failedCheckDialog: Optional[DialogType]
   name: Optional[str] = None
   count: Union[int, str] = 1
   mapName: Optional[str] = None
   mapPos: Optional[Point] = None

# Conditionally branch dialog if the check condition is not met
@dataclass
class DialogAction:
   type: DialogActionEnum
   name: Optional[str] = None
   count: Union[int, str] = 1
   decaySteps: Optional[int] = None
   mapName: Optional[str] = None
   mapPos: Optional[Point] = None
   mapDir: Optional[Direction] = None
   victoryDialog: Optional[DialogType] = None
   runAwayDialog: Optional[DialogType] = None
   encounterMusic: Optional[str] = None

class Tile(NamedTuple):
   name: str
   symbol: str
   image: Union[pygame.Surface, List[pygame.Surface]]
   walkable: bool
   canTalkOver: bool
   hpPenalty: int
   mpPenalty: int
   speed: float
   spawnRate: float
   specialEdges: bool

class Decoration(NamedTuple):
   name: str
   image: pygame.Surface
   walkable: bool
   removeWithSearch: bool
   removeWithKey: bool

class CharacterType(NamedTuple):
   type: str
   images: Dict[Direction, pygame.Surface]

class LeavingTransition(NamedTuple):
   destMap: str
   destPoint: Point
   destDir: Direction
   respawnDecorations: bool

class PointTransition(NamedTuple):
   srcPoint: Point
   destMap: str
   destPoint: Point
   destDir: Direction
   respawnDecorations: bool
   progressMarker: Optional[str]
   inverseProgressMarker: Optional[str]

class NonPlayerCharacter(NamedTuple):
   type: str
   point: Point
   dir: Direction
   walking: bool
   dialog: Optional[DialogType]
   progressMarker: Optional[str]
   inverseProgressMarker: Optional[str]

class MapDecoration(NamedTuple):
   type: Optional[str]
   point: Point
   dialog: Optional[DialogType]
   progressMarker: Optional[str]
   inverseProgressMarker: Optional[str]

class SpecialMonster(NamedTuple):
   name: str
   point: Point
   victoryDialog: Optional[DialogType]
   runAwayDialog: Optional[DialogType]
   progressMarker: Optional[str]
   inverseProgressMarker: Optional[str]

class Map(NamedTuple):
   name: str
   dat: List[str]
   overlayDat: Optional[List[str]]
   size: Point
   music: str
   lightDiameter: Optional[int]
   leavingTransition: Optional[LeavingTransition]
   pointTransitions: List[PointTransition]
   nonPlayerCharacters: List[NonPlayerCharacter]
   mapDecorations: List[MapDecoration]
   monsterZones: List[MonsterZone]
   encounterImage: Optional[pygame.Surface]
   specialMonsters: List[SpecialMonster]
   isOutside: bool
   origin: Optional[Point]

class MonsterAction(NamedTuple):
   type: MonsterActionEnum
   probability: float
   healthRatioThreshold: float

class Monster(NamedTuple):
   name: str
   image: pygame.Surface
   dmgImage: pygame.Surface
   strength: int
   agility: int
   minHp: int
   maxHp: int
   sleepResist: float
   stopspellResist: float
   hurtResist: float
   dodge: float
   blockFactor: float
   xp: int
   minGp: int
   maxGp: int
   monsterActions: List[MonsterAction]

class MonsterZone(NamedTuple):
   x: int
   y: int
   w: int
   h: int
   setName: str

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
   availableInCombat: bool
   availableOutsideCombat: bool
   minHpRecover: int
   maxHpRecover: int
   minDamageByHero: int
   maxDamageByHero: int
   minDamageByMonster: int
   maxDamageByMonster: int
   excludedMap: Optional[str]
   includedMap: Optional[str]

class Weapon(NamedTuple):
   name: str
   attackBonus: int
   gp: int

class Helm(NamedTuple):
   name: str
   defenseBonus: int
   gp: int

class Armor(NamedTuple):
   name: str
   defenseBonus: int
   gp: int
   ignoresTilePenalties: bool
   hurtDmgModifier: float
   hpRegenTiles: int
   # TODO: Add fireDmbModified, stopspellBlock

class Shield(NamedTuple):
   name: str
   defenseBonus: int
   gp: int

@dataclass
class Tool:
   name: str
   attackBonus: int = 0
   defenseBonus: int = 0
   gp: int = 0
   droppable: bool = True
   equippable: bool = False
   useDialog: Optional[DialogType] = None

   def __hash__(self) -> int:
      return hash('Tool:' + self.name)

ItemType = Union[Weapon, Helm, Armor, Shield, Tool]
      
class MapImageInfo(NamedTuple):
   mapName: str
   mapImage: pygame.Surface
   mapImageSize_tiles: Point
   mapImageSize_pixels: Point
   mapOverlayImage: Optional[pygame.Surface]

# TODO: Where to put this???
import pygame
def scroll_view(screen: pygame.Surface,
                image: pygame.Surface,
                direction: Direction,
                view_rect: pygame.Rect,
                zoom_factor: int,
                imagePxStepSize: int,
                update: bool = False) -> None:
   dx = dy = 0
   src_rect = None
   zoom_view_rect = screen.get_clip()
   image_w, image_h = image.get_size()
    
   if direction == Direction.NORTH:
      if view_rect.top > 0:
         screen.scroll(dy=imagePxStepSize*zoom_factor)
         view_rect.move_ip(0, -imagePxStepSize)
         src_rect = view_rect.copy()
         src_rect.h = imagePxStepSize
         dst_rect = zoom_view_rect.copy()
         dst_rect.h = imagePxStepSize*zoom_factor
   elif direction == Direction.SOUTH:
      if view_rect.bottom < image_h:
         screen.scroll(dy=-imagePxStepSize*zoom_factor)
         view_rect.move_ip(0, imagePxStepSize)
         src_rect = view_rect.copy()
         src_rect.h = imagePxStepSize
         src_rect.bottom = view_rect.bottom
         dst_rect = zoom_view_rect.copy()
         dst_rect.h = imagePxStepSize*zoom_factor
         dst_rect.bottom = zoom_view_rect.bottom
   elif direction == Direction.WEST:
      if view_rect.left > 0:
         screen.scroll(dx=imagePxStepSize*zoom_factor)
         view_rect.move_ip(-imagePxStepSize, 0)
         src_rect = view_rect.copy()
         src_rect.w = imagePxStepSize
         dst_rect = zoom_view_rect.copy()
         dst_rect.w = imagePxStepSize*zoom_factor
   elif direction == Direction.EAST:
      if view_rect.right < image_w:
         screen.scroll(dx=-imagePxStepSize*zoom_factor)
         view_rect.move_ip(imagePxStepSize, 0)
         src_rect = view_rect.copy()
         src_rect.w = imagePxStepSize
         src_rect.right = view_rect.right
         dst_rect = zoom_view_rect.copy()
         dst_rect.w = imagePxStepSize*zoom_factor
         dst_rect.right = zoom_view_rect.right
   if src_rect is not None:
      pygame.transform.scale(image.subsurface(src_rect),
            dst_rect.size,
            screen.subsurface(dst_rect))
      if update:
         pygame.display.update(zoom_view_rect)

def main() -> None:
   pass

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
