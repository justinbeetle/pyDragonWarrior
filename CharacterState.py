#!/usr/bin/env python

import math
import random

from Point import Point
from GameTypes import *
from GameInfo import GameInfo

# For main only
import os
import pygame
from AudioPlayer import AudioPlayer

class CharacterState:
   def __init__(self, type, pos_datTile, dir, name, level, npcInfo = None ):
      self.type = type
      self.currPos_datTile = Point( pos_datTile )
      self.destPos_datTile = Point( pos_datTile )
      self.currPosOffset_imgPx = Point( 0, 0 )
      self.dir = dir
      self.npcInfo = npcInfo

      if name is not None:
         self.name = name
      else:
         self.name = 'Unnamed'
         
      if level is not None:
         self.level = level
         self.hp = level.hp
         self.mp = level.mp
         self.gp = 0
         self.xp = level.xp
      else:
         self.level = 'n/a'
         self.hp = 1
         self.mp = 0
         self.gp = 0
         self.xp = 0
         
      self.weapon = None

      self.helm = None
      self.armor = None
      self.shield = None

      self.otherEquippedItems = []
      self.unequippedItems = {} # Dictionary where keys are items and values are the item counts

   def createNpcState( npc ):
      return CharacterState( npc.type, npc.point, npc.dir, None, None, npc )

   def getItemRowData( self, limitToDropable = False, filterTypes = None ):
      itemRowData = []
      if self.weapon is not None:
         self.addItemToItemRowData( self.weapon, 'E', limitToDropable, filterTypes, itemRowData )
      if self.helm is not None:
         self.addItemToItemRowData( self.helm, 'E', limitToDropable, filterTypes, itemRowData )
      if self.armor is not None:
         self.addItemToItemRowData( self.armor, 'E', limitToDropable, filterTypes, itemRowData )
      if self.shield is not None:
         self.addItemToItemRowData( self.shield, 'E', limitToDropable, filterTypes, itemRowData )
      for item in self.otherEquippedItems:
         self.addItemToItemRowData( item, 'E', limitToDropable, filterTypes, itemRowData )
      for item in self.unequippedItems:
         self.addItemToItemRowData( item, str( self.unequippedItems[item] ), limitToDropable, filterTypes, itemRowData )
      return itemRowData

   def addItemToItemRowData( self, item, colValue, limitToDropable, filterTypes, itemRowData ):
      itemPassedTypeFilter = False
      if filterTypes is None:
         itemPassedTypeFilter = True
      else:
         for filterType in filterTypes:
            if filterType == 'Weapon' and isinstance( item, Weapon ):
               itemPassedTypeFilter = True
               break
            elif filterType == 'Helm' and isinstance( item, Helm ):
               itemPassedTypeFilter = True
               break
            elif filterType == 'Armor' and isinstance( item, Armor ):
               itemPassedTypeFilter = True
               break
            elif filterType == 'Tool' and isinstance( item, Tool ):
               itemPassedTypeFilter = True
               break
      if itemPassedTypeFilter and (not limitToDropable or not isinstance(item, Tool) or item.droppable):
         itemRowData.append( [item.name, colValue] )

   def isItemEquipped( self, itemName ):
      retVal = False
      if self.weapon is not None and itemName == self.weapon.name:
         retVal = True
      elif self.helm is not None and itemName == self.helm.name:
         retVal = True
      elif self.armor is not None and itemName == self.armor.name:
         retVal = True
      elif self.shield is not None and itemName == self.shield.name:
         retVal = True
      else:
         for item in self.otherEquippedItems:
            if itemName == item.name:
               retVal = True
               break
      return retVal

   def hasItem( self, itemName ):
      return self.getItemCount( itemName) > 0

   def getItemCount( self, itemName ):
      retVal = 0
      for item in self.unequippedItems:
         if itemName == item.name:
            retVal = self.unequippedItems[item]
            break
      if self.isItemEquipped( itemName ):
         retVal += 1
      return retVal

   def getItemOptions( self, itemName ):
      itemOptions = []
      isEquipped = False
      if self.isItemEquipped( itemName ):
         itemOptions.append( 'UNEQUIP' )
         itemOptions.append( 'DROP' ) # At present all equipable items are also droppable
         isEquipped = True
      for item in self.unequippedItems:
         if itemName == item.name:
            if (not isinstance(item, Tool) or item.equippable) and not isEquipped:
               itemOptions.append( 'EQUIP' )
            if isinstance(item, Tool) and item.usable:
               itemOptions.append( 'USE' )
            if (not isinstance(item, Tool) or item.droppable) and not isEquipped:
               itemOptions.append( 'DROP' )
            break
      return itemOptions

   def equipItem( self, itemName ):
      # Equip an unequipped item - may result in the unequiping of a previously equipped item
      if not self.isItemEquipped( itemName ):
         item = self.loseItem( itemName )
         if item is not None:
            if isinstance( item, Weapon ):
               if self.weapon is not None:
                  self.gainItem( self.weapon )
               self.weapon = item
            elif isinstance( item, Helm ):
               if self.helm is not None:
                  self.gainItem( self.helm )
               self.helm = item
            elif isinstance( item, Armor ):
               if self.armor is not None:
                  self.gainItem( self.armor )
               self.armor = item
            elif isinstance( item, Shield ):
               if self.shield is not None:
                  self.gainItem( self.shield )
               self.shield = item
            elif isinstance( item, Tool ) and item.equippable:
               self.otherEquippedItems.append( item )
            else:
               print( 'ERROR: Item cannot be equipped:', item, flush=True )
               self.gainItem( item )
         else:
            print( 'WARN: Item not in inventory:', itemName, flush=True )
      else:
         print( 'WARN: Item already equipped:', itemName, flush=True )
         
   def unequipItem( self, itemName ):
      # Unequip an equipped item by removing it as eqipped and adding it as unequipped
      if self.weapon is not None and itemName == self.weapon.name:
         self.gainItem( self.weapon )
         self.weapon = None
      elif self.helm is not None and itemName == self.helm.name:
         self.gainItem( self.helm )
         self.helm = None
      elif self.armor is not None and itemName == self.armor.name:
         self.gainItem( self.armor )
         self.armor = None
      elif self.shield is not None and itemName == self.shield.name:
         self.gainItem( self.shield )
         self.shield = None
      else:
         for item in self.otherEquippedItems:
            if itemName == item.name:
               self.gainItem( item )
               self.otherEquippedItems.remove( item )
               break

   def gainItem( self, item, count=1 ):
      # Gained items always go unequippedItems
      if item in self.unequippedItems:
         self.unequippedItems[item] += count
      else:
         self.unequippedItems[item] = count

   def useItem( self, itemName ):
      # Usable items are never (at least not yet) equippable
      for item in self.unequippedItems:
         if itemName == item.name:
            if item.consumeOnUse:
               self.loseItem( itemName )
            break

   def loseItem( self, itemName, count=1 ):
      # Lost items are taken from unequippedItems where possible, else equipped items
      retVal = None
      remainingItemsToLose = count
      for item in self.unequippedItems:
         if itemName == item.name:
            retVal = item
            self.unequippedItems[item] -= count
            if self.unequippedItems[item] <= 0:
               remainingItemsToLose = -self.unequippedItems[item]
               del self.unequippedItems[item]
               break
      if remainingItemsToLose > 0:
         if self.weapon is not None and itemName == self.weapon.name:
            retVal = self.weapon
            self.weapon = None
         elif self.helm is not None and itemName == self.helm.name:
            retVal = self.helm
            self.helm = None
         elif self.armor is not None and itemName == self.armor.name:
            retVal = self.armor
            self.armor = None
         elif self.shield is not None and itemName == self.shield.name:
            retVal = self.shield
            self.shield = None
         else:
            for item in self.otherEquippedItems:
               if itemName == item.name:
                  retVal = item
                  self.otherEquippedItems.remove( item )
                  break
      return retVal

   def getAttackStrength( self ):
      retVal = 0;
      if self.level is not None:
         retVal += self.level.strength // 2
      if self.weapon is not None:
         retVal += self.weapon.attackBonus
      for item in self.otherEquippedItems:
         retVal += item.attackBonus
      return math.floor(retVal)

   def getDefenseStrength( self ):
      retVal = 0;
      if self.level is not None:
         retVal += self.level.agility // 2
      if self.helm is not None:
         retVal += self.helm.defenseBonus
      if self.armor is not None:
         retVal += self.armor.defenseBonus
      if self.shield is not None:
         retVal += self.shield.defenseBonus
      for item in self.otherEquippedItems:
         retVal += item.defenseBonus
      return math.floor(retVal)

   def monsterRunCheck( self, monster ):
      if self.getAttackStrength() > monster.strength * 2:
         return random.uniform(0, 1) < 0.25
      return False

   def monsterInitiativeCheck( self, monster ):
      return self.level.agility * random.uniform(0, 1) < monster.agility * random.uniform(0, 1) * 0.25

   def monsterDodgeCheck( self, monster ):
      return random.uniform(0, 1) < monster.dodge

   def monsterBlockCheck( self, monster ):
      return self.level.agility * random.uniform(0, 1) < monster.agility * random.uniform(0, 1) * monster.blockFactor

   def criticalHitCheck( self, monster ):
      return random.uniform(0, 1) < 1/32

   def calcRegularHitDamageToMonster( self, monster ):
      return CharacterState.calcDamage(
         ( self.getAttackStrength() - monster.agility // 2 ) // 4,
         ( self.getAttackStrength() - monster.agility // 2 ) // 2 )

   def calcCriticalHitDamageToMonster( self, monster ):
      return CharacterState.calcDamage(
         self.getAttackStrength() // 2,
         self.getAttackStrength() )

   def calcHitDamageFromMonster( self, monster ):
      if self.getDefenseStrength() < monster.strength:
         return CharacterState.calcDamage(
            ( monster.strength - self.getDefenseStrength() // 2 ) // 4,
            ( monster.strength - self.getDefenseStrength() // 2 ) // 2 )
      else:
         return CharacterState.calcDamage(
            0,
            ( monster.strength + 4 ) // 6 )

   # TODO: Add spell checks and damage calc methods

   def calcDamage( minDamage, maxDamage ):
      #print( 'minDamage =', minDamage, flush=True )
      #print( 'maxDamage =', maxDamage, flush=True )
      damage = math.floor( minDamage + random.uniform(0, 1) * ( maxDamage - minDamage ) )
      if damage < 1:
         if random.uniform(0, 1) < 0.5:
            damage = 0
         else:
            damage = 1
      return damage

   def calcLevel( levels, xp ):
      for level in reversed(levels):
         if level.xp <= xp:
            return level
      return levels[0]

   def levelUpCheck( self, levels ):
      newLevel = CharacterState.calcLevel(levels, self.xp)
      leveledUp = self.level != newLevel
      self.level = newLevel
      return leveledUp

   def isIgnoringTilePenalties( self ):
      retVal = False
      if not retVal and self.helm is not None:
         retVal = self.helm.ignoresTilePenalties
      if not retVal and self.armor is not None:
         retVal = self.armor.ignoresTilePenalties
      return retVal

   def calcXpToNextLevel( self, levels ):
      retVal = 0
      for level in levels:
         if level.xp > self.level.xp:
            retVal = level.xp - self.xp
            break
      return retVal

   def __str__( self ):
      return "%s(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (
         self.__class__.__name__,
         self.name,
         self.level,
         self.hp,
         self.mp,
         self.gp,
         self.xp,
         self.type,
         self.currPos_datTile,
         self.destPos_datTile,
         self.currPosOffset_imgPx,
         self.dir)

   def __repr__( self ):
      return "%s(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)" % (
         self.__class__.__name__,
         self.name,
         self.level,
         self.hp,
         self.mp,
         self.gp,
         self.xp,
         self.type,
         self.currPos_datTile,
         self.destPos_datTile,
         self.currPosOffset_imgPx,
         self.dir)

def main():
   # Initialize pygame
   pygame.init()
   audioPlayer = AudioPlayer()
   screen = pygame.display.set_mode( (1, 1) )
   
   # Initialize GameInfo
   basePath = os.path.split(os.path.abspath(__file__))[0]
   gameXmlPath = os.path.join(basePath, 'game.xml')
   gameInfo = GameInfo( basePath, gameXmlPath, 16 )
   
   # Test out character states
   pcState = CharacterState( 'hero', Point(5,6), Direction.SOUTH, 'CAMDEN', gameInfo.levels['7'] )
   print( pcState, flush=True )
   pcState.hp += 2
   print( pcState, flush=True )
   for mapName in gameInfo.maps:
      for npc in gameInfo.maps[mapName].nonPlayerCharacters:
         npcState = CharacterState.createNpcState( npc )
         print( npcState, flush=True )

   # Terminate pygame
   audioPlayer.terminate()
   pygame.quit()

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
