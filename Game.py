#!/usr/bin/env python

import os
import subprocess
import sys


def main() -> None:
    # Determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        # Executing as a pyinstaller binary executable
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        # Normal execution
        application_path = os.path.dirname(__file__)

        # Load required Python libraries
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', '-r',
                               os.path.join(application_path, 'requirements.txt')])

    import pygame
    from AudioPlayer import AudioPlayer
    from GameDialog import GameDialog
    from GameLoop import GameLoop

    # Set the current working directory to the location of this file so that the game can be run from any path
    os.chdir(os.path.dirname(__file__))
    base_path = os.path.split(os.path.abspath(__file__))[0]
    icon_image_filename = os.path.join(base_path, 'icon.png')

    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.display.set_caption('pyDragonWarrior')
    if os.path.exists(icon_image_filename):
        try:
            icon_image = pygame.image.load(icon_image_filename)
            pygame.display.set_icon(icon_image)
        except:
            print('ERROR: Failed to load', icon_image_filename, flush=True)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gamepad', help='Gamepad (if present) will be used for providing user inputs',
                        action='store_true', default=None)
    parser.add_argument('-k', '--keyboard', dest='gamepad', help='Keyboard will be used for providing user inputs',
                        action='store_false')
    parser.add_argument('save', nargs='?', help='Load a specific saved game file')
    args = parser.parse_args()
    # print('args =', args, flush=True)

    GameDialog.force_use_menus_for_text_entry = args.gamepad

    # Initialize the game
    game_xml_path = os.path.join(base_path, 'game.xml')
    win_size_pixels = None  # Point(2560, 1340)
    tile_size_pixels = 16 * 3
    game_loop = GameLoop(application_path, base_path, game_xml_path, win_size_pixels, tile_size_pixels)

    # Run the game
    game_loop.run(args.save)

    # Exit the game
    AudioPlayer().terminate()
    pygame.joystick.quit()
    pygame.quit()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        print(traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                         e,
                                         e.__traceback__),
              file=sys.stderr, flush=True)
        traceback.print_exc()
