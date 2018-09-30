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
   ENCOUNTER = 3 # TODO: Remove

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
         mapOrigin = self.gameState.gameInfo.maps[ self.gameState.mapState.mapName ].origin
         if mapOrigin is not None:
            mapCoord = self.gameState.pc.currPos_datTile - mapOrigin
            self.dialogVariableReplacment['[X]'] = abs( mapCoord.x )
            self.dialogVariableReplacment['[Y]'] = abs( mapCoord.y )
            if mapCoord.x < 0:
               self.dialogVariableReplacment['[X_DIR]'] = 'West'
            else:
               self.dialogVariableReplacment['[X_DIR]'] = 'East'
            if mapCoord.y < 0:
               self.dialogVariableReplacment['[Y_DIR]'] = 'North'
            else:
               self.dialogVariableReplacment['[Y_DIR]'] = 'South'

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
               item = item.replace(variable, str(self.dialogVariableReplacment[variable]))
            
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
            try:
               (minVal, maxVal) = GameInfo.parseIntRange(item.value)
               item.value = str( random.randint( minVal, maxVal ) )
               #print( 'Dialog Variable (after value int conversion) =', item, flush=True )
            except:
               pass
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

            checkResult = True

            if item.type == DialogCheckEnum.HAS_ITEM or item.type == DialogCheckEnum.LACKS_ITEM:
               # Perform variable replacement
               itemName = item.name;
               itemCount = item.count;
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
               checkResult = checkValue >= itemCount
               if item.type == DialogCheckEnum.LACKS_ITEM:
                  checkResult = not checkResult

            elif item.type == DialogCheckEnum.IS_FACING_DOOR:
               checkResult = self.gameState.isFacingDoor()

            elif item.type == DialogCheckEnum.IS_OUTSIDE:
               checkResult = self.gameState.isOutside()

            elif item.type == DialogCheckEnum.IS_INSIDE:
               checkResult = not self.gameState.isOutside()

            elif item.type == DialogCheckEnum.IS_DARK:
               checkResult = self.gameState.isLightRestricted()

            elif item.type == DialogCheckEnum.IS_AT_COORDINATES:
               checkResult = item.mapName == self.gameState.mapState.mapName and ( item.mapPos is None or item.mapPos == self.gameState.pc.currPos_datTile )

            elif item.type == DialogCheckEnum.IS_IN_COMBAT:
               print( 'ERROR: DialogCheckEnum.IS_IN_COMBAT is not implemented to check the monster type', flush=True )
               checkResult = GameMode.ENCOUNTER == self.gameMode #and (item.name is None or item.name == 

            elif item.type == DialogCheckEnum.IS_NOT_IN_COMBAT:
               checkResult = GameMode.ENCOUNTER != self.gameMode

            else:
               print( 'ERROR: Unsupported DialogCheckEnum of', item.type, flush=True )

            if not checkResult:
               self.traverseDialog( messageDialog, item.failedCheckDialog, depth+1 )
               break
               
         elif isinstance( item, DialogAction ):
            #print( 'Dialog Action =', item, flush=True )
            
            self.traverseDialogWaitBeforeNewText = False
            #print( 'Set self.traverseDialogWaitBeforeNewText to False', flush=True )
            
            if item.type == DialogActionEnum.SAVE_GAME:
               self.gameState.save()
            elif item.type == DialogActionEnum.MAGIC_RESTORE:
               if item.count == 'unlimited':
                  self.gameState.pc.mp = self.gameState.pc.level.mp
               else:
                  (minRestore, maxRestore) = GameInfo.parseIntRange(item.count)
                  self.gameState.pc.mp += random.randint( minRestore, maxRestore )
               self.gameState.pc.mp = min( self.gameState.pc.mp, self.gameState.pc.level.mp )
               GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, True )
               
            elif item.type == DialogActionEnum.HEALTH_RESTORE:
               if item.count == 'unlimited':
                  self.gameState.pc.hp = self.gameState.pc.level.hp
               else:
                  (minRestore, maxRestore) = GameInfo.parseIntRange(item.count)
                  self.gameState.pc.hp += random.randint( minRestore, maxRestore )
               self.gameState.pc.hp = min( self.gameState.pc.hp, self.gameState.pc.level.hp )
               GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, True )

            elif item.type == DialogActionEnum.GAIN_ITEM or item.type == DialogActionEnum.LOSE_ITEM:
               # Perform variable replacement
               itemName = item.name;
               itemCount = item.count;
               for variable in self.dialogVariableReplacment:
                  if isinstance( self.dialogVariableReplacment[variable], str ):
                     itemName = itemName.replace(variable, self.dialogVariableReplacment[variable])
                     if isinstance(itemCount, str):
                        itemCount = itemCount.replace(variable, self.dialogVariableReplacment[variable])
               try:
                  itemCount = int(itemCount)
               except:
                  print( 'ERROR: Failed to convert itemCount to int so defaulting to 1:', itemCount, flush=True )
                  itemCount = 1
                  
               if itemName == 'gp':
                  if item.type == DialogActionEnum.GAIN_ITEM:
                     self.gameState.pc.gp += itemCount
                  elif item.type == DialogActionEnum.LOSE_ITEM:
                     self.gameState.pc.gp -= itemCount
                     if self.gameState.pc.gp < 0:
                        self.gameState.pc.gp = 0
                  GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, True )
               elif item.type == DialogActionEnum.GAIN_ITEM:
                  if itemName in self.gameState.gameInfo.items:
                     self.gameState.pc.gainItem( self.gameState.gameInfo.items[itemName], itemCount )
                  else:
                     self.gameState.pc.gainItem( itemName )
               elif item.type == DialogActionEnum.LOSE_ITEM:
                  self.gameState.pc.loseItem( itemName, itemCount )
                  
            elif item.type == DialogActionEnum.SET_LIGHT_DIAMETER:
               if item.count == 'unlimited':
                  self.gameState.lightDiameter = None
               else:
                  self.gameState.lightDiameter = item.count
               self.gameState.drawMap()
                  
            elif item.type == DialogActionEnum.REPEL_MONSTERS:
               print( 'ERROR: DialogActionEnum.REPEL_MONSTERS is not implemented', flush=True )
                  
            elif item.type == DialogActionEnum.GOTO_COORDINATES:
               self.gameState.pc.currPosOffset_imgPx = Point(0,0)
               if item.mapPos is not None:
                  self.gameState.pc.currPos_datTile = self.gameState.pc.destPos_datTile = item.mapPos
               if item.mapDir is not None:
                  self.gameState.pc.dir = item.mapDir
               if item.mapName is not None:
                  self.gameState.setMap( item.mapName )
               else:
                  self.gameState.setMap( self.gameState.mapState.mapName )
               self.gameState.drawMap(flipBuffer=messageDialog.isEmpty())
               if not messageDialog.isEmpty():
                  messageDialog.blit( self.gameState.screen, True )
                  
            elif item.type == DialogActionEnum.GOTO_LAST_OUTSIDE_COORDINATES:
               print( 'ERROR: DialogActionEnum.GOTO_LAST_OUTSIDE_COORDINATES is not implemented', flush=True )
                  
            elif item.type == DialogActionEnum.PLAY_SOUND:
               #print( 'Play sound', item.name, flush=True )
               AudioPlayer().playSound( item.name )
                  
            elif item.type == DialogActionEnum.PLAY_MUSIC:
               #print( 'Play music', item.name, flush=True )
               AudioPlayer().playMusic( item.name,
                  self.gameState.gameInfo.maps[ self.gameState.mapState.mapName ].music )
                  
            elif item.type == DialogActionEnum.VISUAL_EFFECT:
               if item.name == 'fadeToBlackAndBack':
                  SurfaceEffects.fadeToBlackAndBack( self.gameState.screen )
               elif item.name == 'flickering':
                  SurfaceEffects.flickering( self.gameState.screen )
               elif item.name == 'rainbowEffect':
                  SurfaceEffects.rainbowEffect( self.gameState.screen, self.gameState.gameInfo.tiles['water'].image[0] )
               else:
                  print( 'ERROR: DialogActionEnum.VISUAL_EFFECT is not implemented for effect', item.name, flush=True )
                  
            elif item.type == DialogActionEnum.ATTACK_MONSTER:
               monster=None
               if item.name in self.gameState.gameInfo.monsters:
                  monster = self.gameState.gameInfo.monsters[item.name]
               self.encounterLoop( monster=monster, victoryDialog=item.victoryDialog, runAwayDialog=item.runAwayDialog, encouterMusic=item.encounterMusic, messageDialog=messageDialog )
            
            elif item.type == DialogActionEnum.OPEN_DOOR:
               self.gameState.openDoor()

            else:
               print( 'ERROR: Unsupported DialogActionEnum of', item.type, flush=True )
                  
         else:
            print( 'ERROR: Not a supported type', item, flush=True )

      if depth==0 and not messageDialog.isEmpty():
         self.waitForAcknowledgement( messageDialog )

   def dialogLoop(self, dialog):
      # TODO: move screen and isRunning to GameState then move this functionality to GameDialog using GameState
      
      # Save off initial key repeat settings
      (origRepeat1, origRepeat2) = pygame.key.get_repeat()
      pygame.key.set_repeat()
      #print( 'Disabled key repeat', flush=True )
      self.getEvents() # Clear event queue

      # Create the status and message dialogs
      GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )
      messageDialog = GameDialog.createMessageDialog()

      self.traverseDialog( messageDialog, dialog )

      # Restore initial key repeat settings
      pygame.key.set_repeat( origRepeat1, origRepeat2 )

      # Redraw the map
      self.gameState.drawMap( True )

   def waitForAcknowledgement( self, messageDialog = None ):
      # TODO: move screen and isRunning to GameState then move this functionality to GameDialog using GameState

      # Skip waiting for acknowledgement of message dialog if the content
      # was already acknowledged.
      if messageDialog is not None and messageDialog.isAcknowledged():
         return

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
               
      if self.gameState.isRunning:
         if messageDialog is not None:
            messageDialog.acknowledge()
            if isWaitingIndicatorDrawn:
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
            self.gameState.boundsCheckPcPosition()

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
                  if not self.gameState.makeMapTransition( self.gameState.getPointTransition() ):
                     self.dialogLoop( 'There are no stairs here.' )
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
                              hpRecover = random.randint( spell.minHpRecover, spell.maxHpRecover )
                              self.gameState.pc.hp = min( self.gameState.pc.level.hp, self.gameState.pc.hp + hpRecover )
                           elif spell.name == 'Radiant':
                              if self.gameState.lightDiameter is not None and self.gameState.lightDiameter < 7:
                                 # TODO: Add diminishing light diameter
                                 self.gameState.lightDiameter = 7
                                 self.gameState.drawMap()
                           elif spell.name == 'Outside':
                              # TODO: If not on the overworld map, go to the last coordinates from the overworld map
                              print( 'Spell not implemented', flush=True )
                           elif spell.name == 'Return':
                              # TODO: Return shouldn't work from caves and the return coordinates shouldn't be hardcoded
                              self.gameState.pc.currPos_datTile = Point(43, 44)
                              self.gameState.pc.currPosOffset_imgPx = Point(0,0)
                              self.gameState.pc.dir = Direction.SOUTH
                              self.gameState.setMap( 'overworld' )
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
                              self.dialogLoop( self.gameState.gameInfo.items[itemResult].useDialog )
                  
               elif menuResult != None:
                  print( 'ERROR:  Unsupoorted menuResult =', menuResult, flush=True )

               # Erase menu and restore initial key repeat settings
               pygame.key.set_repeat( origRepeat1, origRepeat2 )
               self.gameState.drawMap()
               pygame.display.flip()

            if talking:
               talkDest_datTile = self.gameState.pc.currPos_datTile + self.gameState.pc.dir.getDirectionVector()
               talkDestTileType = self.gameState.getTileInfo(talkDest_datTile)
               if talkDestTileType.canTalkOver:
                  talkDest_datTile = talkDest_datTile + self.gameState.pc.dir.getDirectionVector()
               dialog = 'There is no one there.'
               for npc in self.gameState.npcs:
                  if talkDest_datTile == npc.currPos_datTile or talkDest_datTile == npc.destPos_datTile:
                     dialog = npc.npcInfo.dialog
                     break
               self.dialogLoop( dialog )

            if searching:
               dialog = '[NAME] searched the ground and found nothing.'
               for decoration in self.gameState.getDecorations():
                  if decoration.type is not None and self.gameState.gameInfo.decorations[decoration.type].removeWithSearch:
                     self.gameState.removeDecoration( decoration )
                        
                  if decoration.dialog is not None:
                     dialog = decoration.dialog
                     break

               self.dialogLoop( dialog )

            if moving:
               self.scrollTile()

         self.gameState.advanceTick()

   def encounterLoop( self, monster=None, victoryDialog=None, runAwayDialog=None, encouterMusic=None, messageDialog=None ):
      # TODO: Rework this to invoke from an existing dialog or None.
      #       Allow a specific monster to be passed in.
      #       Allow run away and victory dialog to be passed in and triggered.

      # Clear any menus
      self.gameState.drawMap( False )
      
      # Save off initial screen and key repeat settings
      (origRepeat1, origRepeat2) = pygame.key.get_repeat()
      pygame.key.set_repeat()
      #print( 'Disabled key repeat', flush=True )
      pygame.event.get() # Clear event queue
      origScreen = self.gameState.screen.copy()

      isRandomMonster = False
      if monster is None:
         # Check for special monsters
         specialMonster = self.gameState.getSpecialMonster()
         if specialMonster is not None:
            monster = self.gameState.gameInfo.monsters[ specialMonster.name ]
            victoryDialog = specialMonster.victoryDialog
            runAwayDialog = specialMonster.runAwayDialog
               
         # Pick the monster
         if monster is None:
            monster = self.gameState.gameInfo.monsters[ random.choice( self.gameState.getTileMonsters( self.gameState.pc.currPos_datTile ) ) ]
            isRandomMonster = True

      # Pick monster HP and GP
      monster_max_hp = monster_hp = random.randint( monster.minHp, monster.maxHp )
      monster_gp = random.randint( monster.minGp, monster.maxGp )

      # Initialize monster/player spell states
      monster_asleep = False
      monster_turns_asleep = 0
      monster_stopspelled = False
      player_asleep = False
      player_turns_asleep = 0
      player_stopspelled = False

      # Start enounter music
      if encouterMusic is None:
         encouterMusic = '06_-_Dragon_Warrior_-_NES_-_Fight.ogg'
      audioPlayer = AudioPlayer();
      audioPlayer.playMusic( encouterMusic )
      #audioPlayer.playMusic( '14_Dragon_Quest_1_-_A_Monster_Draws_Near.mp3', '24_Dragon_Quest_1_-_Monster_Battle.mp3' )

      # Render the encounter background
      hasPreExistingDialog = messageDialog is not None
      if not hasPreExistingDialog:
         messageDialog = GameDialog.createMessageDialog()
      else:
         messageDialog.addMessage( '' )
      messageDialog.addMessage( 'A ' + monster.name + ' draws near!' )
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
            
            # Check if the monster is going to run away.  Only random monsters should ever run away.
            if isRandomMonster and self.gameState.pc.monsterRunCheck( monster ):
               # TODO: Play sound?
               messageDialog.addMessage( 'The ' + monster.name + ' is running away.' )
               break
            
            # Check if the monster takes the initiative and attacks first
            if self.gameState.pc.monsterInitiativeCheck( monster ):
               messageDialog.addMessage( 'The ' + monster.name + ' attacked before ' + self.gameState.pc.name + ' was ready' )
               skipHeroAttack = True

         # Perform player character turn
         if not skipHeroAttack:
            
            messageDialog.addMessage( '' )

            # Check if player wakes up
            if player_asleep and player_turns_asleep > 0 and random.uniform(0, 1) < 0.5:
               player_asleep = False
               player_turns_asleep = 0
               messageDialog.addMessage( self.gameState.pc.name + ' awakes.' )

            if player_asleep:
               player_turns_asleep += 1
               messageDialog.addMessage( self.gameState.pc.name + ' is still asleep.' )

            ranAway = False
            while self.gameState.isRunning and not player_asleep:
            
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
                  if monster_asleep or not self.gameState.pc.monsterBlockCheck( monster ):
                     audioPlayer.playSound( 'runAway.wav' )
                     messageDialog.addMessage( self.gameState.pc.name + ' started to run away.' )

                     if runAwayDialog is not None:
                        self.traverseDialog( messageDialog, runAwayDialog, depth=1 )
                        
                     ranAway = True
                     break
                  else:
                     # TODO: Play sound?
                     messageDialog.addMessage( self.gameState.pc.name + ' started to run away but was blocked in front.' )
                     
               elif menuResult == 'SPELL':
                  availableSpellNames = self.gameState.getAvailableSpellNames()
                  if len(availableSpellNames) == 0:
                     messageDialog.addMessage( 'Thou hast not yet learned any spells.' )
                     continue
                  else:
                     menuDialog = GameDialog.createMenuDialog(
                        Point(-1, 1),
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

                           if player_stopspelled:
                              messageDialog.addMessage( self.gameState.pc.name + ' cast the spell of ' + spell.name + ' but the spell did not work.' )
                           else:
                              if spell.maxHpRecover > 0:
                                 hpRecover = random.randint( spell.minHpRecover, spell.maxHpRecover )
                                 self.gameState.pc.hp = min( self.gameState.pc.level.hp, self.gameState.pc.hp + hpRecover )
                              elif spell.maxDamageByHero > 0:
                                 monster_hp -= random.randint( spell.minDamageByHero, spell.maxDamageByHero )
                              elif spell.name == 'Sleep':
                                 # TODO: Implement this
                                 print( 'Sleep not implemented', flush=True )
                              elif spell.name == 'Stopspell':
                                 # TODO: Implement this
                                 print( 'Stopspell not implemented', flush=True )

                              messageDialog.addMessage( self.gameState.pc.name + ' cast the spell of ' + spell.name + '.' )
                           GameDialog.createEncounterStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )

                        else:
                           messageDialog.addMessage( 'Thou dost not have enough magic to cast the spell.' )
                           continue
               elif menuResult == 'ITEM':
                  print( 'Items are not implemented', flush=True )
                  continue
               else:
                  continue

               # If here the turn was successfully completed
               break

            # Check for ran away death or monster death
            if ranAway or monster_hp <= 0:
               break
            
            messageDialog.blit( self.gameState.screen, True )
            self.waitForAcknowledgement( messageDialog )

         # Perform monster turn
         messageDialog.addMessage( '' )
         
         # Check if the monster is going to run away.  Only random monsters should ever run away.
         if isRandomMonster and self.gameState.pc.monsterRunCheck( monster ):
            # TODO: Play sound?
            messageDialog.addMessage( 'The ' + monster.name + ' is running away.' )
            break

         # Determine the monster action
         chosenMonsterAction = MonsterActionEnum.ATTACK
         for monsterAction in monster.monsterActions:
            monsterHealthRatio = monster_hp / monster_max_hp
            if monsterHealthRatio > monsterAction.healthRatioThreshold:
               continue
            if MonsterActionEnum.SLEEP == monsterAction.type and player_asleep:
               continue
            if MonsterActionEnum.STOPSPELL == monsterAction.type and player_stopspelled:
               continue
            if random.uniform(0, 1) < monsterAction.probability:
               chosenMonsterAction = monsterAction.type
               break

         # Perform the monster action
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
         self.gameState.drawMap( False )
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

         if victoryDialog is not None:
            self.traverseDialog( messageDialog, victoryDialog )
         
         self.waitForAcknowledgement( messageDialog )

      # Restore initial key repeat settings
      pygame.key.set_repeat( origRepeat1, origRepeat2 )

      # Draw the map
      if self.gameState.pc.hp > 0:
         self.gameState.drawMap( True )
         
      # Return to exploring after completion of encounter
      self.lastGameMode = GameMode.ENCOUNTER
      self.gameMode = GameMode.EXPLORING

   def checkForPlayerDeath( self, messageDialog = None ):
      if self.gameState.pc.hp <= 0:
         # Player death
         self.gameState.pc.hp = 0
         audioPlayer = AudioPlayer()
         AudioPlayer().stopMusic()
         AudioPlayer().playSound( '20_-_Dragon_Warrior_-_NES_-_Dead.ogg' )
         GameDialog.createExploringStatusDialog( self.gameState.pc ).blit( self.gameState.screen, False )
         if messageDialog is None:
            self.dialogLoop( 'Thou art dead.' )
         else:
            messageDialog.addMessage( '' )
            messageDialog.addMessage( 'Thou art dead.' )
            self.waitForAcknowledgement( messageDialog )
         self.gameState.pc.currPos_datTile = self.gameState.gameInfo.deathHeroPos_datTile
         self.gameState.pc.currPosOffset_imgPx = Point(0,0)
         self.gameState.pc.dir = self.gameState.gameInfo.deathHeroPos_dir
         self.gameState.pendingDialog = self.gameState.gameInfo.deathDialog
         self.gameState.pc.hp = self.gameState.pc.level.hp
         self.gameState.pc.mp = self.gameState.pc.level.mp
         self.gameState.pc.gp = self.gameState.pc.gp // 2
         self.gameState.setMap( self.gameState.gameInfo.deathMap, respawnDecorations=True )

   def scrollTile(self): # return (destMap, destPoint) if making transition, else None

      transition = None;
      
      mapImageRect = self.gameState.getMapImageRect()
      origMapImageRect = self.gameState.getMapImageRect()
      imagePxStepSize = self.gameState.gameInfo.tileSize_pixels // 8 # NOTE: tileSize_pixels must be divisible by imagePxStepSize
      tileMoveSteps = self.gameState.gameInfo.tileSize_pixels // imagePxStepSize

      # Determine the destination tile and pixel count for the scroll
      heroDest_datTile = self.gameState.pc.currPos_datTile + self.gameState.pc.dir.getDirectionVector()
      
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
            transition = self.gameState.getPointTransition( heroDest_datTile )

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
            scroll_view(self.gameState.screen, self.gameState.getMapImage(), self.gameState.pc.dir, mapImageRect, 1, imagePxStepSize)
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
         prevPos_datTile = self.gameState.pc.currPos_datTile
         self.gameState.pc.currPos_datTile = self.gameState.pc.destPos_datTile
         self.gameState.pc.currPosOffset_imgPx = Point(0, 0)

         # Redraw the map on a transition between interior and exterior
         if ( self.gameState.isInterior( prevPos_datTile ) !=
              self.gameState.isInterior( self.gameState.pc.currPos_datTile ) ):
            self.gameState.drawMap( True )

         # Apply health penalty and check for player death
         self.gameState.pc.hp -= movementHpPenalty
         self.checkForPlayerDeath()

         # At destination - now determine if an encounter should start
         if not self.gameState.makeMapTransition( transition ):
            # Check for special monster encounters
            if self.gameState.getSpecialMonster() is not None:
               self.gameMode = GameMode.ENCOUNTER
            # Check for random encounters
            elif( len( self.gameState.getTileMonsters( self.gameState.pc.currPos_datTile ) ) > 0 and
                random.uniform(0, 1) < destTileType.spawnRate ):
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
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
