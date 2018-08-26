#!/usr/bin/env python

import sys
import os
import math
import random
from enum import Enum

import pygame

from AudioPlayer import AudioPlayer
from Point import Point
from GameTypes import *
from GameInfo import GameInfo
from CharacterState import CharacterState
from GameState import GameState
from GameDialog import *
from SurfaceEffects import SurfaceEffects

class GameMode(Enum):
   TITLE_SCREEN = 1
   EXPLORING = 2
   ENCOUNTER = 3

class Game:
   def __init__(self, basePath, gameXmlPath, desiredWinSize_pixels, tileSize_pixels, savedGameFile = None):

      self.gameState = GameState( basePath, gameXmlPath, desiredWinSize_pixels, tileSize_pixels, savedGameFile )
      GameDialog.init( self.gameState.winSize_tiles, tileSize_pixels )

   def getEvents(self):
      # Translate joystick events to keyboard events
      events = pygame.event.get()

      # Process joystick taking into account keyboard repeat settings
      isKeyboardRepeatEnabled = pygame.key.get_repeat() != (0, 0)

      # Generate key down events from a joystick hat for the case were repeats are enabled
      if isKeyboardRepeatEnabled:
         for joystickId in range( pygame.joystick.get_count() ):
            joystick = pygame.joystick.Joystick( joystickId )
            if not joystick.get_init():
               continue
            for hatId in range( joystick.get_numhats() ):
               event = self.getEventForJoystickHatPosition( joystick.get_hat( hatId ) )
               if event is not None:
                  events.append( event )

      # Translate joystick events to keyboard events
      for e in events:
         event = None
         eventDict = {}
         if e.type == pygame.JOYBUTTONDOWN:
            if e.button == 0:
               eventDict['key'] = pygame.K_RETURN
               event = pygame.event.Event( pygame.KEYDOWN, eventDict )
            elif e.button == 1:
               eventDict['key'] = pygame.K_SPACE
               event = pygame.event.Event( pygame.KEYDOWN, eventDict )
         elif e.type == pygame.JOYHATMOTION and not isKeyboardRepeatEnabled:
            event = self.getEventForJoystickHatPosition( e.value )
         if event is not None:
            events.append( event )
               
      return events

   def getEventForJoystickHatPosition(self, hatPosition):
      event = None
      eventDict = {}
      if hatPosition == (0, -1):
         eventDict['key'] = pygame.K_DOWN
         event = pygame.event.Event( pygame.KEYDOWN, eventDict )
      elif hatPosition == (0, 1):
         eventDict['key'] = pygame.K_UP
         event = pygame.event.Event( pygame.KEYDOWN, eventDict )
      elif hatPosition == (-1, 0):
         eventDict['key'] = pygame.K_LEFT
         event = pygame.event.Event( pygame.KEYDOWN, eventDict )
      elif hatPosition == (1, 0):
         eventDict['key'] = pygame.K_RIGHT
         event = pygame.event.Event( pygame.KEYDOWN, eventDict )
      return event

   def runGameLoop(self):

      self.lastGameMode = None
      self.gameMode = GameMode.TITLE_SCREEN

      self.gameState.isRunning = True
      while self.gameState.isRunning:
         if GameMode.TITLE_SCREEN == self.gameMode:
            self.titleScreenLoop()
         elif GameMode.EXPLORING == self.gameMode:
            self.exploringLoop()
         elif GameMode.ENCOUNTER == self.gameMode:
            self.encounterLoop()

   def titleScreenLoop(self):
      # TODO: Implement
      # for now transition straight to exploring
      self.gameMode = GameMode.EXPLORING

   def traverseDialog(self, messageDialog, dialog, depth=0):

      if depth == 0:
         self.traverseDialogWaitBeforeNewText = False
         #print( 'Intialized self.traverseDialogWaitBeforeNewText to False', flush=True )
         self.dialogVariableReplacment = {}
         self.dialogVariableReplacment['[NAME]']=self.gameState.pc.name
         self.dialogVariableReplacment['[NEXT_LEVEL_XP]']=str( self.gameState.pc.calcXpToNextLevel( self.gameState.gameInfo.levels ) )

      # Convert to dialog list
      if not isinstance( dialog, list ):
         temp = dialog
         dialog = []
         dialog.append( temp )
      
      for item in dialog:
         #print( 'item =', item, flush=True )
         if isinstance( item, str ):
            # Wait for user to acknowledge that the message is read
            # before iterating to display the next part of the message
            # or exiting out of the loop when the full message has been
            # displayed.
            if self.traverseDialogWaitBeforeNewText:
               #print( 'Waiting because self.traverseDialogWaitBeforeNewText is True', flush=True )
               self.waitForAcknowledgement( messageDialog )
            #else:
            #   print( 'Not waiting because self.traverseDialogWaitBeforeNewText is False', flush=True )
               
            # Perform variable replacement
            for variable in self.dialogVariableReplacment:
               if isinstance( self.dialogVariableReplacment[variable], str ):
                  item = item.replace(variable, self.dialogVariableReplacment[variable])
            
            if not messageDialog.isEmpty():
               messageDialog.addMessage( '' )
            messageDialog.addMessage( item )
            
            messageDialog.blit( self.gameState.screen, True )
            while self.gameState.isRunning and messageDialog.hasMoreContent():
               self.waitForAcknowledgement( messageDialog )
               messageDialog.advanceContent()
               messageDialog.blit( self.gameState.screen, True )
            self.traverseDialogWaitBeforeNewText = True
            #print( 'Set self.traverseDialogWaitBeforeNewText to True', flush=True )
            
         elif isinstance( item, list ):
            if self.gameState.isRunning:
               self.traverseDialog( messageDialog, item, depth+1 )
            
         elif isinstance( item, DialogGoTo ):
            #print( 'Dialog Go To =', item, flush=True )
            if item.label in self.gameState.gameInfo.dialogSequences:
               if self.gameState.isRunning:
                  self.traverseDialog( messageDialog, self.gameState.gameInfo.dialogSequences[item.label], depth+1 )
            else:
               print( 'ERROR: ' + item.label + ' not found in dialogSequences', flush=True )
            
         elif isinstance( item, DialogVariable ):
            #print( 'Dialog Variable =', item, flush=True )
            self.dialogVariableReplacment[item.name] = item.value
            
         elif isinstance( item, dict ):
            #print( 'Dialog Option =', item, flush=True )
            self.traverseDialogWaitBeforeNewText = False
            #print( 'Set self.traverseDialogWaitBeforeNewText to False', flush=True )
            options = list( item.keys() )
            messageDialog.addMenuPrompt( options, len(options), GameDialogSpacing.SPACERS )
            messageDialog.blit( self.gameState.screen, True )
            menuResult = None
            while self.gameState.isRunning and menuResult == None:
               menuResult = self.getMenuResult( messageDialog )
            if self.gameState.isRunning:
               #print( 'menuResult =', menuResult, flush=True )
               self.traverseDialog( messageDialog, item[menuResult], depth+1 )
            
         elif isinstance( item, DialogVendorBuyOptions ):
            #print( 'Dialog Vendor Buy Options =', item, flush=True )
            nameAndGpRowData = item.nameAndGpRowData
            if nameAndGpRowData in self.dialogVariableReplacment:
               nameAndGpRowData = self.dialogVariableReplacment[nameAndGpRowData]
            if len(nameAndGpRowData) == 0:
               print('ERROR: No options from vendor', flush=True)
               self.traverseDialog( messageDialog, 'Nature calls and I need to run.  Sorry!', depth+1 )
               break
            self.traverseDialogWaitBeforeNewText = False
            #print( 'Set self.traverseDialogWaitBeforeNewText to False', flush=True )
            messageDialog.addMenuPrompt( nameAndGpRowData, 2, GameDialogSpacing.OUTSIDE_JUSTIFIED )
            messageDialog.blit( self.gameState.screen, True )
            menuResult = None
            while self.gameState.isRunning and menuResult == None:
               menuResult = self.getMenuResult( messageDialog )
            if menuResult is not None:
               #print( 'menuResult =', menuResult, flush=True )
               self.dialogVariableReplacment['[ITEM]']=menuResult
               for itemNameAndGp in nameAndGpRowData:
                  if itemNameAndGp[0] == menuResult:
                     self.dialogVariableReplacment['[COST]']=itemNameAndGp[1]
                     
         elif isinstance( item, DialogVendorSellOptions ):
            #print( 'Dialog Vendor Sell Options =', item, flush=True )
            itemTypes = item.itemTypes
            if itemTypes in self.dialogVariableReplacment:
               itemTypes = self.dialogVariableReplacment[itemTypes]
            itemRowData = self.gameState.pc.getItemRowData( True, itemTypes )
            if len(itemRowData) == 0:
               self.traverseDialog( messageDialog, 'Thou dost not have any items to sell.', depth+1 )
               break
            self.traverseDialogWaitBeforeNewText = False
            #print( 'Set self.traverseDialogWaitBeforeNewText to False', flush=True )
            messageDialog.addMenuPrompt( itemRowData, 2, GameDialogSpacing.OUTSIDE_JUSTIFIED )
            messageDialog.blit( self.gameState.screen, True )
            menuResult = None
            while self.gameState.isRunning and menuResult == None:
               menuResult = self.getMenuResult( messageDialog )
            if menuResult is not None:
               #print( 'menuResult =', menuResult, flush=True )
               self.dialogVariableReplacment['[ITEM]'] = menuResult
               self.dialogVariableReplacment['[COST]'] = str(self.gameState.gameInfo.items[menuResult].gp // 2)
         
         elif isinstance( item, DialogCheck ):
            #print( 'Dialog Check =', item, flush=True )

            # Perform variable replacement
            itemName = item.itemName;
            itemCount = item.itemCount;
            for variable in self.dialogVariableReplacment:
               if isinstance( self.dialogVariableReplacment[variable], str ):
                  itemName = itemName.replace(variable, self.dialogVariableReplacment[variable])
                  if isinstance(itemCount, str):
                     itemCount = itemCount.replace(variable, self.dialogVariableReplacment[variable])
            try:
               itemCount = int(itemCount)
            except:
               print( 'ERROR: Failed to convert itemCount to int:', itemCount, flush=True )
            if itemName == 'gp':
               checkValue = self.gameState.pc.gp
            elif itemName == 'lv':
               checkValue = self.gameState.pc.level.number
            else:
               checkValue = self.gameState.pc.getItemCount( itemName )
            #print( 'checkValue =', checkValue, flush=True )
            #print( 'itemName =', itemName, flush=True )
            #print( 'itemCount =', itemCount, flush=True )
            if checkValue < itemCount:
               self.traverseDialog( messageDialog, item.failedCheckDialog, depth+1 )
               break
               
         elif isinstance( item, DialogAction ):
            #print( 'Dialog Action =', item, flush=True )
            if item.type == DialogActionEnum.SAVE_GAME:
               self.gameState.save()
            elif item.type == DialogActionEnum.MAGIC_RESTORE:
               # TODO: Add sounds and flash
               SurfaceEffects.flickering( self.gameState.screen )
               self.gameState.pc.mp = self.gameState.pc.level.mp
               GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, True )
            elif item.type == DialogActionEnum.NIGHT_AT_INN:
               AudioPlayer().playMusic(
                  '19_-_Dragon_Warrior_-_NES_-_Inn.ogg',
                  self.gameState.gameInfo.maps[ self.gameState.mapState.mapName ].music )
               SurfaceEffects.fadeToBlackAndBack( self.gameState.screen )
               self.gameState.pc.hp = self.gameState.pc.level.hp
               self.gameState.pc.mp = self.gameState.pc.level.mp
               GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, True )
               self.traverseDialogWaitBeforeNewText = False
            else: # GAIN or LOSE item
               # Perform variable replacement
               itemName = item.itemName;
               itemCount = item.itemCount;
               for variable in self.dialogVariableReplacment:
                  if isinstance( self.dialogVariableReplacment[variable], str ):
                     itemName = itemName.replace(variable, self.dialogVariableReplacment[variable])
                     if isinstance(itemCount, str):
                        itemCount = itemCount.replace(variable, self.dialogVariableReplacment[variable])
               try:
                  itemCount = int(itemCount)
               except:
                  print( 'ERROR: Failed to convert itemCount to int:', itemCount, flush=True )
                  
               if itemName == 'gp':
                  if item.type == DialogActionEnum.GAIN_ITEM:
                     self.gameState.pc.gp += itemCount
                  elif item.type == DialogActionEnum.LOSE_ITEM:
                     self.gameState.pc.gp -= itemCount
                     if self.gameState.pc.gp < 0:
                        self.gameState.pc.gp = 0
                  GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, True )
               elif item.type == DialogActionEnum.GAIN_ITEM and itemName in self.gameState.gameInfo.items:
                  self.gameState.pc.gainItem( self.gameState.gameInfo.items[itemName], itemCount )
               elif item.type == DialogActionEnum.LOSE_ITEM:
                  self.gameState.pc.loseItem( itemName, itemCount )
                  
         else:
            print( 'ERROR: Not a supported type', flush=True )

      if depth==0:
         self.waitForAcknowledgement( messageDialog )

   def dialogLoop(self, dialog):
      # TODO: move screen and isRunning to GameState then move this functionality to GameDialog using GameState
      
      # Save off initial screen and key repeat settings
      (origRepeat1, origRepeat2) = pygame.key.get_repeat()
      pygame.key.set_repeat()
      #print( 'Disabled key repeat', flush=True )
      self.getEvents() # Clear event queue
      origScreen = self.gameState.screen.copy()

      # Create the status and message dialogs
      GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )
      messageDialog = GameDialog.createMessageDialog()

      self.traverseDialog( messageDialog, dialog )

      # Restore initial screen and key repeat settings
      pygame.key.set_repeat( origRepeat1, origRepeat2 )
      self.gameState.screen.blit( origScreen, (0, 0) )
      pygame.display.flip()

   def waitForAcknowledgement( self, messageDialog = None ):
      # TODO: move screen and isRunning to GameState then move this functionality to GameDialog using GameState

      isAwaitingAcknowledgement = True
      isWaitingIndicatorDrawn = False
      while self.gameState.isRunning and isAwaitingAcknowledgement:
         # Process events
         events = self.getEvents()
         if 0 == len(events):
            pygame.time.Clock().tick(8)
            if messageDialog is not None:
               if isWaitingIndicatorDrawn:
                  messageDialog.eraseWaitingIndicator()
               else:
                  messageDialog.drawWaitingIndicator()
               isWaitingIndicatorDrawn = not isWaitingIndicatorDrawn
               messageDialog.blit( self.gameState.screen, True )
         for e in events:
            if e.type == pygame.KEYDOWN:
               if e.key == pygame.K_ESCAPE:
                  self.gameState.isRunning = False
               elif e.key == pygame.K_RETURN or e.key == pygame.K_SPACE: # or e.key == pygame.K_DOWN or e.key == pygame.K_UP or e.key == pygame.K_LEFT or e.key == pygame.K_RIGHT:
                  isAwaitingAcknowledgement = False
            elif e.type == pygame.QUIT:
               self.gameState.isRunning = False
      if self.gameState.isRunning and isWaitingIndicatorDrawn:
         messageDialog.eraseWaitingIndicator()
         messageDialog.blit( self.gameState.screen, True )

   def getMenuResult( self, menuDialog ):
      # TODO: move screen and isRunning to GameState then move this functionality to GameDialog using GameState
      
      menuResult = None
      while self.gameState.isRunning and menuResult is None:
         events = self.getEvents()
         if 0 == len(events):
            pygame.time.Clock().tick(30)
         for e in events:
            if e.type == pygame.KEYDOWN:
               if e.key == pygame.K_ESCAPE:
                  self.gameState.isRunning = False
               elif e.key == pygame.K_RETURN:
                  menuResult = menuDialog.getSelectedMenuOption()
               elif e.key == pygame.K_SPACE:
                  menuResult = ""
               else:
                  menuDialog.processEvent( e, self.gameState.screen )
            elif e.type == pygame.QUIT:
               self.gameState.isRunning = False
               
      if menuResult == "":
         menuResult = None
         
      return menuResult

   def exploringLoop(self):
      
      pygame.key.set_repeat (10, 10)
      mapName = self.gameState.mapState.mapName

      while self.gameState.isRunning and GameMode.EXPLORING == self.gameMode:
         
         # Generate the map state a mode or map change
         if ( self.lastGameMode != self.gameMode or
              mapName != self.gameState.mapState.mapName ):

            self.lastGameMode = self.gameMode
            mapName = self.gameState.mapState.mapName

            # Play the music for the map
            audioPlayer = AudioPlayer()
            audioPlayer.playMusic( self.gameState.gameInfo.maps[ self.gameState.mapState.mapName ].music )

            # Bounds checking to ensure a valid hero/center position
            if ( self.gameState.pc.currPos_datTile is None or
                 self.gameState.pc.currPos_datTile[0] < 1 or
                 self.gameState.pc.currPos_datTile[0] < 1 or
                 self.gameState.pc.currPos_datTile[0] > self.gameState.gameInfo.maps[mapName].size[0]-1 or
                 self.gameState.pc.currPos_datTile[1] > self.gameState.gameInfo.maps[mapName].size[1]-1 ):
               print('ERROR: Invalid hero position, defaulting to middle tile', flush=True)
               self.gameState.pc.currPos_datTile = ( self.gameState.gameInfo.maps[mapName].size[0] // 2,
                                                     self.gameState.gameInfo.maps[mapName].size[1] // 2 )
               self.gameState.pc.destPos_datTile = self.gameState.pc.currPos_datTile
               self.gameState.pc.currPosOffset_imgPx = Point(0,0)
               self.gameState.pc.dir = Direction.SOUTH

            # Draw the map to the screen
            self.gameState.drawMap()

         if self.gameState.pendingDialog is not None:
            self.dialogLoop( self.gameState.pendingDialog )
            self.gameState.pendingDialog = None
         
         # Process events
         events = self.getEvents()

         for e in events:
            moving = False
            menu = False
            talking = False
            doorOpening = False
            searching = False
            pc_dir_old = self.gameState.pc.dir
                           
            if e.type == pygame.QUIT:
               self.gameState.isRunning = False 
            elif e.type == pygame.KEYDOWN:
               if e.key == pygame.K_ESCAPE:
                  self.gameState.isRunning = False
               elif e.key == pygame.K_RETURN:
                  menu = True
               elif e.key == pygame.K_DOWN:
                  self.gameState.pc.dir = Direction.SOUTH
                  moving = True
               elif e.key == pygame.K_UP:
                  self.gameState.pc.dir = Direction.NORTH
                  moving = True
               elif e.key == pygame.K_LEFT:
                  self.gameState.pc.dir = Direction.WEST
                  moving = True
               elif e.key == pygame.K_RIGHT:
                  self.gameState.pc.dir = Direction.EAST
                  moving = True

            # Allow a change of direction without moving
            if pc_dir_old != self.gameState.pc.dir:
               #print('Change of direction detected', flush=True)
               moving = False
               self.gameState.advanceTick()
               self.gameState.advanceTick()
               self.gameState.advanceTick()
               self.gameState.advanceTick()

            if menu:
               # Save off initial screen and key repeat settings
               (origRepeat1, origRepeat2) = pygame.key.get_repeat()
               pygame.key.set_repeat()
               #print( 'Disabled key repeat', flush=True )
               pygame.event.get() # Clear event queue

               GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )
               menuDialog = GameDialog.createExploringMenu()
               menuDialog.blit( self.gameState.screen, True )
               menuResult = self.getMenuResult( menuDialog )
               #print( 'menuResult =', menuResult, flush=True )
               if menuResult == 'TALK':
                  talking = True
               elif menuResult == 'STAIRS':
                  self.dialogLoop( 'Does thou not like traversing stairs automatically?' )
               elif menuResult == 'STATUS':
                  GameDialog.createFullStatusDialog( self.gameState.pc ).blit( self.gameState.screen, True )
                  self.waitForAcknowledgement()
               elif menuResult == 'SEARCH':
                  searching = True
               elif menuResult == 'SPELL':
                  availableSpellNames = self.gameState.getAvailableSpellNames()
                  if len(availableSpellNames) == 0:
                     self.dialogLoop( 'Thou hast not yet learned any spells.' )
                  else:
                     menuDialog = GameDialog.createMenuDialog(
                        Point(-1, menuDialog.pos_tile.y + menuDialog.size_tiles.h + 1),
                        None,
                        'SPELLS',
                        availableSpellNames,
                        1 )
                     menuDialog.blit( self.gameState.screen, True )
                     menuResult = self.getMenuResult( menuDialog )
                     #print( 'menuResult =', menuResult, flush=True )
                     if menuResult is not None:
                        spell = self.gameState.gameInfo.spells[menuResult]
                        if self.gameState.pc.mp >= spell.mp:
                           self.gameState.pc.mp -= spell.mp
                           
                           AudioPlayer().playSound( 'castSpell.wav' )
                           SurfaceEffects.flickering( self.gameState.screen )
                           
                           if spell.maxHpRecover > 0:
                              hpRecover = random.randrange( spell.minHpRecover, spell.maxHpRecover )
                              self.gameState.pc.hp = min( self.gameState.pc.level.hp, self.gameState.pc.hp + hpRecover )
                           elif spell.name == 'Radiant':
                              if self.gameState.lightRadius is not None and self.gameState.lightRadius < 8:
                                 # TODO: Add diminishing light radius
                                 self.gameState.lightRadius = 8
                                 self.gameState.drawMap()
                           elif spell.name == 'Outside':
                              # TODO: If not on the overworld map, go to the last coordinates from the overworld map
                              print( 'Spell not implemented', flush=True )
                           elif spell.name == 'Return':
                              # TODO: If on the overworld map, go to some coordinates
                              print( 'Spell not implemented', flush=True )
                           elif spell.name == 'Repel':
                              print( 'Spell not implemented', flush=True )
                           
                           GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )
                           self.dialogLoop( '[NAME] cast the spell of ' + spell.name + '.' )

                        else:
                           self.dialogLoop( 'Thou dost not have enough magic to cast the spell.' )
                  
               elif menuResult == 'ITEM':
                  itemRowData = self.gameState.pc.getItemRowData()
                  if len(itemRowData) == 0:
                     self.dialogLoop( 'Thou dost not have any items.' )
                  else:
                     menuDialog = GameDialog.createMenuDialog(
                        Point(-1, menuDialog.pos_tile.y + menuDialog.size_tiles.h + 1),
                        None,
                        'ITEMS',
                        itemRowData,
                        2,
                        GameDialogSpacing.OUTSIDE_JUSTIFIED )
                     menuDialog.blit( self.gameState.screen, True )
                     itemResult = self.getMenuResult( menuDialog )
                     #print( 'itemResult =', itemResult, flush=True )

                     if itemResult is not None:
                        itemOptions = self.gameState.pc.getItemOptions( itemResult )
                        if len(itemRowData) == 0:
                           self.dialogLoop( '[NAME] studied the object and was confounded by it.' )
                        else:
                           menuDialog = GameDialog.createMenuDialog(
                              Point(-1, menuDialog.pos_tile.y + menuDialog.size_tiles.h + 1),
                              None,
                              None,
                              itemOptions,
                              len(itemOptions) )
                           menuDialog.blit( self.gameState.screen, True )
                           actionResult = self.getMenuResult( menuDialog )
                           #print( 'actionResult =', actionResult, flush=True )
                           if actionResult == 'DROP':
                              # TODO: Add an are you sure prompt here
                              self.gameState.pc.loseItem( itemResult )
                           elif actionResult == 'EQUIP':
                              self.gameState.pc.equipItem( itemResult )
                           elif actionResult == 'UNEQUIP':
                              self.gameState.pc.unequipItem( itemResult )
                           elif actionResult == 'USE':
                              # TODO: Actually apply item effects here
                              usedItem = False
                              if itemResult == 'Key':
                                 doorOpening = True
                              elif itemResult == 'Torch':
                                 if self.gameState.lightRadius is not None and self.gameState.lightRadius < 1:
                                    usedItem = True
                                    self.gameState.lightRadius = 1
                                    self.gameState.drawMap()
                              else:      
                                 self.dialogLoop( '[NAME] attempted to use ' + itemResult + ' but nothing happened' )

                              if usedItem:
                                 self.gameState.pc.useItem( itemResult )
                  
                  # TODO: Implement door opening from the item list
               elif menuResult != None:
                  print( 'ERROR:  Unsupoorted menuResult =', menuResult, flush=True )

               # Erase menu and restore initial key repeat settings
               pygame.key.set_repeat( origRepeat1, origRepeat2 )
               self.gameState.drawMap()
               pygame.display.flip()

            if talking:
               talkDest_datTile = self.gameState.pc.currPos_datTile + getDirectionVector( self.gameState.pc.dir )
               talkDestTileType = self.gameState.getTileInfo(talkDest_datTile)
               if talkDestTileType.canTalkOver:
                  talkDest_datTile = talkDest_datTile + getDirectionVector( self.gameState.pc.dir )
               dialog = 'There is no one there.'
               for npc in self.gameState.npcs:
                  if talkDest_datTile == npc.currPos_datTile or talkDest_datTile == npc.destPos_datTile:
                     dialog = npc.npcInfo.dialog
                     break
               self.dialogLoop( dialog )

            if doorOpening:
               doorOpenDest_datTile = self.gameState.pc.currPos_datTile + getDirectionVector( self.gameState.pc.dir )
               foundDoor = False
               for decoration in self.gameState.mapDecorations:
                  if doorOpenDest_datTile == decoration.point and decoration.type is not None and self.gameState.gameInfo.decorations[decoration.type].removeWithKey:
                     foundDoor = True
                     if self.gameState.pc.hasItem( 'Key' ):
                        self.gameState.pc.loseItem( 'Key' )
                        self.gameState.mapDecorations.remove( decoration )
                        self.gameState.mapState = self.gameState.gameInfo.getMapImageInfo( mapName, self.gameState.imagePad_tiles, self.gameState.mapDecorations )

                        # Draw the map to the screen
                        self.gameState.drawMap()
                     else:
                        self.dialogLoop( 'Thou dost not have a key.' )
                     break
               if not foundDoor:
                  self.dialogLoop( 'There is no door to open.' )

            if searching:
               dialog = self.gameState.pc.name + ' searched the ground and found nothing.'
               for decoration in self.gameState.mapDecorations:
                  if self.gameState.pc.currPos_datTile == decoration.point:
                     if decoration.type is not None and self.gameState.gameInfo.decorations[decoration.type].removeWithSearch:
                        self.gameState.removeDecoration( decoration )
                        
                     if decoration.dialog is not None:
                        dialog = decoration.dialog
                        break

               self.dialogLoop( dialog )

            if moving:
               self.scrollTile()

         self.gameState.advanceTick()

   def encounterLoop(self):
      # Save off initial screen and key repeat settings
      (origRepeat1, origRepeat2) = pygame.key.get_repeat()
      pygame.key.set_repeat()
      #print( 'Disabled key repeat', flush=True )
      pygame.event.get() # Clear event queue
      origScreen = self.gameState.screen.copy()
      
      # Pick the monster
      monster = self.gameState.gameInfo.monsters[ random.choice( self.gameState.getTileMonsters( self.gameState.pc.currPos_datTile ) ) ]
      if monster.minHp == monster.maxHp:
         monster_hp = monster.minHp
      else:
         monster_hp = random.randrange( monster.minHp, monster.maxHp )
         
      if monster.minGp == monster.maxGp:
         monster_gp = monster.minGp
      else:
         monster_gp = random.randrange( monster.minGp, monster.maxGp )

      # Start enounter music
      audioPlayer = AudioPlayer();
      audioPlayer.playMusic( '06_-_Dragon_Warrior_-_NES_-_Fight.ogg' )
      #audioPlayer.playMusic( '14_Dragon_Quest_1_-_A_Monster_Draws_Near.mp3', '24_Dragon_Quest_1_-_Monster_Battle.mp3' )

      # Render the encounter background
      messageDialog = GameDialog.createMessageDialog( 'A ' + monster.name + ' draws near!' )
      encounterImage = self.gameState.gameInfo.maps[self.gameState.mapState.mapName].encounterImage
      encounterImageSize_pixels = Point( encounterImage.get_size() )
      encounterImageDest_pixels = Point(
         ( self.gameState.winSize_pixels.w - encounterImageSize_pixels.w ) / 2,
         messageDialog.pos_tile.y * self.gameState.gameInfo.tileSize_pixels - encounterImageSize_pixels.h )
      self.gameState.screen.blit( encounterImage, encounterImageDest_pixels )

      # Render the monster
      monsterImageSize_pixels = Point( monster.image.get_size() )
      monsterImageDest_pixels = Point(
         ( self.gameState.winSize_pixels.x - monsterImageSize_pixels.x ) / 2,
         encounterImageDest_pixels.y + encounterImageSize_pixels.y - monsterImageSize_pixels.y - self.gameState.gameInfo.tileSize_pixels )
      self.gameState.screen.blit( monster.image, monsterImageDest_pixels )

      # Display status, command prompt dialog, and command menu
      isStart = True
      while self.gameState.isRunning:
         GameDialog.createEncounterStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )

         # The first time through, check to see if the monster runs away or takes the initiative
         skipHeroAttack = False
         if isStart:
            isStart = False
            
            # Check if the monster is going to run away
            if self.gameState.pc.monsterRunCheck( monster ):
               messageDialog.addMessage( 'The ' + monster.name + ' is running away.' )
               break
            
            # Check if the monster takes the initiative and attacks first
            if self.gameState.pc.monsterInitiativeCheck( monster ):
               messageDialog.addMessage( 'The ' + monster.name + ' attacked before ' + self.gameState.pc.name + ' was ready' )
               skipHeroAttack = True

         # Perform player character turn
         if not skipHeroAttack:
            messageDialog.addMessage( '' )
            messageDialog.addEncounterPrompt()
            messageDialog.blit( self.gameState.screen, True )
            menuResult = None
            while self.gameState.isRunning and menuResult == None:
               menuResult = self.getMenuResult( messageDialog )
            if not self.gameState.isRunning:
               break

            # Process encounter menu selection
            if menuResult == 'FIGHT':

               messageDialog.addMessage( self.gameState.pc.name + ' attacks!' )

               # Check for a critical strike
               if self.gameState.pc.criticalHitCheck( monster ):
                  messageDialog.addMessage( 'Excellent move!' )
                  damage = self.gameState.pc.calcCriticalHitDamageToMonster( monster )
               else:
                  damage = self.gameState.pc.calcRegularHitDamageToMonster( monster )
                  
               # Check for a monster dodge
               if 0 == damage or self.gameState.pc.monsterDodgeCheck( monster ):
                  audioPlayer.playSound( 'Dragon Warrior [Dragon Quest] SFX (9).wav' )
                  messageDialog.addMessage( 'The ' + monster.name + ' dodges ' + self.gameState.pc.name + "'s strike." )
               else:
                  audioPlayer.playSound( 'Dragon Warrior [Dragon Quest] SFX (5).wav' )
                  messageDialog.addMessage( 'The ' + monster.name + "'s hit points reduced by " + str(damage) + '.' )
                  monster_hp -= damage
                  for flickerTimes in range( 10 ):
                     self.gameState.screen.blit( monster.dmgImage, monsterImageDest_pixels )
                     pygame.display.flip()
                     pygame.time.Clock().tick(30)
                     self.gameState.screen.blit( monster.image, monsterImageDest_pixels )
                     pygame.display.flip()
                     pygame.time.Clock().tick(30)

               # The <monster name> is asleep.
               # Thou hast done well in defeating the <monster name>.
               # Thy Experience increases by #.  Thy GOLD increases by #.
               # The <monster name> is running away.
               # <player name> started to run away.
               # <player name> started to run away but was blocked in front.
               # The <monster name> attacked before <player name> was ready.
               # The <monster name> attacks! Thy Hit Points decreased by 1.
            elif menuResult == 'RUN':
               if self.gameState.pc.monsterBlockCheck( monster ):
                  # TODO: Play sound?
                  messageDialog.addMessage( self.gameState.pc.name + ' started to run away but was blocked in front.' )
               else:
                  audioPlayer.playSound( 'runAway.wav' )
                  messageDialog.addMessage( self.gameState.pc.name + ' started to run away.' )
                  break
            elif menuResult == 'SPELL':
               print( 'Magic is not implemented', flush=True )
               self.dialogLoop( 'Thou has yet to learn magic' )
               print( 'spells =', self.gameState.getAvailableSpellNames(), flush=True )
               continue
            elif menuResult == 'ITEM':
               print( 'Items are not implemented', flush=True )
               continue
            else:
               continue

            # Check for monster death
            if monster_hp <= 0:
               break
            
            messageDialog.blit( self.gameState.screen, True )
            self.waitForAcknowledgement( messageDialog )

         # Perform monster turn
         messageDialog.addMessage( '' )
         # Check if the monster is going to run away
         if self.gameState.pc.monsterRunCheck( monster ):
            # TODO: Play sound?
            messageDialog.addMessage( 'The ' + monster.name + ' is running away.' )
            break
                  
         # Check for a player dodge
         damage = self.gameState.pc.calcHitDamageFromMonster( monster )
         if 0 == damage:
            # TODO: Play sound?
            messageDialog.addMessage( 'The ' + monster.name + ' attacks! ' + self.gameState.pc.name + ' dodges the strike.' )
         else:
            audioPlayer.playSound( 'Dragon Warrior [Dragon Quest] SFX (5).wav' )
            messageDialog.addMessage( 'The ' + monster.name + ' attacks! Thy hit points reduced by ' + str(damage) + '.' )
            self.gameState.pc.hp -= damage
            if self.gameState.pc.hp < 0:
               self.gameState.pc.hp = 0
            for flickerTimes in range( 10 ):
               offset_pixels = Point( 4, 4 )
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
         
          # Check for player death
         if self.gameState.pc.hp <= 0:
            break

      audioPlayer.stopMusic()
      if self.gameState.pc.hp <= 0:
         self.checkForPlayerDeath( messageDialog )
      elif monster_hp <= 0:
         audioPlayer.playSound( '17_-_Dragon_Warrior_-_NES_-_Enemy_Defeated.ogg' )
         self.gameState.screen.blit( encounterImage, encounterImageDest_pixels )
         messageDialog.addMessage( 'Thou has done well in defeating the ' + monster.name + '. Thy experience increases by ' + str(monster.xp) + '. Thy gold increases by ' + str(monster_gp) + '.' )
         self.gameState.pc.gp += monster_gp
         self.gameState.pc.xp += monster.xp
         GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )
         if self.gameState.pc.levelUpCheck( self.gameState.gameInfo.levels ):
            self.waitForAcknowledgement( messageDialog )
            audioPlayer.playSound( '18_-_Dragon_Warrior_-_NES_-_Level_Up.ogg' )
            messageDialog.addMessage( '\nCourage and wit have served thee well. Thou hast been promoted to the next level.' )
            GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )
            
         messageDialog.blit( self.gameState.screen, True )
         self.waitForAcknowledgement( messageDialog )

      # Restore initial screen and key repeat settings
      pygame.key.set_repeat( origRepeat1, origRepeat2 )
      if self.gameState.pc.hp > 0:
         self.gameState.screen.blit( origScreen, (0, 0) )
         pygame.display.flip()
         
      # Return to exploring after completion of encounter
      self.lastGameMode = GameMode.ENCOUNTER
      self.gameMode = GameMode.EXPLORING

   def checkForPlayerDeath( self, messageDialog = None ):
      if self.gameState.pc.hp <= 0:
         # Player death
         audioPlayer = AudioPlayer()
         AudioPlayer().stopMusic()
         AudioPlayer().playSound( '20_-_Dragon_Warrior_-_NES_-_Dead.ogg' )
         GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )
         if messageDialog is None:
            self.dialogLoop( 'Thou art dead.' )
         else:
            messageDialog.addMessage( 'Thou art dead.' )
            self.waitForAcknowledgement( messageDialog )
         self.gameState.mapState = self.gameState.gameInfo.getMapImageInfo( self.gameState.gameInfo.deathMap, self.gameState.imagePad_tiles )
         self.gameState.pc.currPos_datTile = self.gameState.gameInfo.deathHeroPos_datTile
         self.gameState.pc.currPosOffset_imgPx = Point(0,0)
         self.gameState.pc.dir = self.gameState.gameInfo.deathHeroPos_dir
         self.gameState.pendingDialog = self.gameState.gameInfo.deathDialog
         self.gameState.pc.hp = self.gameState.pc.level.hp
         self.gameState.pc.mp = self.gameState.pc.level.mp
         self.gameState.pc.gp = math.floor( self.gameState.pc.gp / 2 )
      

   def scrollTile(self): # return (destMap, destPoint) if making transition, else None

      transition = None;
      
      mapImageRect = self.gameState.getMapImageRect()
      origMapImageRect = self.gameState.getMapImageRect()
      imagePxStepSize = self.gameState.gameInfo.tileSize_pixels // 8 # NOTE: tileSize_pixels must be divisible by imagePxStepSize
      tileMoveSteps = self.gameState.gameInfo.tileSize_pixels // imagePxStepSize

      # Determine the destination tile and pixel count for the scroll
      heroDest_datTile = self.gameState.pc.currPos_datTile + getDirectionVector( self.gameState.pc.dir )
      
      # Validate if the destination tile is navagable
      movementAllowed = self.gameState.canMoveToTile( heroDest_datTile )

      # Play a walking sound or bump sound based on whether the movement was allowed
      audioPlayer = AudioPlayer();
      movementHpPenalty = 0
      if movementAllowed:
         self.gameState.pc.destPos_datTile = heroDest_datTile
         destTileType = self.gameState.getTileInfo( heroDest_datTile )

         # Determine if the movement should result in a transition to another map
         if( ( heroDest_datTile[0] == 0 or heroDest_datTile[1] == 0 or
               heroDest_datTile[0] == self.gameState.gameInfo.maps[self.gameState.mapState.mapName].size[0]-1 or
               heroDest_datTile[1] == self.gameState.gameInfo.maps[self.gameState.mapState.mapName].size[1]-1 ) and
             self.gameState.gameInfo.maps[self.gameState.mapState.mapName].leavingTransition is not None ):
            # Map leaving transition
            #print('Leaving map', self.gameState.mapState.mapName, flush=True)
            transition = self.gameState.gameInfo.maps[self.gameState.mapState.mapName].leavingTransition
         else:
            # See if this tile has any associated transitions
            print('Check for transitions at', heroDest_datTile, flush=True) # TODO: Uncomment for coordinate logging
            for pointTransition in self.gameState.gameInfo.maps[self.gameState.mapState.mapName].pointTransitions:
               #print ('Found transition at point: ', pointTransition.srcPoint, flush=True)
               if pointTransition.srcPoint == heroDest_datTile:
                  transition = pointTransition

         # Check for tile penalty effects
         if destTileType.hpPenalty > 0 and not self.gameState.pc.isIgnoringTilePenalties():
            audioPlayer.playSound( 'walking.wav' )
            movementHpPenalty = destTileType.hpPenalty
      else:
         audioPlayer.playSound( 'bump.wav' )
      
      for x in range(tileMoveSteps):
         
         if movementAllowed:
            # Erase the characters
            self.gameState.eraseCharacters()

            # Scroll the view
            scroll_view(self.gameState.screen, self.gameState.mapState.mapImage, self.gameState.pc.dir, mapImageRect, 1, imagePxStepSize)
            self.gameState.pc.currPosOffset_imgPx = Point(mapImageRect.x - origMapImageRect.x, mapImageRect.y - origMapImageRect.y)
            if self.gameState.isLightRestricted():
               self.gameState.drawMap( False )

            if movementHpPenalty > 0:
               if x == tileMoveSteps-2:
                  flickerSurface = pygame.Surface( self.gameState.screen.get_size() )
                  flickerSurface.fill( pygame.Color('red') )
                  flickerSurface.set_alpha(128)
                  self.gameState.screen.blit(flickerSurface, (0, 0) )
               elif x == tileMoveSteps-1:
                  self.gameState.drawMap( False )
         
         self.gameState.advanceTick(movementAllowed)

      if movementAllowed:
         self.gameState.pc.currPos_datTile = self.gameState.pc.destPos_datTile
         self.gameState.pc.currPosOffset_imgPx = Point(0, 0)

         # Apply health penalty and check for player death
         self.gameState.pc.hp -= movementHpPenalty
         self.checkForPlayerDeath()

         # At destination - now determine if an encounter should start
         if transition is not None:
            self.gameState.setMap( transition.destMap )
            self.gameState.pc.currPos_datTile = transition.destPoint
            self.gameState.pc.destPos_datTile = transition.destPoint
            self.gameState.pc.currPosOffset_imgPx = Point(0,0)
            self.gameState.pc.dir = transition.destDir
         elif ( len( self.gameState.getTileMonsters( self.gameState.pc.currPos_datTile ) ) > 0 and
                random.uniform(0, 1) < destTileType.spawnRate ):
            # TODO: Check for special monsters!!!
            self.gameMode = GameMode.ENCOUNTER

