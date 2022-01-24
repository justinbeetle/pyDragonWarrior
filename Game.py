#!/usr/bin/env python

import argparse
import os
import pathlib
import subprocess
import sys


def get_saves_path(application_path: str, application_name: str) -> str:
    saves_base_path = application_path
    saves_path = os.path.join(saves_base_path, 'saves')
    if (os.path.exists(saves_path) and not os.access(saves_path, os.W_OK)) or not os.access(application_path, os.W_OK):
        # Don't have access to write saved game files in the application path.  Determine an alternate location.
        is_windows = sys.platform in ('win32', 'cygwin')
        if is_windows and 'APPDATA' in os.environ:
            # On Windows, prefer a base path in the user's AppData\Roaming directory
            saves_base_path = os.environ['APPDATA']
        else:
            # Default to a base path in the user's home directory
            saves_base_path = pathlib.Path.home()

        # Default to using the home directory
        saves_path = os.path.join(saves_base_path, f'.{application_name}', 'saves')

    if (os.path.exists(saves_path) and not os.access(saves_path, os.W_OK)) or not os.access(saves_base_path, os.W_OK):
        print('ERROR: Failed to identify a save path to which the current user has write access', flush=True)

    return saves_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gamepad', help='Gamepad (if present) will be used for providing user inputs',
                        action='store_true', default=None)
    parser.add_argument('-k', '--keyboard', dest='gamepad', help='Keyboard will be used for providing user inputs',
                        action='store_false')
    parser.add_argument('-u', '--force-use-unlicensed-assets', help='Force using the unlicensed assets',
                        action='store_true', default=False)
    parser.add_argument('-p', '--skip_pip_install', dest='perform_pip_install', help='Skip performing a pip install',
                        action='store_false', default=True)
    parser.add_argument('save', nargs='?', help='Load a specific saved game file')
    args = parser.parse_args()
    # print('args =', args, flush=True)

    # Determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        # Executing as a pyinstaller binary executable
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        # Normal execution
        application_path = os.path.dirname(__file__)

        # Load required Python libraries
        if args. perform_pip_install:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', '-r',
                                   os.path.join(application_path, 'requirements.txt')])

    application_name = 'pyDragonWarrior'
    saves_path = get_saves_path(application_path, application_name)

    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Silence pygame outputs to standard out
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
    pygame.display.set_caption(application_name)
    if os.path.exists(icon_image_filename):
        try:
            icon_image = pygame.image.load(icon_image_filename)
            pygame.display.set_icon(icon_image)
        except:
            print('ERROR: Failed to load', icon_image_filename, flush=True)

    GameDialog.force_use_menus_for_text_entry = args.gamepad

    # Initialize the game
    if not args.force_use_unlicensed_assets and os.path.exists(os.path.join(base_path, 'data', 'licensed_assets')):
        game_xml_path = os.path.join(base_path, 'game_licensed_assets.xml')
    else:
        game_xml_path = os.path.join(base_path, 'game.xml')
    win_size_pixels = None  # Point(2560, 1340)
    tile_size_pixels = 16 * 3
    game_loop = GameLoop(saves_path, base_path, game_xml_path, win_size_pixels, tile_size_pixels)

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
