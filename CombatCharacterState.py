#!/usr/bin/env python

import abc

class CombatCharacterState( metaclass=abc.ABCMeta ):
   def __init__(self, hp: int, maxHp: int = 0 ) -> None:
      self.hp = hp
      self.maxHp = max(hp, maxHp)
      self.clearCombatStatusAffects()

   def clearCombatStatusAffects(self) -> None:
      self.isAsleep = False
      self.turnsAsleep = 0
      self.areSpellsBlocked = False
      self.hasRunAway = False

   def isAlive(self) -> bool:
      return self.hp > 0

   def isDead(self) -> bool:
      return not self.isAlive()

   def isStillInCombat(self) -> bool:
      return self.isAlive() and not self.hasRunAway

   # Determine if character should remain asleep.  Should maintain turnsAsleep.
   @abc.abstractmethod
   def isStillAsleep(self) -> bool:
      raise NotImplementedError

   @abc.abstractmethod
   def getStrength(self) -> int:
      raise NotImplementedError

   @abc.abstractmethod
   def getAgility( self ) -> int:
      raise NotImplementedError

   @abc.abstractmethod
   def getAttackStrength( self ) -> int:
      raise NotImplementedError

   @abc.abstractmethod
   def getDefenseStrength( self ) -> int:
      raise NotImplementedError

   @abc.abstractmethod
   def allowsCriticalHits( self ) -> bool:
      raise NotImplementedError

   def __str__( self ) -> str:
      return "%s(%s, %s, %s, %s, %s)" % (
         self.__class__.__name__,
         self.hp,
         self.maxHp,
         self.isAsleep,
         self.turnsAsleep,
         self.areSpellsBlocked)

   def __repr__( self ) -> str:
      return "%s(%r, %r, %r, %r, %r)" % (
         self.__class__.__name__,
         self.hp,
         self.maxHp,
         self.isAsleep,
         self.turnsAsleep,
         self.areSpellsBlocked)
