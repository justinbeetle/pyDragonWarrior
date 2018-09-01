#!/usr/bin/env python

import os
import xml.etree.ElementTree
import random

import pygame

from AudioPlayer import AudioPlayer
from Point import Point
from GameTypes import *
from GameInfo import GameInfo
from CharacterState import CharacterState

class GameState:

   def __init__(self, basePath, gameXmlPath, desiredWinSize_pixels, tileSize_pixels, savedGameFile = None):
      
      if desiredWinSize_pixels is None:
         self.screen = pygame.display.set_mode( (0, 0) , pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.HWSURFACE )
         winSize_pixels = Point( self.screen.get_size() )
         self.winSize_tiles = ( winSize_pixels / tileSize_pixels ).floor()
         self.imagePad_tiles = self.winSize_tiles // 2
         self.winSize_pixels = self.winSize_tiles * tileSize_pixels
      else:
         self.winSize_tiles = ( desiredWinSize_pixels / tileSize_pixels ).floor()
         self.imagePad_tiles = self.winSize_tiles // 2
         self.winSize_pixels = self.winSize_tiles * tileSize_pixels
         self.screen = pygame.display.set_mode( self.winSize_pixels, pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.HWSURFACE )

      self.isRunning = True
      self.phase = Phase.A
      self.tickCount = 1
      self.gameInfo = GameInfo( basePath, gameXmlPath, tileSize_pixels, savedGameFile)

      # Set character state for new game
      self.mapState = None
      self.setMap( self.gameInfo.initialMap, self.gameInfo.initialMapDecorations )
      self.pendingDialog = self.gameInfo.initialStateDialog
      self.pc = CharacterState(
         'hero',
         self.gameInfo.initialHeroPos_datTile,
         self.gameInfo.initialHeroPos_dir,
         self.gameInfo.pc_name,
         CharacterState.calcLevel( self.gameInfo.levels, self.gameInfo.pc_xp ) )
      self.pc.xp = self.gameInfo.pc_xp
      self.pc.gp = self.gameInfo.pc_gp
      if self.gameInfo.pc_hp is not None and self.gameInfo.pc_hp < self.pc.hp:
         self.pc.hp = self.gameInfo.pc_hp
      if self.gameInfo.pc_mp is not None and self.gameInfo.pc_mp < self.pc.mp:
         self.pc.mp = self.gameInfo.pc_mp
      self.pc.weapon = self.gameInfo.pc_weapon
      self.pc.armor = self.gameInfo.pc_armor
      self.pc.shield = self.gameInfo.pc_shield
      self.pc.otherEquippedItems = self.gameInfo.pc_otherEquippedItems
      self.pc.unequippedItems = self.gameInfo.pc_unequippedItems

   def save(self):
      xmlRoot = xml.etree.ElementTree.Element('SaveState')
      xmlRoot.attrib['name'] = self.pc.name
      xmlRoot.attrib['map'] = self.mapState.mapName
      xmlRoot.attrib['x'] = str(self.pc.currPos_datTile.x)
      xmlRoot.attrib['y'] = str(self.pc.currPos_datTile.y)
      xmlRoot.attrib['dir'] = self.pc.dir.name
      xmlRoot.attrib['xp'] = str(self.pc.xp)
      xmlRoot.attrib['gp'] = str(self.pc.gp)
      xmlRoot.attrib['hp'] = str(self.pc.hp)
      xmlRoot.attrib['mp'] = str(self.pc.mp)

      itemsElement = xml.etree.ElementTree.SubElement( xmlRoot, 'EquippedItems' )
      if self.pc.weapon is not None:
         itemElement = xml.etree.ElementTree.SubElement( itemsElement, 'Item' )
         itemElement.attrib['name'] = self.pc.weapon.name
      if self.pc.armor is not None:
         itemElement = xml.etree.ElementTree.SubElement( itemsElement, 'Item' )
         itemElement.attrib['name'] = self.pc.armor.name
      if self.pc.shield is not None:
         itemElement = xml.etree.ElementTree.SubElement( itemsElement, 'Item' )
         itemElement.attrib['name'] = self.pc.shield.name
      for item in self.pc.otherEquippedItems:
         itemElement = xml.etree.ElementTree.SubElement( itemsElement, 'Item' )
         itemElement.attrib['name'] = item.name

      itemsElement = xml.etree.ElementTree.SubElement( xmlRoot, 'UnequippedItems' )
      for item in self.pc.unequippedItems:
         if self.pc.unequippedItems[item] > 0:
            itemElement = xml.etree.ElementTree.SubElement( itemsElement, 'Item' )
            itemElement.attrib['name'] = item.name
            itemElement.attrib['count'] = str(self.pc.unequippedItems[item])
            
      dialogElement = xml.etree.ElementTree.SubElement( xmlRoot, 'Dialog' )
      dialogElement.text = 'I am glad thou hast returned. All our hopes are riding on thee. Before reaching thy next level of experience thou must gain [NEXT_LEVEL_XP] experience points. See me again when thy level has increased.'
      dialogElement = xml.etree.ElementTree.SubElement( xmlRoot, 'Dialog' )
      dialogElement.text = 'Goodbye now, [NAME]. Take care and tempt not the Fates.'  

      saveGameFilePath = os.path.join( self.gameInfo.savesPath, self.pc.name + '.xml' )
      saveGameFile = open(saveGameFilePath, 'wb')
      saveGameFile.write( xml.etree.ElementTree.tostring( xmlRoot ) )
      saveGameFile.close()

   def getCastableCombatSpellNames(self):
      return self.gameInfo.getCastableSpellNames( True, self.pc.level, self.pc.mp, self.mapState.mapName )

   def getCastableNonCombatSpellNames(self):
      return self.gameInfo.getCastableSpellNames( False, self.pc.level, self.pc.mp, self.mapState.mapName )

   def getAvailableSpellNames(self):
      return self.gameInfo.getAvailableSpellNames( self.pc.level )
   
   def getMapImageRect(self):
      # Always rendering to the entire screen but need to determine the
      # rectangle from the image which is to be scaled to the screen
      return pygame.Rect(
         (self.imagePad_tiles[0] + self.pc.currPos_datTile[0] - self.winSize_tiles[0] / 2 + 0.5) * self.gameInfo.tileSize_pixels + self.pc.currPosOffset_imgPx.x,
         (self.imagePad_tiles[1] + self.pc.currPos_datTile[1] - self.winSize_tiles[1] / 2 + 0.5) * self.gameInfo.tileSize_pixels + self.pc.currPosOffset_imgPx.y,
         self.winSize_pixels[0],
         self.winSize_pixels[1] )

   def getTileImageRect(self, tile, offset=Point(0,0)):
      return self.getTileRegionImageRect(tile, 0, offset)

   def getTileRegionImageRect(self, centerTile, tileRadius, offset=Point(0,0)):
      return pygame.Rect(
         (self.imagePad_tiles[0] + centerTile[0] - tileRadius) * self.gameInfo.tileSize_pixels + offset.x,
         (self.imagePad_tiles[1] + centerTile[1] - tileRadius) * self.gameInfo.tileSize_pixels + offset.y,
         (2*tileRadius + 1) * self.gameInfo.tileSize_pixels,
         (2*tileRadius + 1) * self.gameInfo.tileSize_pixels )

   def getTileScreenRect(self, tile, offset=Point(0,0)):
      return self.getTileRegionScreenRect(tile, 0, offset)
   
   def getTileRegionScreenRect(self, centerTile, tileRadius, offset=Point(0,0)):
      # Hero is always in the center of the screen
      return pygame.Rect(
         (self.winSize_tiles[0] / 2 - 0.5 + centerTile[0] - self.pc.currPos_datTile[0] - tileRadius) * self.gameInfo.tileSize_pixels + offset.x - self.pc.currPosOffset_imgPx.x,
         (self.winSize_tiles[1] / 2 - 0.5 + centerTile[1] - self.pc.currPos_datTile[1] - tileRadius) * self.gameInfo.tileSize_pixels + offset.y - self.pc.currPosOffset_imgPx.y,
         (2*tileRadius + 1) * self.gameInfo.tileSize_pixels,
         (2*tileRadius + 1) * self.gameInfo.tileSize_pixels )

   def getTileInfo(self, tile):
      return self.gameInfo.tiles[self.gameInfo.tileSymbols[self.gameInfo.maps[self.mapState.mapName].dat[tile.y][tile.x]]]

   def getTileDegreesOfFreedom(self, tile, enforceNpcHpPenaltyLimit):
      degreesOfFreedom = 0
      for x in [tile.x-1, tile.x+1]:
         if self.canMoveToTile( Point(x, tile.y), enforceNpcHpPenaltyLimit, False ):
            degreesOfFreedom += 1
      for y in [tile.y-1, tile.y+1]:
         if self.canMoveToTile( Point(tile.x, y), enforceNpcHpPenaltyLimit, False ):
            degreesOfFreedom += 1
      #print('DOF for tile', tile, 'is', degreesOfFreedom, flush=True)
      return degreesOfFreedom

   def canMoveToTile(self, tile, enforceNpcHpPenaltyLimit = False, enforceNpcDofLimit = False):
      movementAllowed = False
      if ( 0 <= tile.x < self.gameInfo.maps[self.mapState.mapName].size.w and
           0 <= tile.y < self.gameInfo.maps[self.mapState.mapName].size.h and
           self.getTileInfo(tile).walkable ):
         movementAllowed = True
         if movementAllowed and enforceNpcHpPenaltyLimit and self.getTileInfo(tile).hpPenalty != 0:
            movementAllowed = False
            #print('Movement not allowed: NPC HP penalty limited', flush=True)
         if movementAllowed and enforceNpcDofLimit and self.getTileDegreesOfFreedom(tile, enforceNpcHpPenaltyLimit) < 2:
            movementAllowed = False
            #print('Movement not allowed: NPC degree-of-freedom limit not met', flush=True)
         if tile == self.pc.currPos_datTile or tile == self.pc.destPos_datTile:
            movementAllowed = False
            #print('Movement not allowed: PC in the way', flush=True)
         if movementAllowed:
            for npc in self.npcs:
               if tile == npc.currPos_datTile or tile == npc.destPos_datTile:
                  movementAllowed = False
                  #print('Movement not allowed: NPC in the way', flush=True)
                  break
         if movementAllowed:
            for decoration in self.mapDecorations:
               if tile == decoration.point and decoration.type is not None and not self.gameInfo.decorations[decoration.type].walkable:
                  movementAllowed = False
                  #print('Movement not allowed: decoration not walkable', flush=True)
                  break
      #else:
      #   print('Movement not allowed: tile not walkable', flush=True)
      return movementAllowed

   def getTileMonsters(self, tile):
      for mz in self.gameInfo.maps[self.mapState.mapName].monsterZones:
         if mz.x <= tile.x <= mz.x + mz.w and mz.y <= tile.y <= mz.y + mz.h:
            #print( 'in monsterZone of monster set ' + mz.setName + ':', self.gameInfo.monsterSets[mz.setName], flush=True )
            return self.gameInfo.monsterSets[mz.setName]
      return []

   def eraseCharacters(self):
      # Erase PC
      self.eraseCharacter( self.pc )

      # Erase NPCs
      for npc in self.npcs:
         self.eraseCharacter( npc )
         
   def eraseCharacter(self, character):
      self.screen.blit(
         self.mapState.mapImage.subsurface(
            self.getTileImageRect(
               character.currPos_datTile,
               character.currPosOffset_imgPx) ),
         self.getTileScreenRect(
            character.currPos_datTile,
            character.currPosOffset_imgPx ) )

   def drawCharacters(self):
      # Draw PC
      self.drawCharacter( self.pc )

      # Draw NPCs
      for npc in self.npcs:
         self.drawCharacter( npc )
         
   def drawCharacter(self, character):
      self.screen.blit(
         self.gameInfo.characterTypes[character.type].images[character.dir][self.phase],
         self.getTileScreenRect(
            character.currPos_datTile,
            character.currPosOffset_imgPx) )

   def isLightRestricted(self):
      return self.lightRadius is not None and self.lightRadius <= self.winSize_tiles.w/2 and self.lightRadius <= self.winSize_tiles.h/2

   def setMap(self, newMapName, oneTimeDecorations = []):
      if self.mapState is not None:
         # Update light radius if different between new and old maps
         # Don't always update as this would cancel out light radius changing affects (torchs, etc.)
         oldMapName = self.mapState.mapName
         if self.gameInfo.maps[newMapName].lightRadius != self.gameInfo.maps[oldMapName].lightRadius:
            self.lightRadius = self.gameInfo.maps[newMapName].lightRadius
      else:
         self.lightRadius = self.gameInfo.maps[newMapName].lightRadius

      self.mapDecorations = self.gameInfo.maps[newMapName].mapDecorations + oneTimeDecorations
      self.mapState = self.gameInfo.getMapImageInfo( newMapName, self.imagePad_tiles, self.mapDecorations )
      self.npcs = []
      for npc in self.gameInfo.maps[newMapName].nonPlayerCharacters:
         self.npcs.append( CharacterState.createNpcState( npc ) )

   def removeDecoration(self, decoration):
      self.mapDecorations.remove( decoration )
      # TODO: May also need to remove this from the list of one-time decorations for this map
      
      self.mapState = self.gameInfo.getMapImageInfo( self.mapState.mapName, self.imagePad_tiles, self.mapDecorations )

      # Draw the map to the screen
      self.drawMap()
      

   def drawMap(self, flipBuffer=True):
      # Draw the map to the screen
      self.screen.set_clip( pygame.Rect( 0,
                                         0,
                                         self.winSize_pixels.x,
                                         self.winSize_pixels.y ) )
      if self.isLightRestricted():
         self.screen.fill( pygame.Color('black') )
         self.screen.blit( self.mapState.mapImage.subsurface(
                              self.getTileRegionImageRect(
                                 self.pc.currPos_datTile,
                                 self.lightRadius,
                                 self.pc.currPosOffset_imgPx ) ),
                           self.getTileRegionScreenRect(
                              self.pc.currPos_datTile,
                              self.lightRadius,
                              self.pc.currPosOffset_imgPx ) )
      else:
         self.screen.blit( self.mapState.mapImage.subsurface( self.getMapImageRect() ), (0,0) )

      # Draw the hero and NPCs to the screen
      self.drawCharacters()

      # Flip the screen buffer
      if flipBuffer:
         pygame.display.flip()

   def advanceTick(self, charactersErased=False):
      PHASE_TICKS = 20
      NPC_MOVE_STEPS = 60

      phaseChanged = False
      if self.tickCount % PHASE_TICKS == 0:
         phaseChanged = True
         if self.phase == Phase.A:
            self.phase = Phase.B
         else:
            self.phase = Phase.A

      if phaseChanged and not charactersErased:
         charactersErased = True
         self.eraseCharacters()

      redrawMap = False
      drawAllCharacters = charactersErased

      # Move NPCs
      imagePxStepSize = self.gameInfo.tileSize_pixels // 8 # NOTE: tileSize_pixels must be divisible by imagePxStepSize
      for npc in self.npcs:
         if npc.npcInfo.walking:
            
            # Start moving NPC by setting a destination tile
            if self.tickCount % NPC_MOVE_STEPS == 0:
               # TODO: Determine where to move instead of blindly moving forward
               npc.dir = random.choice( list( Direction ) )
               destTile = npc.currPos_datTile + getDirectionVector( npc.dir )
               if self.canMoveToTile( destTile, True, True ):
                  npc.destPos_datTile = destTile

            # Move the NPC in steps to the destination tile
            if npc.currPos_datTile != npc.destPos_datTile:
               if not charactersErased:
                  self.eraseCharacter(npc)
               directionVector = getDirectionVector( npc.dir )
               npc.currPosOffset_imgPx += directionVector * imagePxStepSize
               if npc.currPosOffset_imgPx / self.gameInfo.tileSize_pixels == directionVector:
                  npc.currPos_datTile = npc.destPos_datTile
                  npc.currPosOffset_imgPx = Point(0, 0)
               if not drawAllCharacters:
                  self.drawCharacter(npc)
                  redrawMap = True

      if drawAllCharacters:
         self.drawCharacters()
         redrawMap = True

      if redrawMap:
         pygame.display.flip()
            
      self.tickCount += 1
      pygame.time.Clock().tick(40)

def main():
   print( 'Not implemented', flush=True )

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
