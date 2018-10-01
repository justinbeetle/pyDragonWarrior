#!/usr/bin/env python

# Imports to support type annotations
from typing import Any, List, Optional

from typing import NamedTuple
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
      elif Direction.WEST == self:
         vector = Point( -1, 0 )
      else:
         vector = Point( 0, 0 )
      return vector

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

# Dialog to branch to a labeled dialog state
@dataclass
class DialogGoTo:
   label: str

# Dialog for a list of vendor buy options
@dataclass
class DialogVendorBuyOptions:
   nameAndGpRowData: List[List[str]] # List of items that can be bought from the vendor where each item is a 2 element list: item name and gold cost (as str)

# Dialog for a list of vendor sell options
@dataclass
class DialogVendorSellOptions:
   itemTypes: List[str] # List of the classes of items that can be sold to the vendor

# Conditionally branch dialog if the check condition is not met
@dataclass
class DialogCheck:
   type: DialogCheckEnum
   failedCheckDialog: Any # TODO: Better document this type
   name: Optional[str] = None
   count: int = 1
   mapName: Optional[str] = None
   mapPos: Optional[Point] = None

# Conditionally branch dialog if the check condition is not met
@dataclass
class DialogAction:
   type: DialogActionEnum
   name: Optional[str] = None
   count: int = 1
   decaySteps: Optional[int] = None
   mapName: Optional[str] = None
   mapPos: Optional[Point] = None
   mapDir: Optional[Direction] = None
   victoryDialog: Any = None # TODO: Better document this type
   runAwayDialog: Any = None # TODO: Better document this type
   encounterMusic: Optional[str] = None

# Set a variaable to be used in substitution for the remainder of the dialog session
@dataclass
class DialogVariable:
   name: str
   value: str

Tile = namedtuple('Tile', ['name',
                           'symbol',
                           'image',
                           'walkable',
                           'canTalkOver',
                           'hpPenalty',
                           'mpPenalty',
                           'speed',
                           'spawnRate',
                           'specialEdges'])

Decoration = namedtuple('Decoration', ['name',
                                       'image',
                                       'walkable',
                                       'removeWithSearch',
                                       'removeWithKey'])

CharacterType = namedtuple('CharacterType', ['type',
                                             'images'])

LeavingTransition = namedtuple('LeavingTransition', ['destMap',
                                                     'destPoint',
                                                     'destDir',
                                                     'respawnDecorations'])

PointTransition = namedtuple('PointTransition', ['srcPoint',
                                                 'destMap',
                                                 'destPoint',
                                                 'destDir',
                                                 'respawnDecorations',
                                                 'progressMarker',
                                                 'inverseProgressMarker'])

NonPlayerCharacter = namedtuple('NonPlayerCharacter', ['type',
                                                       'point',
                                                       'dir',
                                                       'walking',
                                                       'dialog',
                                                       'progressMarker',
                                                       'inverseProgressMarker'])

MapDecoration = namedtuple('MapDecoration', ['type',
                                             'point',
                                             'dialog',
                                             'progressMarker',
                                             'inverseProgressMarker'])

SpecialMonster = namedtuple('SpecialMonster', ['name',
                                               'point',
                                               'victoryDialog',
                                               'runAwayDialog',
                                               'progressMarker',
                                               'inverseProgressMarker'])

Map = namedtuple('Map', ['name',
                         'dat',
                         'overlayDat',
                         'size',
                         'music',
                         'lightDiameter',
                         'leavingTransition',
                         'pointTransitions',
                         'nonPlayerCharacters',
                         'mapDecorations',
                         'monsterZones',
                         'encounterImage',
                         'specialMonsters',
                         'isOutside',
                         'origin'])

MonsterAction = namedtuple('MonsterAction', ['type',
                                             'probability',
                                             'healthRatioThreshold'])

Monster = namedtuple('Monster', ['name',
                                 'image',
                                 'dmgImage',
                                 'strength',
                                 'agility',
                                 'minHp',
                                 'maxHp',
                                 'sleepResist',
                                 'stopspellResist',
                                 'hurtResist',
                                 'dodge',
                                 'blockFactor',
                                 'xp',
                                 'minGp',
                                 'maxGp',
                                 'monsterActions'])

MonsterZone = namedtuple('MonsterZone', ['x',
                                         'y',
                                         'w',
                                         'h',
                                         'setName'])

Level = namedtuple('Level', ['number',
                             'name',
                             'xp',
                             'strength',
                             'agility',
                             'hp',
                             'mp'])

Spell = namedtuple('Spell', ['name',
                             'level',
                             'mp',
                             'availableInCombat',
                             'availableOutsideCombat',
                             'minHpRecover',
                             'maxHpRecover',
                             'minDamageByHero',
                             'maxDamageByHero',
                             'minDamageByMonster',
                             'maxDamageByMonster',
                             'excludedMap',
                             'includedMap'])

Weapon = namedtuple('Weapon', ['name',
                               'attackBonus',
                               'gp'])

Helm = namedtuple('Helm', ['name',
                           'defenseBonus',
                           'gp'])

Armor = namedtuple('Armor', ['name',
                             'defenseBonus',
                             'gp',
                             'ignoresTilePenalties',
                             'hurtDmgModifier',
                             'hpRegenTiles']) # TODO: Add fireDmbModified, stopspellBlock

Shield = namedtuple('Shield', ['name',
                               'defenseBonus',
                               'gp'])

@dataclass
class Tool:
   name: str
   attackBonus: int
   defenseBonus: int
   gp: int
   droppable: bool
   equippable: bool
   useDialog: Any # TODO: Better document this type

   def __hash__(self):
      return hash('Tool:' + self.name)
      

MapImageInfo = namedtuple('MapImageInfo', ['mapName',
                                           'mapImage',
                                           'mapImageSize_tiles',
                                           'mapImageSize_pixels',
                                           'mapOverlayImage'])

# TODO: Where to put this???
import pygame
def scroll_view(screen, image, direction: Direction, view_rect, zoom_factor: int, imagePxStepSize: int, update: bool = False) -> None:
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
