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
      for x in range(screen.get_width()):
         for y in range(screen.get_height()):
            c = screen.get_at( (x, y) )
            if c.r > 200 and c.g > 200 and c.b > 200:
               screen.set_at( (x, y), PINK )
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
