#!/usr/bin/env python

from typing import Optional, Tuple

import argparse
from multiprocessing import freeze_support
import os
import pathlib
import subprocess
import sys
import tarfile
import traceback


def is_windows() -> bool:
    return sys.platform in ("win32", "cygwin")


def get_writeable_application_path(
    application_path: str, application_name: str, directory: str
) -> Tuple[bool, str]:
    """Get a writeable directory path for this application

    First try to use the path of the application.  Then try APPDATA on Windows.  Finally try the home directory.
    Return a tuple of a bool indicating success and the path identified
    """
    writeable_application_base_path = application_path
    writeable_application_path = os.path.join(
        writeable_application_base_path, directory
    )

    def is_path_writeable() -> bool:
        return (
            os.access(writeable_application_path, os.W_OK)
            if os.path.exists(writeable_application_path)
            else os.access(writeable_application_base_path, os.W_OK)
        )

    if not is_path_writeable():
        # Don't have access to write saved game files in the application path.  Determine an alternate location.
        if is_windows() and "APPDATA" in os.environ:
            # On Windows, prefer a base path in the user's AppData\Roaming directory
            writeable_application_base_path = os.environ["APPDATA"]
        else:
            # Default to a base path in the user's home directory
            writeable_application_base_path = str(pathlib.Path.home())

        writeable_application_path = os.path.join(
            writeable_application_base_path, f".{application_name}", directory
        )

    return is_path_writeable(), writeable_application_path


