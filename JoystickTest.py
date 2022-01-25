#!/usr/bin/env python

import pygame


def main():
    # Initialize pygame
    pygame.init()
    print('pygame.joystick.get_count() =', pygame.joystick.get_count(), flush=True)
    joysticks = []
    for x in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(x)
        print('joystick.get_id() =', joystick.get_id(), flush=True)
        print('joystick.get_name() =', joystick.get_name(), flush=True)
        if joystick.get_name() == 'Controller (Xbox One For Windows)':
            print('Initializing joystick...', flush=True)
            joystick.init()
            joysticks.append(joystick)

    # Setup to draw maps
    win_size_pixels = (1280, 960)
    pygame.display.set_mode(win_size_pixels, pygame.SRCALPHA | pygame.HWSURFACE)

    is_running = True
    while is_running:
        for event in pygame.event.get():
            print('event =', event, flush=True )
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                print('event =', event, flush=True)
                print('event.button =', event.button, flush=True)
            elif event.type == pygame.JOYHATMOTION:
                print('event =', event, flush=True)
                print('event.value =', event.value, flush=True)
            elif event.type == pygame.QUIT:
                is_running = False
        pygame.time.wait(25)

    # Terminate pygame
    pygame.joystick.quit()
    pygame.quit()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import sys
        import traceback
        print(traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                         e,
                                         e.__traceback__),
              file=sys.stderr, flush=True)
