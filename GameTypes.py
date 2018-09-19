#!/usr/bin/env python

from collections import namedtuple
from enum import Enum
from Point import Point

class Direction(Enum):
   NORTH = 1
   SOUTH = 2
   WEST = 3
   EAST = 4
   
def getDirectionVector( dir ):
   if Direction.NORTH == dir:
      vector = Point( 0, -1 )
   elif Direction.SOUTH == dir:
      vector = Point( 0, 1 )
   elif Direction.EAST == dir:
      vector = Point( 1, 0 )
   elif Direction.WEST == dir:
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

# Branch to a labeled dialog state
class DialogGoTo:
   def __init__(self, label):
      self.label = label
      
   def __str__(self):
      return "%s(%s)" % (self.__class__.__name__, self.label)

class DialogVendorBuyOptions:
   def __init__(self, nameAndGpRowData):
      self.nameAndGpRowData = nameAndGpRowData
      
   def __str__(self):
      return "%s(%s)" % (self.__class__.__name__, self.nameAndGpRowData)

class DialogVendorSellOptions:
   def __init__(self, itemTypes):
      self.itemTypes = itemTypes
      
   def __str__(self):
      return "%s(%s)" % (self.__class__.__name__, self.itemTypes)

# Conditionally branch dialog if the check condition is not met
class DialogCheck:
   def __init__(self,
                type,
                failedCheckDialog,
                name = None,
                count = 1,
                mapName = None,
                mapPos = None ):
      self.type = type
      self.failedCheckDialog = failedCheckDialog
      self.name = name
      self.count = count
      self.mapName = mapName
      self.mapPos = mapPos
      
   def __str__(self):
      return "%s(%s, %s, %s, %s, %s, %s)" % (self.__class__.__name__,
                                             self.type,
                                             self.failedCheckDialog,
                                             self.name,
                                             self.count,
                                             self.mapName,
                                             self.mapPos)

# Conditionally branch dialog if the check condition is not met
class DialogAction:
   def __init__(self,
                type,
                name = None,
                count = 1,
                decaySteps = None,
                mapName = None,
                mapPos = None,
                mapDir = None,
                victoryDialog = None,
                runAwayDialog = None,
                encounterMusic = None):
      self.type = type
      self.name = name
      self.count = count
      self.decaySteps = decaySteps
      self.mapName = mapName
      self.mapPos = mapPos
      self.mapDir = mapDir
      self.victoryDialog = victoryDialog
      self.runAwayDialog = runAwayDialog
      self.encounterMusic = encounterMusic
      
   def __str__(self):
      return "%s(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.__class__.__name__,
                                                             self.type,
                                                             self.name,
                                                             self.count,
                                                             self.decaySteps,
                                                             self.mapName,
                                                             self.mapPos,
                                                             self.mapDir,
                                                             self.victoryDialog,
                                                             self.runAwayDialog,
                                                             self.encounterMusic)

# Set a variaable to be used in substitution for the remainder of the dialog session
class DialogVariable:
   def __init__(self, name, value):
      self.name = name
      self.value = value
      
   def __str__(self):
      return "%s(%s, %s)" % (self.__class__.__name__, self.name, self.value)

Tile = namedtuple('Tile', ['name',
                           'symbol',
                           'image',
                           'walkable',
                           'canTalkOver',
                           'hpPenalty',
                           'mpPenalty',
                           'speed',
                           'spawnRate',
                           'specialEdges'], verbose=False)

Decoration = namedtuple('Decoration', ['name',
                                       'image',
                                       'walkable',
                                       'removeWithSearch',
                                       'removeWithKey'], verbose=False)

CharacterType = namedtuple('CharacterType', ['type',
                                             'images'], verbose=False)

LeavingTransition = namedtuple('LeavingTransition', ['destMap',
                                                     'destPoint',
                                                     'destDir',
                                                     'respawnDecorations'], verbose=False)

PointTransition = namedtuple('PointTransition', ['srcPoint',
                                                 'destMap',
                                                 'destPoint',
                                                 'destDir',
                                                 'respawnDecorations',
                                                 'progressMarker',
                                                 'inverseProgressMarker'], verbose=False)

NonPlayerCharacter = namedtuple('NonPlayerCharacter', ['type',
                                                       'point',
                                                       'dir',
                                                       'walking',
                                                       'dialog',
                                                       'progressMarker',
                                                       'inverseProgressMarker'], verbose=False)

MapDecoration = namedtuple('MapDecoration', ['type',
                                             'point',
                                             'dialog',
                                             'progressMarker',
                                             'inverseProgressMarker'], verbose=False)

SpecialMonster = namedtuple('SpecialMonster', ['name',
                                               'point',
                                               'victoryDialog',
                                               'runAwayDialog',
                                               'progressMarker',
                                               'inverseProgressMarker'], verbose=False)

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
                         'origin'], verbose=False)

MonsterAction = namedtuple('MonsterAction', ['type',
                                             'probability',
                                             'healthRatioThreshold'], verbose=False)

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
                                 'monsterActions'], verbose=False)

MonsterZone = namedtuple('MonsterZone', ['x',
                                         'y',
                                         'w',
                                         'h',
                                         'setName'], verbose=False)

Level = namedtuple('Level', ['number',
                             'name',
                             'xp',
                             'strength',
                             'agility',
                             'hp',
                             'mp'], verbose=False)

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
                             'includedMap'], verbose=False)

Weapon = namedtuple('Weapon', ['name',
                               'attackBonus',
                               'gp'], verbose=False)

Helm = namedtuple('Helm', ['name',
                           'defenseBonus',
                           'gp'], verbose=False)

Armor = namedtuple('Armor', ['name',
                             'defenseBonus',
                             'gp',
                             'ignoresTilePenalties',
                             'hurtDmgModifier',
                             'hpRegenTiles'], verbose=False) # TODO: Add fireDmbModified, stopspellBlock

Shield = namedtuple('Shield', ['name',
                               'defenseBonus',
                               'gp'], verbose=False)

# Tool as class as the namedtuple variant wasn't hashable for use in a dict
class Tool:
   def __init__(self, name, attackBonus, defenseBonus, gp, droppable, equippable, useDialog):
      self.name = name
      self.attackBonus = attackBonus
      self.defenseBonus = defenseBonus
      self.gp = gp
      self.droppable = droppable
      self.equippable = equippable
      self.useDialog = useDialog
      
   def __str__(self):
      return "%s(%s, %s, %s, %s, %s, %s, %s)" % (self.__class__.__name__, self.name, self.attackBonus, self.defenseBonus, self.gp, self.droppable, self.equippable, self.useDialog)
   

MapImageInfo = namedtuple('MapImageInfo', ['mapName',
                                           'mapImage',
                                           'mapImageSize_tiles',
                                           'mapImageSize_pixels',
                                           'mapOverlayImage'], verbose=False)

# TODO: Where to put this???
import pygame
def scroll_view(screen, image, direction, view_rect, zoom_factor, imagePxStepSize, update = False):
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
