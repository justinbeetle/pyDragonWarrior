#!/usr/bin/env python

import sys
import os

import pygame

from AudioPlayer import AudioPlayer
from Point import Point

# Run like this: MapImageToDatConverter.py ..\unusedAssets\maps\brecconary.png data\maps\brecconary.dat
def main():
   # Initialize pygame
   pygame.init()
   pygame.font.init()
   audioPlayer = AudioPlayer()

   # Setup to draw maps
   tileSize_pixels = 16
   winSize_tiles = Point( 1 , 1 )
   winSize_pixels = winSize_tiles * tileSize_pixels
   screen = pygame.display.set_mode( (160, 160), pygame.SRCALPHA|pygame.HWSURFACE )
   clock = pygame.time.Clock()

   # Load the map image to convert to dat file
   basePath = os.path.split(os.path.abspath(__file__))[0]
   mapImageFileName = os.path.join(basePath, sys.argv[1])
   print( 'mapImageFileName =', mapImageFileName )
   mapDatFileName = os.path.join(basePath, sys.argv[2])
   print( 'mapDatFileName =', mapDatFileName )
   mapImage = pygame.image.load(mapImageFileName).convert()
   print( 'mapImage.get_width() =', mapImage.get_width() )
   print( 'mapImage.get_width() / tileSize_pixels =', mapImage.get_width() / tileSize_pixels )
   print( 'mapImage.get_height() =', mapImage.get_height() )
   print( 'mapImage.get_height() / tileSize_pixels =', mapImage.get_height() / tileSize_pixels )

   print( 'Enter symbol for border:' )
   borderSymbol = '\n'
   while borderSymbol == '\n':
      borderSymbol = sys.stdin.read(1)

   # Convert the image to dat file
   tileImageToSymbolMap = {}
   mapDatFile = open( mapDatFileName, 'w' )

   for map_y in range( mapImage.get_height() // tileSize_pixels + 2 ):
      mapDatFile.write( borderSymbol )
   mapDatFile.write( '\n' )
   for map_y in range( mapImage.get_height() // tileSize_pixels ):
      map_y_px = map_y * tileSize_pixels
      mapDatFile.write( borderSymbol )
      for map_x in range( mapImage.get_width() // tileSize_pixels ):
         map_x_px = map_x * tileSize_pixels
         currentTile = mapImage.subsurface( pygame.Rect( map_x_px, map_y_px, tileSize_pixels, tileSize_pixels ) )
         screen.blit( currentTile, (0, 0) )
         
         # Determine if the tile has previously been seen
         isNewTile = True
         for tile in tileImageToSymbolMap:
            isTileMatch = True
            for tile_x in range( tileSize_pixels ):
               for tile_y in range( tileSize_pixels ):
                  if tile.get_at( (tile_x, tile_y) ) != currentTile.get_at( (tile_x, tile_y) ):
                     isTileMatch = False
                     break
               if not isTileMatch:
                  break
               
            if isTileMatch:
               symbol = tileImageToSymbolMap[tile]
               isNewTile = False
               break

         if isNewTile:
            pygame.display.flip()
            pygame.event.pump()
            clock.tick(5)
            # Prompt user for tile symbol
            print( 'Enter symbol for this tile ' + str(map_x) + ',' + str(map_y) + ':' )
            symbol = '\n'
            while symbol == '\n':
               symbol = sys.stdin.read(1)
            tileImageToSymbolMap[ currentTile ] = symbol
            
         mapDatFile.write( symbol )
      mapDatFile.write( borderSymbol )
      mapDatFile.write( '\n' )
   for map_y in range( mapImage.get_height() // tileSize_pixels + 2 ):
      mapDatFile.write( borderSymbol )
   mapDatFile.close()

   # Terminate pygame
   audioPlayer.terminate()
   pygame.font.quit()
   pygame.quit()

if __name__ == '__main__':
   main()
