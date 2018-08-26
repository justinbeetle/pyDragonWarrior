#!/usr/bin/env python

import os
import math
import random
import xml.etree.ElementTree
from collections import namedtuple
from enum import Enum

import pygame

from AudioPlayer import AudioPlayer
from GameTypes import *
from Point import Point

class GameInfo:
   TRANSPARENT_COLOR = pygame.Color(0, 128, 128)
   
   def __init__(self, basePath, gameXmlPath, tileSize_pixels, savedGameFile = None):

      self.tileSize_pixels = tileSize_pixels
      self.dialogSequences = {}

      # TODO: Need to determine a method for determining how much to scale the monster images
      monsterScaleFactor = 4

      # Parse XML
      xmlRoot = xml.etree.ElementTree.parse(gameXmlPath).getroot()
      self.savesPath = os.path.join(basePath,  xmlRoot.attrib['savesPath'])
      dataPath = os.path.join(basePath, xmlRoot.attrib['dataPath'])
      imagePath = os.path.join(dataPath, xmlRoot.attrib['imagePath'])
      musicPath = os.path.join(dataPath, xmlRoot.attrib['musicPath'])
      soundPath = os.path.join(dataPath, xmlRoot.attrib['soundPath'])
      tilePath = os.path.join(imagePath, xmlRoot.attrib['tilePath'])
      mapsPath = os.path.join(dataPath, xmlRoot.attrib['mapsPath'])
      decorationPath = os.path.join(imagePath, xmlRoot.attrib['decorationPath'])
      characterPath = os.path.join(imagePath, xmlRoot.attrib['characterPath'])
      monsterPath = os.path.join(imagePath, xmlRoot.attrib['monsterPath'])
      encounterPath = os.path.join(imagePath, xmlRoot.attrib['encounterPath'])

      # Initialize the music player
      audioPlayer = AudioPlayer()
      audioPlayer.setMusicPath( musicPath )
      audioPlayer.setSoundPath( soundPath )

      # Parse items
      self.items = {}

      # Parse weapons
      self.weapons = {}
      for element in xmlRoot.findall("./Items/Weapons/Weapon"):
         itemName = element.attrib['name']
         self.weapons[itemName] = Weapon(
            itemName,
            int(element.attrib['attackBonus']),
            int(element.attrib['gp']) )
         self.items[itemName] = self.weapons[itemName]
         
      # Parse armors
      self.armors = {}
      for element in xmlRoot.findall("./Items/Armors/Armor"):
         itemName = element.attrib['name']
         self.armors[itemName] = Armor(
            itemName,
            int(element.attrib['defenseBonus']),
            int(element.attrib['gp']),
            element.attrib['ignoresTilePenalties'] == 'yes',
            float(element.attrib['hurtDmgModifier']),
            int(element.attrib['hpRegenTiles']) )
         self.items[itemName] = self.armors[itemName]
         
      # Parse shields
      self.shields = {}
      for element in xmlRoot.findall("./Items/Shields/Shield"):
         itemName = element.attrib['name']
         self.shields[itemName] = Shield(
            itemName,
            int(element.attrib['defenseBonus']),
            int(element.attrib['gp']) )
         self.items[itemName] = self.shields[itemName]
         
      # Parse tools
      self.tools = {}
      for element in xmlRoot.findall("./Items/Tools/Tool"):
         itemName = element.attrib['name']
         attackBonus = 0
         defenseBonus = 0
         minHpRecover = 0
         maxHpRecover = 0
         lightRadius = 0
         gp = 0
         consumeOnUse = True
         if 'attackBonus' in element.attrib:
            attackBonus = int(element.attrib['attackBonus'])
         if 'defenseBonus' in element.attrib:
            defenseBonus = int(element.attrib['defenseBonus'])
         if 'hpRecover' in element.attrib:
            (minHpRecover, maxHpRecover) = GameInfo.parseIntRange(element.attrib['hpRecover'])
         if 'lightRadius' in element.attrib:
            lightRadius = int(element.attrib['lightRadius'])
         if 'gp' in element.attrib:
            gp = int(element.attrib['gp'])
         if 'consumeOnUse' in element.attrib:
            consumeOnUse = element.attrib['consumeOnUse'] == 'yes'

         self.tools[itemName] = Tool(
            itemName,
            attackBonus,
            defenseBonus,
            minHpRecover,
            maxHpRecover,
            lightRadius,
            gp,
            element.attrib['droppable'] == 'yes',
            element.attrib['equippable'] == 'yes',
            element.attrib['usable'] == 'yes',
            consumeOnUse )
         self.items[itemName] = self.tools[itemName]

      # Parse tiles
      self.tileSymbols = {}
      self.tiles = {}
      for element in xmlRoot.findall("./Tiles/Tile"):
         tileName = element.attrib['name']
         tileSymbol = element.attrib['symbol']
         tileImageFileName = os.path.join( tilePath, element.attrib['image'] )
         tileWalkable = True
         canTalkOver = False
         hpPenalty = 0
         mpPenalty = 0
         speed = 1.0
         spawnRate = 1.0
         specialEdges = False
         if 'walkable' in element.attrib:
            tileWalkable = element.attrib['walkable'] == 'yes'
         if 'canTalkOver' in element.attrib:
            canTalkOver = element.attrib['canTalkOver'] == 'yes'
         if 'hpPenalty' in element.attrib:
            hpPenalty = int(element.attrib['hpPenalty'])
         if 'mpPenalty' in element.attrib:
            mpPenalty = int(element.attrib['mpPenalty'])
         if 'speed' in element.attrib:
            speed = GameInfo.parseFloat(element.attrib['speed'])
         if 'spawnRate' in element.attrib:
            spawnRate = GameInfo.parseFloat(element.attrib['spawnRate'])
         if 'specialEdges' in element.attrib:
            specialEdges = element.attrib['specialEdges'] == 'yes'
            
         #print('Loading image', tileImageFileName, flush=True)
         tileImageUnscaled = pygame.image.load(tileImageFileName).convert()
         if specialEdges:
            tileImageScaled = []
            unscaledHeight = tileImageUnscaled.get_height()
            for x in range(16):
               temp = pygame.Surface( (self.tileSize_pixels, self.tileSize_pixels) )
               pygame.transform.scale( tileImageUnscaled.subsurface(
                  pygame.Rect( x*unscaledHeight, 0, unscaledHeight, unscaledHeight ) ),
                  (self.tileSize_pixels, self.tileSize_pixels),
                  temp )
               tileImageScaled.append(temp)
         else:
            tileImageScaled = pygame.Surface( (self.tileSize_pixels, self.tileSize_pixels) )
            pygame.transform.scale( tileImageUnscaled, (self.tileSize_pixels, self.tileSize_pixels), tileImageScaled )
         
         self.tileSymbols[tileSymbol] = tileName
         self.tiles[tileName] = Tile(tileName, tileSymbol, tileImageScaled, tileWalkable, canTalkOver, hpPenalty, mpPenalty, speed, spawnRate, specialEdges)

      # Parse decorations
      self.decorations = {}
      for element in xmlRoot.findall("./Decorations/Decoration"):
         decorationName = element.attrib['name']
         widthTiles = 1
         heightTiles = 1
         walkable = True
         removeWithSearch = False
         removeWithKey = False
         if 'widthTiles' in element.attrib:
            widthTiles = int(element.attrib['widthTiles'])
         if 'heightTiles' in element.attrib:
            heightTiles = int(element.attrib['heightTiles'])
         if 'walkable' in element.attrib:
            walkable = element.attrib['walkable'] == 'yes'
         if 'removeWithSearch' in element.attrib:
            removeWithSearch = element.attrib['removeWithSearch'] == 'yes'
         if 'removeWithKey' in element.attrib:
            removeWithKey = element.attrib['removeWithKey'] == 'yes'
            
         decorationImageFileName = os.path.join( decorationPath, element.attrib['image'] )
         #print('Loading image', decorationImageFileName, flush=True)
         decorationImageUnscaled = pygame.image.load(decorationImageFileName).convert()
         unscaledSize_pixels = Point( decorationImageUnscaled.get_size() )
         maxScaledSize_pixels = Point( widthTiles, heightTiles ) * self.tileSize_pixels
         scaleFactor_point = (maxScaledSize_pixels / unscaledSize_pixels).floor()
         scaleFactor = max( scaleFactor_point.w, scaleFactor_point.h )
         scaledSize_pixels = unscaledSize_pixels * scaleFactor
         decorationImageScaled = pygame.Surface( scaledSize_pixels )
         pygame.transform.scale( decorationImageUnscaled, scaledSize_pixels, decorationImageScaled )
         decorationImageScaled.set_colorkey( GameInfo.TRANSPARENT_COLOR )
         self.decorations[decorationName] = Decoration(decorationName, decorationImageScaled, walkable, removeWithSearch, removeWithKey )

      # Parse characters
      self.characterTypes = {}
      for element in xmlRoot.findall("./CharacterTypes/CharacterType"):
         characterType = element.attrib['type']
         characterTypeFileName = os.path.join( characterPath, element.attrib['image'] )
         #print('Loading image', characterTypeFileName, flush=True)
         characterTypeImage = pygame.image.load(characterTypeFileName).convert()
         characterTypeImages = {}
         x_px = 0
         for direction in [Direction.SOUTH, Direction.EAST, Direction.NORTH, Direction.WEST]:
            directionCharacterTypeImages = {}
            for phase in [Phase.A, Phase.B]:
               image = pygame.Surface( (self.tileSize_pixels, self.tileSize_pixels) )
               pygame.transform.scale( characterTypeImage.subsurface(x_px, 0, characterTypeImage.get_height(), characterTypeImage.get_height()), (self.tileSize_pixels, self.tileSize_pixels), image )
               image.set_colorkey( GameInfo.TRANSPARENT_COLOR )
               directionCharacterTypeImages[phase] = image
               x_px += characterTypeImage.get_height() + 1
            characterTypeImages[direction] = directionCharacterTypeImages
         self.characterTypes[characterType]=CharacterType(characterType, characterTypeImages)

      # Parse maps
      self.maps = {}
      for element in xmlRoot.findall("./Maps/Map"):
         mapName = element.attrib['name']
         #print( 'mapName =', mapName, flush=True )
         mapDatFileName = os.path.join( mapsPath, element.attrib['tiles'] )
         music = element.attrib['music']
         lightRadius = None
         if 'lightRadius' in element.attrib and element.attrib['lightRadius'] != 'unlimited':
            lightRadius = int(element.attrib['lightRadius'])

         # Parse transitions
         leavingTransition = None
         pointTransitions = []
         mapDecorations = []
         transElement = element.find('LeavingTransition')
         if transElement != None:
            leavingTransition = LeavingTransition( transElement.attrib['toMap'],
                                                   Point( int(transElement.attrib['toX']),
                                                          int(transElement.attrib['toY']) ),
                                                   Direction[transElement.attrib['toDir']] )
         for transElement in element.findall('PointTransition'):
            fromPoint = Point( int(transElement.attrib['fromX']),
                               int(transElement.attrib['fromY']) )
            pointTransitions.append( PointTransition( fromPoint,
                                                      transElement.attrib['toMap'],
                                                      Point( int(transElement.attrib['toX']),
                                                             int(transElement.attrib['toY']) ),
                                                      Direction[transElement.attrib['toDir']] ) )
            if 'decoration' in transElement.attrib and transElement.attrib['decoration'] != 'None':
               decorationType = transElement.attrib['decoration']
               mapDecorations.append( MapDecoration( decorationType, fromPoint, None ) )

         # Parse NPCs
         nonPlayerCharacters = []
         for npcElement in element.findall('NonPlayerCharacter'):
            nonPlayerCharacters.append( NonPlayerCharacter( npcElement.attrib['type'],
                                                            Point( int(npcElement.attrib['x']),
                                                                   int(npcElement.attrib['y']) ),
                                                            Direction[npcElement.attrib['dir']],
                                                            npcElement.attrib['walking'] == 'yes',
                                                            self.parseDialog( npcElement ) ) ) #npcElement.find('Dialog').text ) )

         # Parse standalone decorations
         for decorationElement in element.findall('MapDecoration'):
            decorationType = None
            if 'type' in decorationElement.attrib and decorationElement.attrib['type'] != 'None':
               decorationType = decorationElement.attrib['type']
            mapDecorations.append( MapDecoration(
                  decorationType,
                  Point( int(decorationElement.attrib['x']),
                         int(decorationElement.attrib['y']) ),
                  self.parseDialog( decorationElement ) ) )
         
         # Load map dat file
         mapDat = []
         mapDatFile = open(mapDatFileName, 'r')
         # Future: Could corner turn data from row,col (y,x) into col,row (x,y)
         for line in mapDatFile:
            line = line.strip('\n')
            mapDat.append(line)
            # TODO: Validate the map is rectangular and all tiles are defined
         mapDatFile.close()
         mapDatSize = Point( len( mapDat[0] ), len( mapDat ) )

         # Parse map monster info
         monsterZones = []
         if 'monsterSet' in element.attrib:
            monsterZones.append( MonsterZone( 0, 0, mapDatSize.w, mapDatSize.h, element.attrib['monsterSet'] ) )
         else:
            for monsterZoneElement in element.findall('MonsterZones/MonsterZone'):
               monsterZones.append( MonsterZone(
                  int(monsterZoneElement.attrib['x']),
                  int(monsterZoneElement.attrib['y']),
                  int(monsterZoneElement.attrib['w']),
                  int(monsterZoneElement.attrib['h']),
                  monsterZoneElement.attrib['set'] ) )
         
         # Load the encounter image
         encounterImage = None
         if len(monsterZones):
            encounterImageFileName = os.path.join( encounterPath, element.attrib['encounterBackground'] )
            unscaledEncounterImage = pygame.image.load(encounterImageFileName).convert()
            encounterImage = pygame.transform.scale( unscaledEncounterImage, ( unscaledEncounterImage.get_width() * monsterScaleFactor, unscaledEncounterImage.get_height() * monsterScaleFactor ) )
         
         self.maps[mapName] = Map(mapName, mapDat, mapDatSize, music, lightRadius, leavingTransition, pointTransitions, nonPlayerCharacters, mapDecorations, monsterZones, encounterImage)

      # Parse dialog scripts
      for element in xmlRoot.findall("./DialogScripts/DialogScript"):
         self.dialogSequences[ element.attrib['label'] ] =  self.parseDialog( element )

      # Parse monsters
      self.monsters = {}
      for element in xmlRoot.findall("./Monsters/Monster"):
         monsterName = element.attrib['name']

         monsterImageFileName = os.path.join( monsterPath, element.attrib['image'] )
         unscaledMonsterImage = pygame.image.load(monsterImageFileName).convert()
         monsterImage = pygame.transform.scale( unscaledMonsterImage, ( unscaledMonsterImage.get_width() * monsterScaleFactor, unscaledMonsterImage.get_height() * monsterScaleFactor ) )
         monsterImage.set_colorkey( GameInfo.TRANSPARENT_COLOR )

         dmgImage = monsterImage.copy()
         for x in range( dmgImage.get_width() ):
            for y in range( dmgImage.get_height() ):
               if dmgImage.get_at( (x, y) ) != GameInfo.TRANSPARENT_COLOR:
                  dmgImage.set_at( (x, y), pygame.Color( 'red' ) )

         (minHp, maxHp) = GameInfo.parseIntRange(element.attrib['hp'])
         (minGp, maxGp) = GameInfo.parseIntRange(element.attrib['gp'])
         
         self.monsters[monsterName] = Monster(
            monsterName,
            monsterImage,
            dmgImage,
            int(element.attrib['strength']),
            int(element.attrib['agility']),
            minHp,
            maxHp,
            GameInfo.parseFloat(element.attrib['sleepResist']),
            GameInfo.parseFloat(element.attrib['stopspellResist']),
            GameInfo.parseFloat(element.attrib['hurtResist']),
            GameInfo.parseFloat(element.attrib['dodge']),
            GameInfo.parseFloat(element.attrib['blockFactor']),
            int(element.attrib['xp']),
            minGp,
            maxGp )
         
      # Parse monster sets
      self.monsterSets = {}
      for element in xmlRoot.findall("./MonsterSets/MonsterSet"):
         monsters = []
         for monsterElement in element.findall("./Monster"):
            monsters.append( monsterElement.attrib['name'] )
         self.monsterSets[ element.attrib['name'] ] = monsters

      # Parse levels
      self.levels = []
      self.levelsByName = {}
      self.levelsByNumber = {}
      for element in xmlRoot.findall("./Levels/Level"):
         levelName = element.attrib['name']
         levelNumber = len(self.levels)
         level = Level(
            levelNumber,
            levelName,
            int(element.attrib['xp']),
            int(element.attrib['strength']),
            int(element.attrib['agility']),
            int(element.attrib['hp']),
            int(element.attrib['mp']) )
         self.levels.append( level )
         self.levelsByName[ levelName ] = level
         self.levelsByNumber[ levelNumber ] = level

      # Parse spells
      self.spells = {}
      for element in xmlRoot.findall("./Spells/Spell"):
         spellName = element.attrib['name']
         availableInCombat = True
         availableOutsideCombat = True
         minHpRecover = 0
         maxHpRecover = 0
         minDamageByHero = 0
         maxDamageByHero = 0
         minDamageByMonster = 0
         maxDamageByMonster = 0
         excludedMap = None
         includedMap = None
         if 'availableInCombat' in element.attrib:
            availableInCombat = element.attrib['availableInCombat'] == 'yes'
         if 'availableOutsideCombat' in element.attrib:
            availableOutsideCombat = element.attrib['availableOutsideCombat'] == 'yes'
         if 'hpRecover' in element.attrib:
            (minHpRecover, maxHpRecover) = GameInfo.parseIntRange(element.attrib['hpRecover'])
         if 'damageByHero' in element.attrib:
            (minDamageByHero, maxDamageByHero) = GameInfo.parseIntRange(element.attrib['damageByHero'])
         if 'damageByMonster' in element.attrib:
            (minDamageByMonster, maxDamageByMonster) = GameInfo.parseIntRange(element.attrib['damageByMonster'])
         if 'excludedMap' in element.attrib:
            excludedMap = element.attrib['excludedMap']
         if 'includedMap' in element.attrib:
            includedMap = element.attrib['includedMap']
         
         self.spells[ spellName ] = Spell(
            spellName,
            self.levelsByName[ element.attrib['level'] ],
            int(element.attrib['mp']),
            availableInCombat,
            availableOutsideCombat,
            minHpRecover,
            maxHpRecover,
            minDamageByHero,
            maxDamageByHero,
            minDamageByMonster,
            maxDamageByMonster,
            excludedMap,
            includedMap )
         
      # Parse initial game state
      self.pc_name = None
      initialStateElement = xmlRoot.find('InitialState')
      if savedGameFile is not None:
         saveGameFilePath = os.path.join( self.savesPath, savedGameFile + '.xml' )
         if os.path.isfile(saveGameFilePath):
            print('Loading save game from file ' + saveGameFilePath, flush=True)
            initialStateElement = xml.etree.ElementTree.parse(saveGameFilePath).getroot()
         else:
            self.pc_name = savedGameFile
         
      self.initialMap = initialStateElement.attrib['map']
      self.initialHeroPos_datTile = Point(
         int(initialStateElement.attrib['x']),
         int(initialStateElement.attrib['y']) )
      self.initialHeroPos_dir = Direction[initialStateElement.attrib['dir']]
      self.initialStateDialog = self.parseDialog( initialStateElement )

      if self.pc_name is None:
         self.pc_name = initialStateElement.attrib['name']
      self.pc_xp = int(initialStateElement.attrib['xp'])
      self.pc_gp = int(initialStateElement.attrib['gp'])
      self.pc_weapon = None
      self.pc_armor = None
      self.pc_shield = None
      self.pc_otherEquippedItems = []
      self.pc_unequippedItems = {}
      for itemElement in initialStateElement.findall("./EquippedItems/Item"):
         itemName = itemElement.attrib['name']
         if itemName in self.weapons:
            self.pc_weapon = self.weapons[itemName]
         elif itemName in self.armors:
            self.pc_armor = self.armors[itemName]
         elif itemName in self.shields:
            self.pc_shield = self.shields[itemName]
         elif itemName in self.items:
            self.pc_otherEquippedItems.append( self.items[itemName] )
         else:
            print( 'ERROR: Unsupported item', itemName, flush=True )
            
      for itemElement in initialStateElement.findall("./UnequippedItems/Item"):
         itemName = itemElement.attrib['name']
         itemCount = 1
         if 'count' in itemElement.attrib:
            itemCount = int(itemElement.attrib['count'])
         if itemName in self.items:
            self.pc_unequippedItems[ self.items[itemName] ] = itemCount
         else:
            print( 'ERROR: Unsupported item', itemName, flush=True )
      
      self.initialMapDecorations = []
      for decorationElement in initialStateElement.findall("./MapDecoration"):
         decorationType = None
         if 'type' in decorationElement.attrib and decorationElement.attrib['type'] != 'None':
            decorationType = decorationElement.attrib['type']
         self.initialMapDecorations.append( MapDecoration(
            decorationType,
            Point( int(decorationElement.attrib['x']),
                   int(decorationElement.attrib['y']) ),
            self.parseDialog( decorationElement ) ) )

      # Parse death state
      deathStateElement = xmlRoot.find('DeathState')
      self.deathMap = deathStateElement.attrib['map']
      self.deathHeroPos_datTile = Point(
         int(deathStateElement.attrib['x']),
         int(deathStateElement.attrib['y']) )
      self.deathHeroPos_dir = Direction[deathStateElement.attrib['dir']]
      self.deathDialog = self.parseDialog( deathStateElement )

   def parseFloat(value):
      if '/' in value:
         retVal = int(value.split('/')[0]) / int(value.split('/')[1])
      else:
         retVal = float(value)
      return retVal

   def parseIntRange(value):
      if '-' in value:
         minVal = int(value.split('-')[0])
         maxVal = int(value.split('-')[1])
      else:
         minVal = maxVal = int(value)
      return (minVal, maxVal)

   def parseDialog( self, dialogRootElement ):
      dialog = []
      for element in dialogRootElement:
         #print( 'in parseDialog: element =', element, flush=True )
         
         label = None
         if 'label' in element.attrib and element.attrib['label'] != 'None':
            label = element.attrib['label']
         
         if element.tag == 'DialogSubTree':
            dialogSubTree = self.parseDialog( element )
            dialog.append( dialogSubTree )
            if label is not None:
               self.dialogSequences[label] = dialogSubTree
               
         elif element.tag == 'DialogGoTo':
            dialog.append( DialogGoTo( label ) )
            
         elif element.tag == 'Dialog':
            dialog.append( element.text )
            
         elif element.tag == 'DialogOptions':
            dialogOptions = {}
            for optionElement in element.findall("./DialogOption"):
               dialogOptions[ optionElement.attrib['name'] ] = self.parseDialog( optionElement )
            dialog.append( dialogOptions )
            if label is not None:
               self.dialogSequences[label] = dialogOptions
            
         elif element.tag == 'DialogVendorBuyOptions':
            if 'values' in element.attrib:
               dialogVendorBuyOptions = element.attrib['values']
            else:
               dialogVendorBuyOptions = []
               for optionElement in element.findall("./DialogVendorBuyOption"):
                  itemName = optionElement.attrib['name']
                  itemGp = self.items[itemName].gp
                  if 'gp' in optionElement.attrib:
                     itemGp = optionElement.attrib['gp']
                  dialogVendorBuyOptions.append( [itemName, str(itemGp)] )
            dialog.append( DialogVendorBuyOptions( dialogVendorBuyOptions ) )
            
         elif element.tag == 'DialogVendorSellOptions':
            if 'values' in element.attrib:
               dialogVendorSellOptions = element.attrib['values']
            else:
               dialogVendorSellOptions = []
               for optionElement in element.findall("./DialogVendorSellOption"):
                  dialogVendorSellOptions.append( optionElement.attrib['type'] )
            dialog.append( DialogVendorSellOptions( dialogVendorSellOptions ) )
               
         elif element.tag == 'DialogCheck':
            item = element.attrib['item']
            count = 1
            if 'count' in element.attrib:
               try:
                  count = int(element.attrib['count'])
               except:
                  count = element.attrib['count']
            dialog.append( DialogCheck( item, count, self.parseDialog( element ) ) )
            
         elif element.tag == 'DialogAction':
            item = None
            count = 1
            if 'item' in element.attrib:
               item = element.attrib['item']
            if 'count' in element.attrib:
               try:
                  count = int(element.attrib['count'])
               except:
                  count = element.attrib['count']
            dialog.append( DialogAction( DialogActionEnum[ element.attrib['type'] ], item, count ) )
            
         elif element.tag == 'DialogVariable':
            name = element.attrib['name']
            value = element.attrib['value']
            if value == 'ITEM_LIST':
               value = []
               for itemElement in element.findall("./Item"):
                  itemName = itemElement.attrib['name']
                  itemGp = self.items[itemName].gp
                  if 'gp' in itemElement.attrib:
                     itemGp = itemElement.attrib['gp']
                  value.append( [itemName, str(itemGp)] )
            elif value == 'INVENTORY_ITEM_TYPE_LIST':
               value = []
               for itemTypeElement in element.findall("./InventoryItemType"):
                  value.append( itemTypeElement.attrib['type'] )
            dialog.append( DialogVariable( name, value ) )

      if 0 == len(dialog):
         dialog = None
      
      return dialog

   def getCastableSpellNames(self, isInCombat, level, availableMp, mapName):
      availableSpells = []
      for spellName in self.spells:
         spell = self.spells[ spellName ]
         if ( spell.level.number <= level.number and
              ( ( isInCombat and spell.availableInCombat ) or
                ( not isInCombat and spell.availableOutsideCombat ) ) and
              spell.mp <= availableMp and
              spell.excludedMap != mapName and
              ( spell.includedMap is None or spell.includedMap == mapName ) ):
            availableSpells.append( spell.name )
      return availableSpells

   def getAvailableSpellNames(self, level):
      availableSpells = []
      for spellName in self.spells:
         spell = self.spells[ spellName ]
         if spell.level.number <= level.number:
            availableSpells.append( spell.name )
      return availableSpells

   def getMapImageInfo(self, mapName, imagePad_tiles = Point(0,0), mapDecorations = None ):
      
      # Determine the size of the map image then initialize
      # The size of the image is padded by imagePad_tiles in all directions
      mapImageSize_tiles = self.maps[mapName].size + 2 * imagePad_tiles
      mapImageSize_pixels = mapImageSize_tiles * self.tileSize_pixels
      mapImage = pygame.Surface( mapImageSize_pixels, pygame.SRCALPHA )
      mapImage.fill( pygame.Color('pink') ) # Fill with a color to make is easier to identify any gaps

      # Blit the padded portions of the image
      lastCol = self.maps[mapName].size[0]-1
      lastRow = self.maps[mapName].size[1]-1
      for x in range(imagePad_tiles.x):
         xW_px = x * self.tileSize_pixels
         xE_px  = (x + imagePad_tiles.x + self.maps[mapName].size[0]) * self.tileSize_pixels
         for y in range(imagePad_tiles.y):
            # Blit corners
            yN_px = y * self.tileSize_pixels
            yS_px  = (y + imagePad_tiles.y + self.maps[mapName].size[1]) * self.tileSize_pixels
            if self.tiles[self.tileSymbols[self.maps[mapName].dat[0][0]]].specialEdges:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[0][0]]].image[0],             (xW_px, yN_px) ) # NW pad
            else:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[0][0]]].image,                (xW_px, yN_px) ) # NW pad
            if self.tiles[self.tileSymbols[self.maps[mapName].dat[0][lastCol]]].specialEdges:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[0][lastCol]]].image[0],       (xE_px, yN_px) ) # NE pad
            else:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[0][lastCol]]].image,          (xE_px, yN_px) ) # NE pad
            if self.tiles[self.tileSymbols[self.maps[mapName].dat[lastRow][0]]].specialEdges:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[lastRow][0]]].image[0],       (xW_px, yS_px) ) # SW pad
            else:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[lastRow][0]]].image,          (xW_px, yS_px) ) # SW pad
            if self.tiles[self.tileSymbols[self.maps[mapName].dat[lastRow][lastCol]]].specialEdges:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[lastRow][lastCol]]].image[0], (xE_px, yS_px) ) # SE pad
            else:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[lastRow][lastCol]]].image,    (xE_px, yS_px) ) # SE pad
         for y in range(self.maps[mapName].size[1]):
            # Blit sides
            y_px = (y + imagePad_tiles.y) * self.tileSize_pixels
            if self.tiles[self.tileSymbols[self.maps[mapName].dat[y][0]]].specialEdges:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[y][0]]].image[0],             (xW_px, y_px) )  # W pad
            else:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[y][0]]].image,                (xW_px, y_px) )  # W pad
            if self.tiles[self.tileSymbols[self.maps[mapName].dat[y][lastCol]]].specialEdges:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[y][lastCol]]].image[0],       (xE_px, y_px) )  # E pad
            else:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[y][lastCol]]].image,          (xE_px, y_px) )  # E pad
      for y in range(imagePad_tiles.y):
         yN_px = y * self.tileSize_pixels
         yS_px = (y + imagePad_tiles.y + self.maps[mapName].size[1]) * self.tileSize_pixels
         for x in range(self.maps[mapName].size[0]):
            # Blit the top and bottom
            x_px = (x + imagePad_tiles.x) * self.tileSize_pixels
            if self.tiles[self.tileSymbols[self.maps[mapName].dat[0][x]]].specialEdges:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[0][x]]].image[0],             (x_px, yN_px) )  # N pad
            else:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[0][x]]].image,                (x_px, yN_px) )  # N pad
            if self.tiles[self.tileSymbols[self.maps[mapName].dat[lastRow][x]]].specialEdges:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[lastRow][x]]].image[0],       (x_px, yS_px) )  # S pad
            else:
               mapImage.blit( self.tiles[self.tileSymbols[self.maps[mapName].dat[lastRow][x]]].image,          (x_px, yS_px) )  # S pad

      # Blit the map data portion of the image
      for y, rowData in enumerate(self.maps[mapName].dat):
         y_px = (y + imagePad_tiles.y) * self.tileSize_pixels
         for x, tileSymbol in enumerate(rowData):
            x_px = (x + imagePad_tiles.x) * self.tileSize_pixels
            if self.tiles[self.tileSymbols[tileSymbol]].specialEdges:
               # Determine which image to use
               imageIdx = 0
               # TODO: Fix hardcoded exception for the bridge tileSymbol of 'b'
               if y>0 and self.maps[mapName].dat[y-1][x] != tileSymbol and self.maps[mapName].dat[y-1][x] != 'b':
                  imageIdx += 8
               if y<len(self.maps[mapName].dat)-1 and self.maps[mapName].dat[y+1][x] != tileSymbol and self.maps[mapName].dat[y+1][x] != 'b':
                  imageIdx += 2
               if x>0 and rowData[x-1] != tileSymbol and rowData[x-1] != 'b':
                  imageIdx += 1
               if x<len(rowData)-1 and rowData[x+1] != tileSymbol and rowData[x+1] != 'b':
                  imageIdx += 4
               mapImage.blit( self.tiles[self.tileSymbols[tileSymbol]].image[imageIdx],                        (x_px, y_px) )   # data
            else:
               mapImage.blit( self.tiles[self.tileSymbols[tileSymbol]].image,                                  (x_px, y_px) )   # data

      # Blit the decoration on the image
      if mapDecorations is None:
         mapDecorations = self.maps[mapName].mapDecorations
      for mapDecoration in mapDecorations:
         if mapDecoration.type is None:
            continue
         decoration = self.decorations[mapDecoration.type]
         tilePosition_px = (mapDecoration.point + imagePad_tiles) * self.tileSize_pixels
         x_px = tilePosition_px.x + (self.tileSize_pixels - decoration.image.get_width()) / 2
         y_px = tilePosition_px.y + self.tileSize_pixels - decoration.image.get_height()
         mapImage.blit( decoration.image,                                                                      (x_px, y_px) )   # decoration
         
      # Return the map image info
      return MapImageInfo(mapName, mapImage, mapImageSize_tiles, mapImageSize_pixels)


