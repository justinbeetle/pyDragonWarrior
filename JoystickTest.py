#!/usr/bin/env python

import os

import pygame

def main():
   # Initialize pygame
   pygame.init()
   print( 'pygame.joystick.get_count() =', pygame.joystick.get_count() )
   joysticks = []
   for x in range(pygame.joystick.get_count()):
      joystick = pygame.joystick.Joystick(x)
      print( 'joystick.get_id() =', joystick.get_id() )
      print( 'joystick.get_name() =', joystick.get_name() )
      if joystick.get_name() == 'Controller (Xbox One For Windows)':
         print( 'Initializing joystick...' )
         joystick.init()
         joysticks.append( joystick ) 

   # Setup to draw maps
   winSize_pixels = (1280, 960)
   pygame.display.set_mode( winSize_pixels, pygame.SRCALPHA|pygame.HWSURFACE )

   isRunning = True
   while isRunning:
      for e in pygame.event.get():
         #print( 'e =', e )
         if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
               isRunning = False
         elif e.type == pygame.JOYBUTTONDOWN:
            print( 'e =', e )
            print( 'e.button =', e.button )
         elif e.type == pygame.JOYHATMOTION:
            print( 'e =', e )
            print( 'e.value =', e.value )
         elif e.type == pygame.QUIT:
            isRunning = False
      pygame.time.Clock().tick(30)

   # Terminate pygame
   pygame.joystick.quit()
   pygame.quit()

if __name__ == '__main__':
   main()
