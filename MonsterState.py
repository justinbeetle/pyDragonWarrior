#!/usr/bin/env python

from typing import Optional
import random

from CombatCharacterState import CombatCharacterState
from GameTypes import Monster, SpecialMonster
from GameDialog import GameDialog

class MonsterState(CombatCharacterState):
   def __init__( self, monsterInfo: Monster, specialMonsterInfo: Optional[SpecialMonster] = None ) -> None:
      super(MonsterState, self).__init__( hp=random.randint(monsterInfo.minHp, monsterInfo.maxHp) )
      self.monsterInfo = monsterInfo
      self.specialMonsterInfo = specialMonsterInfo
      self.gp = random.randint(monsterInfo.minGp, monsterInfo.maxGp)
      self.xp = monsterInfo.xp # TODO: Should this also come from a range?

   def isStillAsleep(self) -> bool:
      retVal = self.isAsleep and (self.turnsAsleep == 0 or random.uniform(0, 1) > 1.0 / 3.0)
      if retVal:
         self.turnsAsleep += 1
      else:
         self.isAsleep = False
         self.turnsAsleep = 0
      return retVal

   def getStrength( self ) -> int:
      return self.monsterInfo.strength

   def getAgility( self ) -> int:
      return self.monsterInfo.agility

   def getAttackStrength( self ) -> int:
      return self.getStrength()

   def getDefenseStrength( self ) -> int:
      return self.getAgility()

   def allowsCriticalHits( self ) -> bool:
      # TODO: Remove this hack
      return not self.monsterInfo.name.startswith('Dragonlord')

   # Determine if the monster has the initiative and attacks first in an encounter
   def hasInitiative( self, heroState: CombatCharacterState ) -> bool:
      return heroState.getAgility() * random.uniform(0, 1) <  self.getAgility() * random.uniform(0, 1) * 0.25

   # Determine if the monster will attempt to run away
   def shouldRunAway( self, heroState: CombatCharacterState ) -> bool:
      return heroState.getStrength() > self.getStrength() * 2 and random.uniform(0, 1) < 0.25

   # Determine if the monster dodges an attack
   def isDodgingAttack( self ) -> bool:
       return not self.isAsleep and random.uniform(0, 1) < self.monsterInfo.dodge

   # Determine if the monster blocks an attempt by the hero to run away
   def isBlockingEscape( self, heroState: CombatCharacterState ) -> bool:
      return not self.isAsleep and heroState.getAgility() * random.uniform(0, 1) <  self.getAgility() * random.uniform(0, 1) * self.monsterInfo.blockFactor

   def shouldWakeUp( self ) -> bool:
      return self.turnsAsleep > 0 and random.uniform(0, 1) < 1.0 / 3.0

   # Perform a turn for the monster in the encounter with the hero
   def performTurn( self, heroState: CombatCharacterState, messageDialog: GameDialog ) -> None:
      # If monster is asleep, determine whether it stays asleep or wakes up
      if self.isAsleep:
         if self.isStillAslepp():
            messageDialog.addMessage( 'The ' + monster.name + ' is still asleep.' )
            return
         else:
            messageDialog.addMessage('The ' + monster.name + ' awakes.')

      # Determine is monster will run away
      if self.shouldRunAway( heroState ):
          self.hasRunAway = True
          messageDialog.addMessage('The ' + monster.name + ' is running away.')
          return

      # Determine monster action
      chosenMonsterAction = MonsterActionEnum.ATTACK
      for monsterAction in monster.monsterActions:
         if self.hp / self.maxHp > monsterAction.healthRatioThreshold:
            continue
         if MonsterActionEnum.SLEEP == monsterAction.type and heroState.isAsleep:
            continue
         if MonsterActionEnum.STOPSPELL == monsterAction.type and heroState.areSpellsBlocked:
            continue
         if random.uniform(0, 1) < monsterAction.probability:
            chosenMonsterAction = monsterAction.type
            break

      # Perform monster action
      damage = 0
      if chosenMonsterAction == MonsterActionEnum.HEAL or chosenMonsterAction == MonsterActionEnum.HEALMORE:
         AudioPlayer().playSound( 'castSpell.wav' )
         SurfaceEffects.flickering( self.gameState.screen )
         if chosenMonsterAction == MonsterActionEnum.HEAL:
            messageDialog.addMessage( 'The ' + monster.name + ' chants the spell of heal.' )
         else:
            messageDialog.addMessage( 'The ' + monster.name + ' chants the spell of healmore.' )
         if monster_stopspelled:
            messageDialog.addMessage( 'But that spell hath been blocked.' )
         else:
            messageDialog.addMessage( 'The ' + monster.name + ' hath recovered.' )
            monster_hp = monster_max_hp
      elif chosenMonsterAction == MonsterActionEnum.HURT or chosenMonsterAction == MonsterActionEnum.HURTMORE:
         AudioPlayer().playSound( 'castSpell.wav' )
         SurfaceEffects.flickering( self.gameState.screen )
         if chosenMonsterAction == MonsterActionEnum.HURT:
            messageDialog.addMessage( 'The ' + monster.name + ' chants the spell of hurt.' )
            damage = random.randint( self.gameState.gameInfo.spells['Hurt'].minDamageByMonster, self.gameState.gameInfo.spells['Hurt'].maxDamageByMonster )
         else:
            messageDialog.addMessage( 'The ' + monster.name + ' chants the spell of hurtmore.' )
            damage = random.randint( self.gameState.gameInfo.spells['Hurtmore'].minDamageByMonster, self.gameState.gameInfo.spells['Hurtmore'].maxDamageByMonster )
         if self.gameState.pc.armor is not None:
            damage = round(damage * self.gameState.pc.armor.hurtDmgModifier)
         if monster_stopspelled:
            messageDialog.addMessage( 'But that spell hath been blocked.' )
            damage = 0
      elif chosenMonsterAction == MonsterActionEnum.SLEEP:
         AudioPlayer().playSound( 'castSpell.wav' )
         SurfaceEffects.flickering( self.gameState.screen )
         messageDialog.addMessage( 'The ' + monster.name + ' chants the spell of sleep.' )
         if monster_stopspelled:
            messageDialog.addMessage( 'But that spell hath been blocked.' )
         else:
            messageDialog.addMessage( 'Thou art asleep.' )
            player_asleep = True
      elif chosenMonsterAction == MonsterActionEnum.STOPSPELL:
         AudioPlayer().playSound( 'castSpell.wav' )
         SurfaceEffects.flickering( self.gameState.screen )
         messageDialog.addMessage( 'The ' + monster.name + ' chants the spell of stopspell.' )
         if monster_stopspelled:
            messageDialog.addMessage( 'But that spell hath been blocked.' )
         # TODO: Should always be blocked by certain items - Erdrick's Armor
         elif random.uniform(0, 1) < 0.5:
            messageDialog.addMessage( self.gameState.pc.name + ' spells hath been blocked.' )
            player_stopspelled = True
         else:
            messageDialog.addMessage( 'But that spell did not work.' )
      elif chosenMonsterAction == MonsterActionEnum.BREATH_FIRE or chosenMonsterAction == MonsterActionEnum.BREATH_STRONG_FIRE:
         AudioPlayer().playSound( 'fireBreathingAttack.wav' )
         messageDialog.addMessage( 'The ' + monster.name + ' is breathing fire.' )
         if chosenMonsterAction == MonsterActionEnum.BREATH_FIRE:
            damage = random.randint(16, 23)
         else:
            damage = random.randint(65, 72)
         # TODO: Apply armor damage reduction
      else: # chosenMonsterAction == MonsterActionEnum.ATTACK
         damage = self.gameState.pc.calcHitDamageFromMonster( monster )
         if 0 == damage:
            # TODO: Play sound?
            messageDialog.addMessage( 'The ' + monster.name + ' attacks! ' + self.gameState.pc.name + ' dodges the strike.' )
         else:
            audioPlayer.playSound( 'Dragon Warrior [Dragon Quest] SFX (5).wav' )
            messageDialog.addMessage( 'The ' + monster.name + ' attacks!' )

      if damage != 0:
         messageDialog.addMessage( 'Thy hit points reduced by ' + str(damage) + '.' )
         self.gameState.pc.hp -= damage
         if self.gameState.pc.hp < 0:
            self.gameState.pc.hp = 0
         for flickerTimes in range( 10 ):
            offset_pixels = Point( damageFlickerPixels, damageFlickerPixels )
            self.gameState.screen.blit( origScreen, (0, 0) )
            self.gameState.screen.blit( encounterImage, encounterImageDest_pixels )
            self.gameState.screen.blit( monster.image, monsterImageDest_pixels )
            GameDialog.createEncounterStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False, offset_pixels )
            messageDialog.blit( self.gameState.screen, True, offset_pixels )
            pygame.time.Clock().tick(30)
            self.gameState.screen.blit( origScreen, (0, 0) )
            self.gameState.screen.blit( encounterImage, encounterImageDest_pixels )
            self.gameState.screen.blit( monster.image, monsterImageDest_pixels )
            GameDialog.createEncounterStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )
            messageDialog.blit( self.gameState.screen, True )
            pygame.time.Clock().tick(30)

   def __str__( self ) -> str:
      return "%s(%s, %s, %s, %s, %s)" % (
         self.__class__.__name__,
         super(MonsterState, self).__str__(),
         self.monsterInfo,
         self.specialMonsterInfo,
         self.gp,
         self.xp)

   def __repr__( self ) -> str:
      return "%s(%r, %r, %r, %r, %r)" % (
         self.__class__.__name__,
         super(MonsterState, self).__repr__(),
         self.monsterInfo,
         self.specialMonsterInfo,
         self.gp,
         self.xp)

def main() -> None:
   import pygame
   monsterInfo = Monster( name='MonsterName',
                          image=pygame.Surface( (0, 0) ),
                          dmgImage=pygame.Surface( (0, 0) ),
                          strength=1,
                          agility=2,
                          minHp=3,
                          maxHp=4,
                          sleepResist=5.1,
                          stopspellResist=6.2,
                          hurtResist=7.3,
                          dodge=8.4,
                          blockFactor=9.5,
                          xp=10,
                          minGp=11,
                          maxGp=12,
                          monsterActions=[] )
   monsterState = MonsterState( monsterInfo, None )
   print( monsterState, flush=True )
   while monsterState.isAlive():
      monsterState.hp -= 10
      print( monsterState, flush=True )

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