def main():
   # Initialize pygame
   pygame.init()
   audioPlayer = AudioPlayer()

   # Setup to draw maps
   winSize_pixels = Point(1280, 960)
   tileSize_pixels = 16
   winSize_tiles = ( winSize_pixels / tileSize_pixels ).ceil()
   imagePad_tiles = winSize_tiles // 2
   winSize_pixels = winSize_tiles * tileSize_pixels
   screen = pygame.display.set_mode( winSize_pixels, pygame.SRCALPHA|pygame.HWSURFACE )
   clock = pygame.time.Clock()
   
   # Initialize GameInfo
   basePath = os.path.split(os.path.abspath(__file__))[0]
   gameXmlPath = os.path.join(basePath, 'game.xml')
   gameInfo = GameInfo( basePath, gameXmlPath, tileSize_pixels )
   
   # Iterate through and render the different maps
   for mapName in gameInfo.maps:
      audioPlayer.playMusic( gameInfo.maps[mapName].music )
      mapImageInfo = gameInfo.getMapImageInfo( mapName, imagePad_tiles )

      # Always rendering to the entire window but need to determine the
      # rectangle from the image which is to be scaled to the screen
      mapImageRect = pygame.Rect( 0, 0, winSize_pixels.x, winSize_pixels.y )
      screen.set_clip( pygame.Rect( 0, 0, winSize_pixels.x, winSize_pixels.y ) )
      screen.blit( mapImageInfo.mapImage.subsurface( mapImageRect ), (0,0) )
      pygame.display.flip()

      pygame.key.set_repeat (10, 10)
      isRunning = True
      while isRunning:
         for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
               if e.key == pygame.K_ESCAPE:
                  isRunning = False
               elif e.key == pygame.K_DOWN:
                  scroll_view(screen, mapImageInfo.mapImage, Direction.SOUTH, mapImageRect, 1, tileSize_pixels, True)
               elif e.key == pygame.K_UP:
                  scroll_view(screen, mapImageInfo.mapImage, Direction.NORTH, mapImageRect, 1, tileSize_pixels, True)
               elif e.key == pygame.K_LEFT:
                  scroll_view(screen, mapImageInfo.mapImage, Direction.WEST,  mapImageRect, 1, tileSize_pixels, True)
               elif e.key == pygame.K_RIGHT:
                  scroll_view(screen, mapImageInfo.mapImage, Direction.EAST,  mapImageRect, 1, tileSize_pixels, True)
            elif e.type == pygame.QUIT:
               isRunning = False
            else:
               print( 'e.type =', e.type, flush=True )
         clock.tick(30)

   # Terminate pygame
   audioPlayer.terminate()
   pygame.quit()

if __name__ == '__main__':
   main()