def main():
   pygame.init()
   pygame.mouse.set_visible( False )

   joysticks = []
   print( 'pygame.joystick.get_count() =', pygame.joystick.get_count(), flush=True )
   for joystickId in range(pygame.joystick.get_count()):
      joystick = pygame.joystick.Joystick(joystickId)
      print( 'joystick.get_id() =', joystick.get_id(), flush=True )
      print( 'joystick.get_name() =', joystick.get_name(), flush=True )
      #if joystick.get_name() == 'Controller (Xbox One For Windows)':
      print( 'Initializing joystick...', flush=True )
      joystick.init()
      joysticks.append( joystick )

   savedGameFile = None
   if len(sys.argv) > 1:
      savedGameFile = sys.argv[1]
   
   # Initialize the game
   basePath = os.path.split(os.path.abspath(__file__))[0]
   gameXmlPath = os.path.join(basePath, 'game.xml')
   winSize_pixels = None #Point(1280, 960) # TODO: Get good size for system from OS or switch to fullscreen
   tileSize_pixels = 16*3
   game = Game( basePath, gameXmlPath, winSize_pixels, tileSize_pixels, savedGameFile )

   # Run the game
   game.runGameLoop()

   # Exit the game
   AudioPlayer().terminate()
   pygame.joystick.quit()
   pygame.quit()

if __name__ == '__main__':
   main()
