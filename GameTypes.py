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

class DialogActionEnum(Enum):
   SAVE_GAME = 1
   MAGIC_RESTORE = 2
   NIGHT_AT_INN = 3
   LOSE_ITEM = 4
   GAIN_ITEM = 5

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

class DialogCheck:
   def __init__(self, itemName, itemCount, failedCheckDialog ):
      self.itemName = itemName
      self.itemCount = itemCount
      self.failedCheckDialog = failedCheckDialog
      
   def __str__(self):
      return "%s(%s, %s, %s)" % (self.__class__.__name__, self.itemName, self.itemCount, self.failedCheckDialog)

class DialogAction:
   def __init__(self, type, itemName = None, itemCount = 1):
      self.type = type
      self.itemName = itemName
      self.itemCount = itemCount
      
   def __str__(self):
      return "%s(%s, %s, %s)" % (self.__class__.__name__, self.type, self.itemName, self.itemCount)

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
                                                     'destDir'], verbose=False)

PointTransition = namedtuple('PointTransition', ['srcPoint',
                                                 'destMap',
                                                 'destPoint',
                                                 'destDir'], verbose=False)

NonPlayerCharacter = namedtuple('NonPlayerCharacter', ['type',
                                                       'point',
                                                       'dir',
                                                       'walking',
                                                       'dialog'], verbose=False)

MapDecoration = namedtuple('MapDecoration', ['type',
                                             'point',
                                             'dialog'], verbose=False)

SpecialMonster = namedtuple('SpecialMonster', ['name',
                                               'point'], verbose=False)

Map = namedtuple('Map', ['name',
                         'dat',
                         'overlayDat',
                         'size',
                         'music',
                         'lightRadius',
                         'leavingTransition',
                         'pointTransitions',
                         'nonPlayerCharacters',
                         'mapDecorations',
                         'monsterZones',
                         'encounterImage',
                         'specialMonsters'], verbose=False)

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
                                 'maxGp'], verbose=False)

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
                             'hpRegenTiles'], verbose=False)

Shield = namedtuple('Shield', ['name',
                               'defenseBonus',
                               'gp'], verbose=False)

Tool = namedtuple('Tool', ['name',
                           'attackBonus',
                           'defenseBonus',
                           'minHpRecover',
                           'maxHpRecover',
                           'lightRadius',
                           'gp',
                           'droppable',
                           'equippable',
                           'usable',
                           'consumeOnUse'], verbose=False)

MapImageInfo = namedtuple('MapImageInfo', ['mapName',
                                           'mapImage',
                                           'mapImageSize_tiles',
                                           'mapImageSize_pixels'], verbose=False)

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
