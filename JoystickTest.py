#!/usr/bin/env python

import os

import pygame

def main():
   # Initialize pygame
   pygame.init()
   print( 'pygame.joystick.get_count() =', pygame.joystick.get_count(), flush=True )
   joysticks = []
   for x in range(pygame.joystick.get_count()):
      joystick = pygame.joystick.Joystick(x)
      print( 'joystick.get_id() =', joystick.get_id(), flush=True )
      print( 'joystick.get_name() =', joystick.get_name(), flush=True )
      if joystick.get_name() == 'Controller (Xbox One For Windows)':
         print( 'Initializing joystick...', flush=True )
         joystick.init()
         joysticks.append( joystick ) 

   # Setup to draw maps
   winSize_pixels = (1280, 960)
   pygame.display.set_mode( winSize_pixels, pygame.SRCALPHA|pygame.HWSURFACE )

   isRunning = True
   while isRunning:
      for e in pygame.event.get():
         #print( 'e =', e, flush=True )
         if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
               isRunning = False
         elif e.type == pygame.JOYBUTTONDOWN:
            print( 'e =', e, flush=True )
            print( 'e.button =', e.button, flush=True )
         elif e.type == pygame.JOYHATMOTION:
            print( 'e =', e, flush=True )
            print( 'e.value =', e.value, flush=True )
         elif e.type == pygame.QUIT:
            isRunning = False
      pygame.time.Clock().tick(30)

   # Terminate pygame
   pygame.joystick.quit()
   pygame.quit()

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