def main() -> None:
    application_name = "pyDragonWarrior"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="Set the game configuration xml file to use",
    )
    parser.add_argument(
        "-g",
        "--gamepad",
        action="store_true",
        default=None,
        help="Gamepad (if present) will be used for providing user inputs",
    )
    parser.add_argument(
        "-k",
        "--keyboard",
        dest="gamepad",
        action="store_false",
        help="Keyboard will be used for providing user inputs",
    )
    parser.add_argument(
        "-u",
        "--force-use-unlicensed-assets",
        action="store_true",
        default=False,
        help="Force using the unlicensed assets",
    )
    parser.add_argument(
        "-s",
        "--skip-pip-install",
        dest="perform_pip_install",
        action="store_false",
        default=True,
        help="Skip performing a pip install to a venv",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--width",
        default=None,
        help="Window width - should be specified alongside --height",
    )
    parser.add_argument(
        "--height",
        default=None,
        help="Window height - should be specified alongside --width",
    )
    parser.add_argument("save", nargs="?", help="Load a specific saved game file")
    args = parser.parse_args()
    # print('args =', args, flush=True)

    # Determine if application is a script file or frozen exe
    is_frozen = getattr(sys, "frozen", False)
    if is_frozen:
        # Executing as a PyInstaller binary executable
        if args.verbose:
            print("Running as a PyInstaller binary executable", flush=True)
        application_path = os.path.dirname(os.path.abspath(sys.executable))
        base_path = os.path.dirname(os.path.abspath(__file__))
    else:
        # Normal execution
        if args.verbose:
            print("Running as a Python script", flush=True)
        application_path = base_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    # Set the current working directory to the base path so that the game can be run from any path
    # First ensure sys.argv[0] is an absolute path
    sys.argv[0] = os.path.abspath(sys.argv[0])
    os.chdir(base_path)

    # Load required Python libraries
    if not is_frozen and args.perform_pip_install:
        # If not in a virtual environment, create one first
        venv_path: Optional[str] = None
        if "VIRTUAL_ENV" not in os.environ:
            # Identify path for venv
            venv_path_found, venv_path = get_writeable_application_path(
                application_path, application_name, "venv"
            )
            if venv_path_found:
                if args.verbose:
                    print(
                        f"Not running in a venv, will switch to {venv_path}", flush=True
                    )
            else:
                venv_path = None
                print(
                    "ERROR: Failed to identify a venv path to which the current user has write access",
                    flush=True,
                )
        else:
            venv_path = os.environ["VIRTUAL_ENV"]
            if args.verbose:
                print(f"Already running in venv {venv_path}", flush=True)

        if venv_path:
            created_venv = False
            if args.verbose:
                subprocess_stdout = None
                subprocess_stderr = None
            else:
                subprocess_stdout = subprocess.DEVNULL
                subprocess_stderr = subprocess.DEVNULL

            # Create the venv if it doesn't already exist
            import venv

            venv_builder = venv.EnvBuilder(with_pip=True)
            venv_context = venv_builder.ensure_directories(venv_path)
            if not os.path.exists(venv_context.env_exe):
                print(f"Creating venv {venv_path}...", flush=True)
                created_venv = True
            try:
                venv_builder.create(venv_path)
            except Exception:
                if args.verbose:
                    print(f"Failed to create venv {venv_path}", flush=True)
                    traceback.print_exc()

            # Run pip to install the required packages (it also builds and installs the wheel for this repo)
            if args.verbose or created_venv:
                print("Running pip install...", flush=True)
            subprocess.check_call(
                [venv_context.env_exe, "-m", "pip", "install", "."],
                stdout=subprocess_stdout,
                stderr=subprocess_stderr,
            )
            if not args.verbose and created_venv:
                print("Completed pip install", flush=True)

            # Run the application from the venv
            if venv_context.env_exe != sys.executable:
                if args.verbose:
                    print("Running application in venv", flush=True)
                exit(subprocess.check_call([venv_context.env_exe] + sys.argv + ["-s"]))
        elif args.verbose:
            print("Not running in a venv", flush=True)

    # Identify the path for saved gamed files
    saves_path_found, saves_path = get_writeable_application_path(
        application_path, application_name, "saves"
    )
    if not saves_path_found:
        print(
            "ERROR: Failed to identify a saves path to which the current user has write access",
            flush=True,
        )
    elif args.verbose:
        print("Running with a save path of", saves_path, flush=True)

    os.environ[
        "PYGAME_HIDE_SUPPORT_PROMPT"
    ] = "1"  # Silence pygame outputs to standard out
    import pygame
    from generic_utils.point import Point
    from pygame_utils.audio_player import AudioPlayer
    from pydw.game_dialog import GameDialog
    from pydw.game_loop import GameLoop

    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.display.set_caption(application_name)
    icon_image_filename = os.path.join(base_path, "icon.png")
    if os.path.exists(icon_image_filename):
        try:
            icon_image = pygame.image.load(icon_image_filename)
            pygame.display.set_icon(icon_image)
        except Exception:
            print("ERROR: Failed to load", icon_image_filename, flush=True)

    GameDialog.force_use_menus_for_text_entry = args.gamepad

    # Initialize the game
    win_size_pixels: Optional[Point] = None  # Point(2560, 1340)
    if args.width and args.height:
        win_size_pixels = Point(args.width, args.height)
    tile_size_pixels = 16
    tile_scaling_factor = 3

    def create_game_loop(
        game_xml_path: str, error_msg: Optional[str] = None
    ) -> Optional[GameLoop]:
        try:
            return GameLoop(
                saves_path,
                base_path,
                game_xml_path,
                win_size_pixels,
                tile_size_pixels,
                tile_scaling_factor,
                verbose=args.verbose,
            )
        except Exception:
            if args.verbose:
                if error_msg is None:
                    error_msg = f"Failed to load game using {game_xml_path}"
                print(f"ERROR: {error_msg}", flush=True)
                traceback.print_exc()
        return None

    game_loop: Optional[GameLoop] = None
    if args.config is not None:
        # Attempt to load game using a user specified configuration
        game_loop = create_game_loop(args.config)

    if game_loop is None:
        if not args.force_use_unlicensed_assets:
            # Attempt to load game using the licensed assets
            game_xml_path = os.path.join(base_path, "game_licensed_assets.xml")
            game_loop = create_game_loop(
                game_xml_path, "Failed to load using licensed assets"
            )

            if not game_loop:
                # Attempt to load game using the licensed assets after extracting missing assets from the asset pack
                asset_pack_path = os.path.join(base_path, "licensed_assets.tgz")
                if os.path.exists(asset_pack_path):
                    with tarfile.open(asset_pack_path) as asset_pack_file:
                        if args.verbose:
                            print("Extracting assets...", flush=True)
                        for asset_file in asset_pack_file:
                            if not os.path.exists(
                                os.path.join(base_path, asset_file.name)
                            ):
                                asset_pack_file.extract(asset_file)
                                if args.verbose:
                                    print(f"   {asset_file.name}", flush=True)
                    game_loop = create_game_loop(
                        game_xml_path,
                        "Failed to load licensed assets after extracting from asset pack",
                    )

        if game_loop is None:
            # Fallback to using unlicensed assets
            game_xml_path = os.path.join(base_path, "game.xml")
            game_loop = create_game_loop(
                game_xml_path, "ERROR: Failed to load unlicensed assets"
            )

    # Run the game
    if game_loop is not None:
        game_loop.run(args.save)
    elif not args.verbose:
        print(
            "ERROR: Failed to load the game.  Run with the -v option for more info.",
            flush=True,
        )

    # Exit the game
    AudioPlayer().terminate()
    pygame.joystick.quit()
    pygame.quit()


if __name__ == "__main__":
    freeze_support()  # This allows pyinstaller Windows executables to support the use of concurrent.futures
    try:
        main()
    except Exception:
        traceback.print_exc()
