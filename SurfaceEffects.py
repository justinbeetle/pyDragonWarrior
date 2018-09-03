#!/usr/bin/env python

import os

import pygame

class SurfaceEffects:

   def fadeToBlackAndBack(screen):
      backgroundSurface = screen.copy()
      fadeSurface = pygame.Surface( screen.get_size() )
      fadeSurface.fill( pygame.Color('black') )
      SurfaceEffects.fadeOut( screen, backgroundSurface, fadeSurface )
      SurfaceEffects.fadeIn( screen, backgroundSurface, fadeSurface )

   def fadeToBlack(screen):
      startingSurface = screen.blit( origScreen, (0, 0) )
      fadeSurface = pygame.Surface( screen.get_size() )
      fadeSurface.fill( pygame.Color('black') )
      SurfaceEffects.fadeOut( screen, backgroundSurface, fadeSurface )

   def fadeOut(screen, backgroundSurface, fadeSurface):
      for i in range(15, 256, 16):
         fadeSurface.set_alpha(i)
         screen.blit( backgroundSurface, (0, 0) )
         screen.blit( fadeSurface, (0, 0) )
         pygame.display.flip()
         pygame.time.Clock().tick(30)

   def fadeIn(screen, backgroundSurface, fadeSurface):
      for i in range(240, -1, -16):
         fadeSurface.set_alpha(i)
         screen.blit( backgroundSurface, (0, 0) )
         screen.blit( fadeSurface, (0, 0) )
         pygame.display.flip()
         pygame.time.Clock().tick(30)

   def flickering(screen):
      backgroundSurface = screen.copy()
      flickerSurface = pygame.Surface( screen.get_size() )
      flickerSurface.fill( pygame.Color('white') )
      flickerSurface.set_alpha(128)
      
      for flickerTimes in range( 10 ):
         screen.blit( backgroundSurface, (0, 0) )
         screen.blit( flickerSurface, (0, 0) )
         pygame.display.flip()
         pygame.time.Clock().tick(30)
         
         screen.blit( backgroundSurface, (0, 0) )
         pygame.display.flip()
         pygame.time.Clock().tick(30)

   def pinkTinge(screen):
      PINK = pygame.Color(252, 116, 96)
      pygame.transform.threshold(screen, screen, search_color=pygame.Color('white'), threshold=pygame.Color(50, 50, 50), set_color=PINK, inverse_set=True)
      pygame.display.flip()

   def rainbowEffect(screen, waterTile):
      origScreen = screen.copy()
      waterColor = pygame.transform.average_color(waterTile)
      rainbowColors = [pygame.Color('red'),
                       pygame.Color('orange'),
                       pygame.Color('yellow'),
                       pygame.Color('green'),
                       pygame.Color('blue'),
                       pygame.Color('green'),
                       pygame.Color(75,0,130), #pygame.Color('indigo'),
                       pygame.Color('violet')]
      
      # Cycle through the rainbow colors
      for i in range( 5 ):
         for rainbowColor in rainbowColors:
            try:
               pygame.transform.threshold(screen, origScreen, search_color=waterColor, threshold=pygame.Color(50, 50, 50), set_color=rainbowColor, inverse_set=True)
               pygame.display.flip()
               pygame.time.Clock().tick(15)
            except:
               print( 'Color not found: ', color, flush=True )

      # Restore original screen
      screen.blit( origScreen, (0, 0) )
      pygame.display.flip()

def main():
   # Initialize pygame
   pygame.init()

   # Terminate pygame
   pygame.quit()

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
