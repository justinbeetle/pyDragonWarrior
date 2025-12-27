#!/usr/bin/env python

"""This module serves as the entry point for running pyDragonWarrior."""

from typing import Optional, List, Protocol, Tuple

from argparse import ArgumentParser, Namespace
import logging
from multiprocessing import freeze_support
import os
import pathlib
import subprocess
import sys
import traceback


class BootstrappableApplication(Protocol):
    """Protocol for an application which can be run via the Bootstrapper."""

    def get_application_name(self) -> str:
        """Get the name of the application"""

    def get_arg_parser(self) -> ArgumentParser:
        """Get an ArgumentParser populated for the application.

        Bootstrapper adds -v/--verbose, -vv/--very-verbose, and -s/--skip-pip-install options.  A
        BootstrappableApplication needs to reserve  these options for the Launcher, though the verbose option is generic
        and can also be used by the application."""

    def run(self, args: Namespace, base_path: str, saves_path: str) -> int:
        """Method to run the application returning an exit code for the application."""


class Bootstrapper:
    """Class for bootstrapping a Python application conforming to the BootstrappableApplication protocol.  It supports
    both Python scripts and PyInstaller "frozen" executables.  When running a Python script, it will create a Python
    venv if not already running in one, install the required Python packages, then run the application via a subprocess
    using Python from the venv.  In order to do this, it must reside in the same module as the application to be
    bootstrapped as it will be invoked before the venv with the needed packages is created such that package imports
    for packages not in the Python standard library are not yet supported."""

    def __init__(self, app: BootstrappableApplication) -> None:
        self.app = app

    @staticmethod
    def is_os_windows() -> bool:
        """Returns True if running on the Windows operating system, else False."""
        return sys.platform in ("win32", "cygwin")

    @staticmethod
    def get_application_base_path() -> str:
        """Get the repo base path (path of the root directory of the repo) or the file path if not found."""
        file_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = file_dir
        parent_dir = ""
        while current_dir != parent_dir:
            if os.path.exists(os.path.join(current_dir, "pyproject.toml")):
                return current_dir
            parent_dir = current_dir
            current_dir = os.path.dirname(current_dir)
        return file_dir

    def get_writeable_application_path(self, app_path: str, directory: str) -> Tuple[bool, str]:
        """Get a writeable directory path for this application.

        First try to use the path of the application.  Then try APPDATA on Windows.  Finally try the home directory.
        Return a tuple of a bool indicating success and the path identified
        """
        writeable_application_base_path = app_path
        writeable_application_path = os.path.join(writeable_application_base_path, directory)

        def is_path_writeable() -> bool:
            return (
                os.access(writeable_application_path, os.W_OK)
                if os.path.exists(writeable_application_path)
                else os.access(writeable_application_base_path, os.W_OK)
            )

        if not is_path_writeable():
            # Don't have access to write saved game files in the application path.  Determine an alternate location.
            if Bootstrapper.is_os_windows() and "APPDATA" in os.environ:
                # On Windows, prefer a base path in the user's AppData\Roaming directory
                writeable_application_base_path = os.environ["APPDATA"]
            else:
                # Default to a base path in the user's home directory
                writeable_application_base_path = str(pathlib.Path.home())

            writeable_application_path = os.path.join(
                writeable_application_base_path, f".{self.app.get_application_name()}", directory
            )

        return is_path_writeable(), writeable_application_path

    def run(self, argv: Optional[List[str]] = None) -> int:
        """Bootstrap the application and call its main method returning an exit code for the application."""

        # Allows pyinstaller Windows executables to support the use of concurrent.futures
        freeze_support()

        # Get the application arg parsers and add launcher specific args
        parser = self.app.get_arg_parser()
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
            "-vv",
            "--very-verbose",
            action="store_true",
            default=False,
            help="Enable very verbose",
        )
        args = parser.parse_args(argv)
        # print('args =', args, flush=True)

        # Setup logging
        self.setup_logging(args)

        # Determine if application is a script file or frozen exe
        is_frozen = getattr(sys, "frozen", False)
        if is_frozen:
            # Executing as a PyInstaller binary executable
            if args.verbose:
                print("Running as a PyInstaller binary executable", flush=True)
            application_path = os.path.dirname(os.path.abspath(sys.executable))
            base_path = os.path.dirname(os.path.abspath(__file__))

            # Close the PyInstaller splash screen
            import pyi_splash

            pyi_splash.close()
        else:
            # Normal execution
            if args.verbose:
                print("Running as a Python script", flush=True)
            application_path = base_path = self.get_application_base_path()

            # On Windows, change the app user model so that Windows doesn't use the Python icon in the taskbar.
            # NOTE: No longer using is_os_windows() here because it confuses mypy.  If mypy can't successfully determine
            #       this logic is platform specific, it will report an error on Linux for ctypes.windll.  Applying a
            #       type ignore on that line also doesn't work, as it results in an unused ignore error in Windows.
            #       See https://github.com/python/mypy/issues/9242 for more info.
            if sys.platform in ("win32", "cygwin"):
                import ctypes

                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("pydw")

        # Set the current working directory to the base path so that the game can be run from any path
        # First ensure sys.argv[0] is an absolute path
        sys.argv[0] = os.path.abspath(sys.argv[0])
        os.chdir(base_path)

        # Load required Python libraries
        if not is_frozen and args.perform_pip_install and os.path.exists("pyproject.toml"):
            exit_code = self.setup_venv(application_path, args.verbose)
            if exit_code is not None:
                # The application was run in a subprocess command in setup_venv.  Return its exit code here.
                return exit_code

        # Identify the path for saved gamed files
        saves_path_found, saves_path = self.get_writeable_application_path(application_path, "saves")
        if not saves_path_found:
            print(
                "ERROR: Failed to identify a saves path to which the current user has write access",
                flush=True,
            )
        elif args.verbose:
            print("Running with a save path of", saves_path, flush=True)

        return self.app.run(args, base_path, saves_path)

    def setup_venv(self, application_path: str, verbose: bool) -> Optional[int]:
        """Attempt to setup the Python venv, potentially creating one in the process, and then run the application
        via a subprocess command using Python from the venv (if different from our current Python).  If running a
        subprocess command, returns its exit code.  Else returns None."""

        # If not in a venv, create one first
        venv_path: Optional[str] = None
        if "VIRTUAL_ENV" not in os.environ:
            # Identify path for venv
            venv_path_found, venv_path = self.get_writeable_application_path(application_path, "venv")
            if venv_path_found:
                if verbose:
                    print(f"Not running in a venv, will switch to {venv_path}", flush=True)
            else:
                venv_path = None
                print(
                    "ERROR: Failed to identify a venv path to which the current user has write access",
                    flush=True,
                )
        else:
            venv_path = os.environ["VIRTUAL_ENV"]
            if verbose:
                print(f"Already running in venv {venv_path}", flush=True)

        if venv_path:
            created_venv = False
            subprocess_stdout = subprocess_stderr = None if verbose else subprocess.DEVNULL

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
                if verbose:
                    print(f"Failed to create venv {venv_path}", flush=True)
                    traceback.print_exc()

            # Run pip to install the required packages (it also builds and installs the wheel for this repo)
            if verbose or created_venv:
                print("Running pip install...", flush=True)
            subprocess.check_call(
                [venv_context.env_exe, "-m", "pip", "install", "."],
                stdout=subprocess_stdout,
                stderr=subprocess_stderr,
            )
            if not verbose and created_venv:
                print("Completed pip install", flush=True)

            # Run the application from the venv
            if venv_context.env_exe != sys.executable:
                if verbose:
                    print("Running application in venv", flush=True)
                return subprocess.check_call([venv_context.env_exe] + sys.argv + ["-s"])
        elif verbose:
            print("Not running in a venv", flush=True)

        return None

    @staticmethod
    def setup_logging(args: Namespace) -> None:
        logging_level = logging.WARNING
        if args.very_verbose:
            logging_level = logging.DEBUG
            args.verbose = True
        elif args.verbose:
            logging_level = logging.INFO
        logging.basicConfig(
            stream=sys.stdout,
            level=logging_level,
            format="%(asctime)s.%(msecs)d %(levelname)s %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",  # ISO-8601
        )
        # logging.debug("debug log message")
        # logging.info("info log message")
        # logging.warning("warning log message")
        # logging.error("error log message")


class Launcher:
    """Class specific to pyDragonWarrior conforming to the BootstrappableApplication protocol allowing it to be run
    via Bootstrappable.  Defines the supported command line options for pyDragonWarrior."""

    application_name = "pyDragonWarrior"

    def __init__(self) -> None:
        pass

    def get_application_name(self) -> str:
        """Get the name of the application"""
        return Launcher.application_name

    def get_arg_parser(self) -> ArgumentParser:
        """Get an ArgumentParser populated for the application."""
        parser = ArgumentParser(self.application_name)
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
        return parser

    def run(self, args: Namespace, base_path: str, saves_path: str) -> int:
        """Method to run the application returning an exit code for the application."""

        # Set PYGAME_HIDE_SUPPORT_PROMPT in the environment to silence pygame outputs to standard out
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

        from pydw.loader import Loader

        return Loader(args, base_path, saves_path).run()


def main(argv: Optional[List[str]] = None) -> int:
    """Run the pyDragonWarrior Launcher via Bootstrapper"""
    try:
        return Bootstrapper(Launcher()).run(argv)
    except Exception:
        traceback.print_exc()
    return 1


if __name__ == "__main__":
    main()
