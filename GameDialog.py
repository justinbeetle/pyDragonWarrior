#!/usr/bin/env python

import os
import math

import pygame

from Point import Point
from GameTypes import *
from CharacterState import CharacterState

class GameDialogSpacing(Enum):
   EQUAL_COLUMNS = 1
   OUTSIDE_JUSTIFIED = 2
   SPACERS = 3

class GameDialog:
   winSize_tiles= Point(20, 15)
   tileSize_pixels = 48
   fontSize = 32
   fontColor = pygame.Color('white')
   font = None
   outsideSpacing_pixels = 24
   internalSpacing_pixels = 10
   selectionIndicator_pixels = 16
   
   def init( winSize_tiles, tileSize_pixels ):
      GameDialog.winSize_tiles = winSize_tiles
      GameDialog.tileSize_pixels = tileSize_pixels
      #GameDialog.fontSize = 1
      #while pygame.font.SysFont( 'arial', GameDialog.fontSize ).get_height() < tileSize_pixels:
      #   GameDialog.fontSize += 1
      #GameDialog.fontSize -= 1
      #print( 'GameDialog.fontSize =', GameDialog.fontSize )

      # Create font
      # TODO: Size font to tileSize_pixels
      #print( 'pygame.font.get_default_font() =', pygame.font.get_default_font() )
      #print( 'pygame.font.get_fonts() =', pygame.font.get_fonts() )
      GameDialog.font = pygame.font.SysFont( 'arial', GameDialog.fontSize )
      #GameDialog.font = pygame.font.Font( None, GameDialog.tileSize_pixels )

   def getSizeForContent(longestString, numRows, title):
      width_pixels = 2*GameDialog.outsideSpacing_pixels + GameDialog.font.size(longestString)[0]
      if title is not None:
         height_pixels = GameDialog.outsideSpacing_pixels + (numRows+1) * GameDialog.font.get_height() + numRows * GameDialog.internalSpacing_pixels
      else:
         height_pixels = 2*GameDialog.outsideSpacing_pixels + numRows * GameDialog.font.get_height() + (numRows-1) * GameDialog.internalSpacing_pixels
      return Point( math.ceil(width_pixels / GameDialog.tileSize_pixels), height_pixels / GameDialog.tileSize_pixels )

   def getSizeForMenu(options, numCols, title, spacingType = GameDialogSpacing.EQUAL_COLUMNS):
      rowData = GameDialog.convertOptionsToRowData( options, numCols )
      numRows = len(rowData)

      # Determine width
      longestOption_pixels = 0
      if isinstance( options[0], list ):
         for option in options:
            option_pixels = 0
            for optionCol in option:
               option_pixels += GameDialog.font.size(optionCol)[0] + 2*GameDialog.internalSpacing_pixels
            if option_pixels > longestOption_pixels:
               longestOption_pixels = option_pixels
      else:
         for option in options:
            option_pixels = GameDialog.font.size(option)[0]
            if option_pixels > longestOption_pixels:
               longestOption_pixels = option_pixels
      width_pixels = 2*GameDialog.outsideSpacing_pixels + numCols * (1.1*longestOption_pixels + 2*GameDialog.internalSpacing_pixels + GameDialog.selectionIndicator_pixels)   
            
      # Determine height
      if title is not None:
         height_pixels = GameDialog.outsideSpacing_pixels + (numRows+1) * GameDialog.font.get_height() + numRows * GameDialog.internalSpacing_pixels
      else:
         height_pixels = 2*GameDialog.outsideSpacing_pixels + numRows * GameDialog.font.get_height() + (numRows-1) * GameDialog.internalSpacing_pixels
      return Point( math.ceil(width_pixels / GameDialog.tileSize_pixels), height_pixels / GameDialog.tileSize_pixels )
   
   def __init__( self, pos_tile, size_tiles, title = None ):
      if pos_tile.x < 0:
         self.pos_tile = Point( GameDialog.winSize_tiles.x - size_tiles.x + pos_tile.x, pos_tile.y )
      else:
         self.pos_tile = Point( pos_tile )
      self.size_tiles = Point( size_tiles )
      self.title = title
      self.fontColor = GameDialog.fontColor

      # Initialize the image
      self.intitializeImage()

      self.displayedMessageLines = []
      self.remainingMessageLines = []

      self.menuOptions = None
      self.menuPrompt = None
      self.menuSpacing = None
      self.menuRow = 0
      self.menuCol = 0

   def intitializeImage( self ):
      self.image = pygame.Surface( self.size_tiles * GameDialog.tileSize_pixels )
      self.image.fill( pygame.Color('black') )
      pygame.draw.rect( self.image, self.fontColor, pygame.Rect(8, 8, self.image.get_width()-16, self.image.get_height()-16), 7 )
      if self.title is not None:
         titleImage = GameDialog.font.render( self.title, False, self.fontColor, pygame.Color('black') )
         titleImagePosX = (self.image.get_width() - titleImage.get_width()) / 2
         self.image.fill(
            pygame.Color('black'),
            pygame.Rect(
               titleImagePosX - GameDialog.internalSpacing_pixels,
               0,
               titleImage.get_width() + 2 * GameDialog.internalSpacing_pixels,
               titleImage.get_height() ) )
         self.image.blit( titleImage, (titleImagePosX, 0) )

   def createMessageDialog( messageContent = None ):
      dialog = GameDialog(
         Point( 2, GameDialog.winSize_tiles.y/2 + 1.5 ),
         Point( GameDialog.winSize_tiles.x-4, (GameDialog.winSize_tiles.y-1) / 2 - 2 ) )
      if messageContent is not None:
         dialog.addMessage( messageContent )
      return dialog

   def createMenuDialog( pos_tile, size_tiles, title, options, numCols = 2, spacingType = GameDialogSpacing.EQUAL_COLUMNS ):
      if size_tiles is None:
         size_tiles = GameDialog.getSizeForMenu( options, numCols, title, spacingType )
      dialog = GameDialog( pos_tile, size_tiles, title )
      dialog.addMenuPrompt( options, numCols, spacingType )
      return dialog

   def createExploringMenu():
      return GameDialog.createMenuDialog(
         Point(-1, 1),
         None,
         'COMMANDS',
         ['TALK', 'STATUS', 'STAIRS', 'SEARCH', 'SPELL', 'ITEM'],
         3 )

   def createEncounterMenu():
      title = 'COMMANDS'
      options = ['FIGHT', 'SPELL', 'RUN', 'ITEM']
      numCols = len(options)
      return GameDialog.createMenuDialog(
         Point(-1, 1),
         Point(
            GameDialog.getSizeForMenu( ['TALK', 'STATUS', 'STAIRS', 'SEARCH', 'SPELL', 'ITEM'], 3, title ).w,
            GameDialog.getSizeForMenu( options, numCols, title ).h ),
         title,
         options,
         numCols )

   def createStatusDialog( pos_tile, size_tiles, title, rowData ):
      if size_tiles is None:
         size_tiles = GameDialog.getSizeForContent( 'XP 1000000000', len(rowData), title )
      dialog = GameDialog( pos_tile, size_tiles, title )
      dialog.addRowData( rowData )
      return dialog

   def createExploringStatusDialog( pc ):
      return GameDialog.createStatusDialog(
         Point(1, 1),
         None,
         pc.name,
         [ [ 'LV', pc.level.name  ],
           [ 'HP', str( pc.hp )   ],
           [ 'MP', str( pc.mp )   ],
           [ 'GP', str( pc.gp )   ],
           [ 'XP', str( pc.xp )   ] ] )

   def createEncounterStatusDialog( pc ):
      return GameDialog.createStatusDialog(
         Point(1, 1),
         None,
         pc.name,
         [ [ 'LV', pc.level.name  ],
           [ 'HP', str( pc.hp )   ],
           [ 'MP', str( pc.mp )   ] ] )

   def createFullStatusDialog( pc ):
      title = pc.name
      weaponName = 'None'
      helmName = 'None'
      armorName = 'None'
      shieldName = 'None'
      if pc.weapon is not None:
         weaponName = pc.weapon.name
      if pc.helm is not None:
         helmName = pc.helm.name
      if pc.armor is not None:
         armorName = pc.armor.name
      if pc.shield is not None:
         shieldName = pc.shield.name
      rowData = [
         [ 'Level:',             pc.level.name                  ],
         [ 'Max Hit Points:',    str( pc.level.hp )             ],
         [ 'Hit Points:',        str( pc.hp )                   ],
         [ 'Max Magic Points:',  str( pc.level.mp )             ],
         [ 'Magic Points:',      str( pc.mp )                   ],
         [ 'Experience Points:', str( pc.xp )                   ],
         [ 'Gold Pieces:',       str( pc.gp )                   ],
         [ 'Strenth:',           str( pc.level.strength )       ],
         [ 'Agility:',           str( pc.level.agility )        ],
         [ 'Attack Strength:',   str( pc.getAttackStrength() )  ],
         [ 'Defense Strenth:',   str( pc.getDefenseStrength() ) ],
         [ 'Weapon:',            weaponName                     ],
         #[ 'Helm:',             helmName                        ],
         [ 'Armor:',             armorName                      ],
         [ 'Shield:',            shieldName                     ] ]
      return GameDialog.createStatusDialog(
         Point(1, 1),
         GameDialog.getSizeForContent( 'Experience Points 1000000000', len(rowData), title ),
         title,
         rowData )

   def addMessage( self, newMessage, append = True ):

      self.menuOptions = None

      # Turn message into lines of text
      newMessageLines = []
      for line in newMessage.split('\n'):
         lineToDisplay = None
         for word in line.split(' '):
            #print('word =', word)
            if lineToDisplay == None:
               lineToEvaluate = word
            else:
               lineToEvaluate = lineToDisplay + ' ' + word
            lineToEvaluateSize = Point( GameDialog.font.size(lineToEvaluate) )
            #print('lineToEvaluate =', lineToEvaluate)
            if lineToEvaluateSize[0] + 2 * GameDialog.outsideSpacing_pixels <= self.image.get_width():
               lineToDisplay = lineToEvaluate
               #print('lineToDisplay =', lineToDisplay)
            else:
               newMessageLines.append( lineToDisplay )
               lineToDisplay = word
               #print('lineToDisplay =', lineToDisplay)
         if lineToDisplay is not None:
            newMessageLines.append( lineToDisplay )
            
      # Determine the number of lines of text which can be displayed in the dialog
      numRows = self.getNumRows()

      # Merge new messeage content with old message content
      if append and len(self.displayedMessageLines) > 0:
         if 0 == len(self.remainingMessageLines):
            if len(newMessageLines) <= numRows:
               if len(self.displayedMessageLines) + len(newMessageLines) <= numRows:
                  self.displayedMessageLines += newMessageLines
               else:
                  self.displayedMessageLines = self.displayedMessageLines[ len(self.displayedMessageLines) + len(newMessageLines) - numRows : ] + newMessageLines   
            else:
               self.displayedMessageLines = newMessageLines[ 0 : numRows ]
               self.remainingMessageLines = newMessageLines[ numRows : ]
         else:
            self.remainingMessageLines += newMessageLines
            self.displayedMessageLines = self.remainingMessageLines[ 0 : numRows ]
            self.remainingMessageLines = self.remainingMessageLines[ numRows : ]
      else:
         self.displayedMessageLines = newMessageLines[ 0 : numRows ]
         self.remainingMessageLines = newMessageLines[ numRows : ]

      # Blit lines to dialog
      self.intitializeImage()
      colPosX = GameDialog.outsideSpacing_pixels
      for row in range( len(self.displayedMessageLines) ):
         rowPosY = self.getRowPosY( row )
         self.image.blit( GameDialog.font.render(self.displayedMessageLines[row], False, self.fontColor, pygame.Color('black') ), (colPosX, rowPosY) )

   def addEncounterPrompt( self ):
      self.addMenuPrompt( ['FIGHT', 'RUN', 'SPELL', 'ITEM'], 4, GameDialogSpacing.SPACERS, 'Command?' )

   def addYesNoPrompt( self, prompt = None ):
      self.addMenuPrompt( ['YES', 'NO'], 2, GameDialogSpacing.SPACERS, prompt )

   def setFontColor( fontColor ):
      GameDialog.fontColor = fontColor

   def setFontColor( self, fontColor ):
      if fontColor != self.fontColor:
         self.fontColor = fontColor
         self.refreshImage()

   def isEmpty( self ):
      return len(self.displayedMessageLines) == 0

   def hasMoreContent( self ):
      return len(self.remainingMessageLines) != 0

   def advanceContent( self ):
      # Determine the number of lines of text which can be displayed in the dialog
      numRows = self.getNumRows()

      # Shift remainingMessageLines into displayedMessageLines
      self.displayedMessageLines = self.remainingMessageLines[ 0 : numRows ]
      self.remainingMessageLines = self.remainingMessageLines[ numRows : ]

      # Refresh image
      self.refreshImage()

   def refreshImage( self ):
      # Clear the image
      self.intitializeImage()

      # Blit lines to dialog
      colPosX = GameDialog.outsideSpacing_pixels
      rowPosY = self.getStartingRowPosY()
      for lines in self.displayedMessageLines:
         self.image.blit( GameDialog.font.render(lines, False, self.fontColor, pygame.Color('black') ), (colPosX, rowPosY) )
         rowPosY += GameDialog.font.get_height() + GameDialog.internalSpacing_pixels

   def getStartingRowPosY( self ):
      return self.getRowPosY( 0 )

   def getRowPosY( self, row ):
      if self.title is None:
         startingRowPosY = GameDialog.outsideSpacing_pixels
      else:
         startingRowPosY = GameDialog.font.get_height() + GameDialog.internalSpacing_pixels
      return startingRowPosY + row * (GameDialog.font.get_height() + GameDialog.internalSpacing_pixels)

   def getNumRows( self ):
      # Determine the number of lines of text which can be displayed in the dialog
      numRows = 0
      while self.getRowPosY( numRows ) + GameDialog.font.get_height() + GameDialog.internalSpacing_pixels < self.image.get_height():
         numRows += 1
      return numRows - 1

   def addMenuPrompt( self, options, numCols, spacingType = GameDialogSpacing.EQUAL_COLUMNS, prompt = None ):
      self.addRowData( GameDialog.convertOptionsToRowData( options, numCols ), spacingType, True, prompt )

   def convertOptionsToRowData( options, numCols ):
      numRows = math.ceil( len(options) / numCols)
      rowData = []
      colsPerOption = 1
      if len(options) > 0 and isinstance( options[0], list ):
         colsPerOption = len(options[0])
      for row in range(numRows):
         temp = []
         for col in range(numCols):
            indexInOptions = row + col * numRows
            if indexInOptions < len(options):
               if isinstance( options[indexInOptions], list ):
                  for item in options[indexInOptions]:
                     temp.append( item )
               else:
                  temp.append( options[indexInOptions] )
            else:
               for colInner in range(colsPerOption):
                  temp.append( None )
         rowData.append( temp )
      return rowData

   def addRowData( self, rowData, spacingType = GameDialogSpacing.OUTSIDE_JUSTIFIED, isMenu = False, prompt = None ):
      # NOTE:  isOutsideJustified assumes 2 columns in rowData
      # NOTE:  If isMenu and isOutsideJustified, each row constitutes a single menu item

      # Determine the number of lines of text which can be displayed in the dialog
      numRows = self.getNumRows()
      availRows = numRows - len(self.displayedMessageLines)

      if len(rowData) > availRows:
         self.displayedMessageLines = self.displayedMessageLines[ len(rowData)-availRows : ]

      # Refresh image
      self.refreshImage()

      rowPosY = self.getRowPosY( len(self.displayedMessageLines) )
      numCols = 1
      if len(rowData)>0:
         numCols = len(rowData[0])
      if spacingType == GameDialogSpacing.OUTSIDE_JUSTIFIED and numCols % 2 != 0:
         print( 'ERROR: addRowData invoked with isOutsideJustified set for odd numCols =', numCols )
      firstColPosX = GameDialog.outsideSpacing_pixels
      colPosX = firstColPosX
      if prompt is not None:
         firstColPosX += GameDialog.font.size( prompt )[0] + GameDialog.internalSpacing_pixels
         colPosX = firstColPosX - GameDialog.internalSpacing_pixels
         self.image.blit( GameDialog.font.render( prompt, False, self.fontColor, pygame.Color('black') ), (GameDialog.outsideSpacing_pixels, rowPosY) )
      for row in range( len(rowData) ):
         for col in range(numCols):
            if rowData[row][col] is None:
               continue
            if spacingType == GameDialogSpacing.SPACERS:
               colPosX += GameDialog.selectionIndicator_pixels + 5 * GameDialog.internalSpacing_pixels
               if col != 0:
                  colPosX += GameDialog.font.size( rowData[row][col-1] )[0]
            elif spacingType == GameDialogSpacing.OUTSIDE_JUSTIFIED and col % 2 == 1:
               colPosX = self.image.get_width() * (col+1) / numCols - GameDialog.font.size( rowData[row][col] )[0] - GameDialog.outsideSpacing_pixels
            else:
               colPosX = firstColPosX + col * (self.image.get_width() - firstColPosX - GameDialog.outsideSpacing_pixels)/numCols
               if isMenu:
                  colPosX += GameDialog.selectionIndicator_pixels + GameDialog.internalSpacing_pixels
            self.image.blit( GameDialog.font.render( rowData[row][col], False, self.fontColor, pygame.Color('black') ), (colPosX, rowPosY) )
         rowPosY += GameDialog.font.get_height() + GameDialog.internalSpacing_pixels

      if isMenu:
         self.menuPrompt = prompt
         self.menuSpacing = spacingType
         self.menuRow = 0
         self.menuCol = 0
         if spacingType == GameDialogSpacing.OUTSIDE_JUSTIFIED:
            self.menuOptions = []
            for row in range( len(rowData) ):
               temp = []
               for col in range( numCols//2 ):
                  temp.append( rowData[row][2*col] )
               self.menuOptions.append( temp )
         else:
            self.menuOptions = rowData
         self.drawMenuIndicator()
      else:
         self.menuOptions = None

   def blit(self, surface, display = False, offset_pixels = Point(0, 0) ):
      surface.blit( self.image, self.pos_tile * GameDialog.tileSize_pixels + offset_pixels )
      if display:
         pygame.display.flip()

   def getSelectedMenuOption( self ):
      if self.menuOptions is not None:
         return self.menuOptions[self.menuRow][self.menuCol]
      return None

   def eraseMenuIndicator( self ):
      self.drawMenuIndicator( pygame.Color('black') )

   def drawMenuIndicator( self, color = None ):
      if color is None:
         color = self.fontColor
      firstColPosX = GameDialog.outsideSpacing_pixels
      colPosX = firstColPosX
      if self.menuPrompt is not None:
         firstColPosX += GameDialog.font.size( self.menuPrompt )[0] + GameDialog.internalSpacing_pixels
         colPosX = firstColPosX - GameDialog.internalSpacing_pixels
      numCols = 1
      if len(self.menuOptions)>0:
         numCols = len( self.menuOptions[0] )
      if self.menuSpacing == GameDialogSpacing.SPACERS:
         for col in range(self.menuCol + 1):
            colPosX += 4 * GameDialog.internalSpacing_pixels
            if col != 0:
               colPosX += GameDialog.font.size( self.menuOptions[self.menuRow][col-1] )[0] + GameDialog.selectionIndicator_pixels + GameDialog.internalSpacing_pixels
      else:
         colPosX = firstColPosX + self.menuCol * (self.image.get_width() - firstColPosX - GameDialog.outsideSpacing_pixels)/numCols
      numRows = len( self.menuOptions )
      rowPosY = self.getRowPosY( len(self.displayedMessageLines) + self.menuRow ) + (GameDialog.font.get_height() - GameDialog.internalSpacing_pixels) / 3
      pointlist = (
         (colPosX + 1/4 * GameDialog.selectionIndicator_pixels, rowPosY),
         (colPosX + 1/4 * GameDialog.selectionIndicator_pixels, rowPosY + GameDialog.selectionIndicator_pixels),
         (colPosX + 3/4 * GameDialog.selectionIndicator_pixels, rowPosY + GameDialog.selectionIndicator_pixels/2) )
      pygame.draw.polygon( self.image, color, pointlist)

   def eraseWaitingIndicator( self ):
      self.drawWaitingIndicator( pygame.Color('black') )

   def drawWaitingIndicator( self, color = None ):
      if color is None:
         color = self.fontColor
      colPosX = (self.image.get_width() - GameDialog.selectionIndicator_pixels) / 2
      rowPosY = self.getRowPosY( len(self.displayedMessageLines) )
      pointlist = (
         (colPosX,                                          rowPosY + 1/4 * GameDialog.selectionIndicator_pixels),
         (colPosX + GameDialog.selectionIndicator_pixels,   rowPosY + 1/4 * GameDialog.selectionIndicator_pixels),
         (colPosX + GameDialog.selectionIndicator_pixels/2, rowPosY + 3/4 * GameDialog.selectionIndicator_pixels) )
      pygame.draw.polygon( self.image, color, pointlist)
      
   def processEvent( self, e, screen ):
      if e.type == pygame.KEYDOWN:
         numCols = len( self.menuOptions[0] )
         newCol = self.menuCol
         numRows = len( self.menuOptions )
         newRow = self.menuRow
         if e.key == pygame.K_DOWN:
            newRow = (self.menuRow + 1) % numRows
         elif e.key == pygame.K_UP:
            newRow = (self.menuRow - 1) % numRows
         elif e.key == pygame.K_LEFT:
            newCol = (self.menuCol - 1) % numCols
         elif e.key == pygame.K_RIGHT:
            newCol = (self.menuCol + 1) % numCols

         # Skip over empty cells in menuOptions
         if self.menuOptions[newRow][newCol] is None:
            if newRow != self.menuRow:
               newRow = 0
            if newCol != self.menuCol:
               newCol = 0

         if newRow != self.menuRow or newCol != self.menuCol:
            # Erase old indicator
            self.eraseMenuIndicator()

            self.menuRow = newRow
            self.menuCol = newCol

            # Draw new indicator
            self.drawMenuIndicator()
            self.blit( screen, True )

def main():
   # Initialize pygame
   pygame.init()
   pygame.font.init()

   # Setup the screen
   winSize_pixels = Point(1280, 960)
   tileSize_pixels = 48
   winSize_tiles = ( winSize_pixels / tileSize_pixels ).ceil()
   winSize_pixels = winSize_tiles * tileSize_pixels
   screen = pygame.display.set_mode( winSize_pixels, pygame.SRCALPHA|pygame.HWSURFACE )
   clock = pygame.time.Clock()
   pygame.key.set_repeat()
   
   # Test out game dialog
   GameDialog.init( winSize_tiles, tileSize_pixels )
   level = Level( 1, '1', 0, 20, 20, 15, 0)
   pcState = CharacterState( 'hero', Point(5,6), Direction.SOUTH, 'CAMDEN', level )

   screen.fill( pygame.Color('pink') )
   GameDialog.createExploringStatusDialog( pcState ).blit( screen, False )
   messageDialog = GameDialog.createMessageDialog( 'Hail!' )
   messageDialog.drawWaitingIndicator()
   messageDialog.blit( screen, False )
   menu = GameDialog.createExploringMenu()
   menu.blit( screen, True )
   
   isAwaitingSelection = True
   while isAwaitingSelection:
      for e in pygame.event.get():
         if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
               isAwaitingSelection = False
            elif e.key == pygame.K_RETURN:
               isAwaitingSelection = False
               print( 'Selection made =', menu.getSelectedMenuOption() )
            else:
               menu.processEvent( e, screen )
         elif e.type == pygame.QUIT:
            isAwaitingSelection = False
      clock.tick(30)

   screen.fill( pygame.Color('pink') )
   GameDialog.createEncounterStatusDialog( pcState ).blit( screen, False )
   GameDialog.createMessageDialog( 'Word wrap testing...  Word wrap testing...  Word wrap testing...  Word wrap testing...  Word wrap testing...  Word wrap testing...' ).blit( screen, False )
   menu = GameDialog.createEncounterMenu()
   menu.blit( screen, True )
   
   isAwaitingSelection = True
   while isAwaitingSelection:
      for e in pygame.event.get():
         if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
               isAwaitingSelection = False
            elif e.key == pygame.K_RETURN:
               isAwaitingSelection = False
               print( 'Selection made =', menu.getSelectedMenuOption() )
            else:
               menu.processEvent( e, screen )
         elif e.type == pygame.QUIT:
            isAwaitingSelection = False
      clock.tick(30)

   screen.fill( pygame.Color('pink') )
   GameDialog.createEncounterStatusDialog( pcState ).blit( screen, False )
   messageDialog = GameDialog.createMessageDialog( 'Hail 1!\nHail 2!\nHail 3!\nHail 4!\nHail 5!\nHail 6!\nHail 7!\nHail 8!\nHail 9!\nHail 10!\nHail 11!' )
   while messageDialog.hasMoreContent():
      messageDialog.drawWaitingIndicator()
      messageDialog.blit( screen, True )
      pygame.time.wait(1000)
      messageDialog.advanceContent()
   messageDialog.blit( screen, True )
      
   #messageDialog.addEncounterPrompt()
   messageDialog.addMenuPrompt( ['Yes', 'No'], 2, GameDialogSpacing.SPACERS )
   messageDialog.blit( screen, True )
   isAwaitingSelection = True
   while isAwaitingSelection:
      for e in pygame.event.get():
         if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
               isAwaitingSelection = False
            elif e.key == pygame.K_RETURN:
               isAwaitingSelection = False
               print( 'Selection made =', messageDialog.getSelectedMenuOption() )
            else:
               messageDialog.processEvent( e, screen )
         elif e.type == pygame.QUIT:
            isAwaitingSelection = False
      clock.tick(30)
   messageDialog.addMessage( '\nLexie attacks!' )
   messageDialog.blit( screen, True )
   pygame.time.wait(1000)

   # Terminate pygame
   pygame.font.quit()
   pygame.quit()

if __name__ == '__main__':
   main()