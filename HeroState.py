#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Dict, List, Optional, Union

import math
import random

from MapCharacterState import MapCharacterState
from CombatCharacterState import CombatCharacterState
from Point import Point
from GameTypes import Armor, Direction, Helm, ItemType, Level, Shield, Tool, Weapon

class HeroState(MapCharacterState, CombatCharacterState):
   def __init__( self,
                 type: str,
                 pos_datTile: Point,
                 dir: Direction,
                 name: str,
                 level: Level ) -> None:

      MapCharacterState.__init__( self, type, pos_datTile, dir )
      CombatCharacterState.__init__( self, hp=level.hp )

      self.name = name
      self.level = level

      self.mp = level.mp
      self.gp = 0
      self.xp = level.xp
         
      self.weapon: Optional[Weapon] = None

      self.helm: Optional[Helm] = None
      self.armor: Optional[Armor] = None
      self.shield: Optional[Shield] = None

      self.otherEquippedItems: List[Tool] = []
      self.unequippedItems: Dict[ItemType, int] = {} # Dictionary where keys are items and values are the item counts
      self.progressMarkers: List[str] = []

   def getItemRowData( self, limitToDropable: bool = False, filterTypes: Optional[List[str]] = None ) -> List[List[str]]:
      itemRowData: List[List[str]] = []
      if self.weapon is not None:
         self.addItemToItemRowData( self.weapon, 'E', limitToDropable, filterTypes, itemRowData )
      if self.helm is not None:
         self.addItemToItemRowData( self.helm, 'E', limitToDropable, filterTypes, itemRowData )
      if self.armor is not None:
         self.addItemToItemRowData( self.armor, 'E', limitToDropable, filterTypes, itemRowData )
      if self.shield is not None:
         self.addItemToItemRowData( self.shield, 'E', limitToDropable, filterTypes, itemRowData )
      #for item in self.otherEquippedItems:
      for tool in sorted(self.otherEquippedItems, key=lambda tool: tool.name):
         self.addItemToItemRowData( tool, 'E', limitToDropable, filterTypes, itemRowData )
      #for item in self.unequippedItems:
      for item in sorted(self.unequippedItems, key=lambda item: item.name):
         self.addItemToItemRowData( item, str( self.unequippedItems[item] ), limitToDropable, filterTypes, itemRowData )
      return itemRowData

   def addItemToItemRowData( self, item: ItemType, colValue: str, limitToDropable: bool, filterTypes: Optional[List[str]], itemRowData: List[List[str]] ) -> None:
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
            elif filterType == 'Shield' and isinstance( item, Shield ):
               itemPassedTypeFilter = True
               break
            elif filterType == 'Tool' and isinstance( item, Tool ):
               itemPassedTypeFilter = True
               break
      if itemPassedTypeFilter and (not limitToDropable or not isinstance(item, Tool) or item.droppable):
         itemRowData.append( [item.name, colValue] )

   def isItemEquipped( self, itemName: str ) -> bool:
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

   def hasItem( self, itemName: str ) -> bool:
      return self.getItemCount( itemName) > 0

   def getItemCount( self, itemName: str ) -> int:
      retVal = 0
      for item in self.unequippedItems:
         if itemName == item.name:
            retVal = self.unequippedItems[item]
            break
      if self.isItemEquipped( itemName ):
         retVal += 1
      if itemName in self.progressMarkers:
         retVal += 1
      return retVal

   def getItemOptions( self, itemName: str ) -> List[str]:
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
            if isinstance(item, Tool) and item.useDialog is not None:
               itemOptions.append( 'USE' )
            if (not isinstance(item, Tool) or item.droppable) and not isEquipped:
               itemOptions.append( 'DROP' )
            break
      return itemOptions

   def equipItem( self, itemName: str ) -> None:
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
         
   def unequipItem( self, itemName: str ) -> None:
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

   def gainItem( self, item: Union[ItemType, str], count: int = 1 ) -> None:
      # Gained items always go unequippedItems
      if isinstance(item, str):
         if item not in self.progressMarkers:
            self.progressMarkers.append( item )
            #print( 'Added progress marker', item, flush=True )
         else:
            print( 'WARN: Did not add previously added progress marker', item, flush=True )
      elif item in self.unequippedItems:
         self.unequippedItems[item] += count
      else:
         self.unequippedItems[item] = count

   def loseItem( self, itemName: str, count: int = 1 ) -> Optional[ItemType]:
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
            remainingItemsToLose -= 1
         elif self.helm is not None and itemName == self.helm.name:
            retVal = self.helm
            self.helm = None
            remainingItemsToLose -= 1
         elif self.armor is not None and itemName == self.armor.name:
            retVal = self.armor
            self.armor = None
            remainingItemsToLose -= 1
         elif self.shield is not None and itemName == self.shield.name:
            retVal = self.shield
            self.shield = None
            remainingItemsToLose -= 1
         elif itemName in self.progressMarkers:
            self.progressMarkers.remove( itemName )
            remainingItemsToLose -= 1
            #print( 'Removed progress marker', itemName, flush=True )
         else:
            for item in self.otherEquippedItems:
               if itemName == item.name:
                  retVal = item
                  self.otherEquippedItems.remove( item )
                  remainingItemsToLose -= 1
                  break
      return retVal

   def isStillAsleep(self) -> bool:
      retVal = self.isAsleep and (self.turnsAsleep == 0 or random.uniform(0, 1) > 0.5)
      if retVal:
         self.turnsAsleep += 1
      else:
         self.isAsleep = False
         self.turnsAsleep = 0
      return retVal

   def getStrength( self ) -> int:
      return self.level.strength

   def getAgility( self ) -> int:
      return self.level.agility

   def getAttackStrength( self ) -> int:
      retVal = self.getStrength()
      if self.weapon is not None:
         retVal += self.weapon.attackBonus
      for item in self.otherEquippedItems:
         retVal += item.attackBonus
      return math.floor(retVal)

   def getDefenseStrength( self ) -> int:
      retVal = self.getAgility() // 2
      if self.helm is not None:
         retVal += self.helm.defenseBonus
      if self.armor is not None:
         retVal += self.armor.defenseBonus
      if self.shield is not None:
         retVal += self.shield.defenseBonus
      for item in self.otherEquippedItems:
         retVal += item.defenseBonus
      return retVal

   def allowsCriticalHits( self ) -> bool:
      return False

   def criticalHitCheck( self, monster: MonsterState ) -> bool:
      return random.uniform(0, 1) < 1/32

   def calcRegularHitDamageToMonster( self, monster: MonsterState ) -> int:
      return HeroState.calcDamage(
         ( self.getAttackStrength() - monster.getAgility() // 2 ) // 4,
         ( self.getAttackStrength() - monster.getAgility() // 2 ) // 2 )

   def calcCriticalHitDamageToMonster( self, monster: MonsterState ) -> int:
      return HeroState.calcDamage(
         self.getAttackStrength() // 2,
         self.getAttackStrength() )

   def calcHitDamageFromMonster( self, monster: MonsterState ) -> int:
      if self.getDefenseStrength() < monster.getStrength():
         return HeroState.calcDamage(
            ( monster.getStrength() - self.getDefenseStrength() // 2 ) // 4,
            ( monster.getStrength() - self.getDefenseStrength() // 2 ) // 2 )
      else:
         return HeroState.calcDamage(
            0,
            ( monster.getStrength() + 4 ) // 6 )

   # TODO: Add spell checks and damage calc methods

   @staticmethod
   def calcDamage( minDamage: int, maxDamage: int ) -> int:
      #print( 'minDamage =', minDamage, flush=True )
      #print( 'maxDamage =', maxDamage, flush=True )
      damage = math.floor( minDamage + random.uniform(0, 1) * ( maxDamage - minDamage ) )
      if damage < 1:
         if random.uniform(0, 1) < 0.5:
            damage = 0
         else:
            damage = 1
      return damage

   @staticmethod
   def calcLevel( levels: List[Level], xp: int ) -> Level:
      for level in reversed(levels):
         if level.xp <= xp:
            return level
      return levels[0]

   def levelUpCheck( self, levels: List[Level] ) -> bool:
      leveledUp = False
      if self.level is not None:
         newLevel = HeroState.calcLevel(levels, self.xp)
         leveledUp = self.level != newLevel
         self.level = newLevel
      return leveledUp

   def isIgnoringTilePenalties( self ) -> bool:
      retVal = False
      if not retVal and self.armor is not None:
         retVal = self.armor.ignoresTilePenalties
      return retVal

   def calcXpToNextLevel( self, levels: List[Level] ) -> int:
      retVal = 0
      if self.level is not None:
         for level in levels:
            if level.xp > self.level.xp:
               retVal = level.xp - self.xp
               break
      return retVal

   def __str__( self ) -> str:
      return "%s(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (
         self.__class__.__name__,
         self.name,
         self.level,
         self.hp,
         self.mp,
         self.gp,
         self.xp,
         self.typeName,
         self.currPos_datTile,
         self.destPos_datTile,
         self.currPosOffset_imgPx,
         self.dir)

   def __repr__( self ) -> str:
      return "%s(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)" % (
         self.__class__.__name__,
         self.name,
         self.level,
         self.hp,
         self.mp,
         self.gp,
         self.xp,
         self.typeName,
         self.currPos_datTile,
         self.destPos_datTile,
         self.currPosOffset_imgPx,
         self.dir)

def main() -> None:
   # Test out character states
   level = Level( 0, '1', 2, 3, 4, 25, 6 )
   heroState = HeroState( 'hero', Point(7,3), Direction.WEST, 'Sir Me', level )
   print( heroState, flush=True )
   while heroState.isAlive():
      heroState.hp -= 10
      print( heroState, flush=True )

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
