#!/usr/bin/env python

"""Module defining MainMenu class."""

from typing import List, Optional

import glob
import os

import pygame

from pygame_utils.audio_player import AudioPlayer
from pygame_utils import game_events

from pydw.game_dialog import GameDialog
from pydw.game_dialog_evaluator import GameDialogEvaluator
from pydw.game_info import GameInfo
from pydw.game_mode import GameMode
from pydw.game_state import GameState
from pydw.loading_screen import LoadingScreen


class MainMenu(GameMode):
    """Game mode for the game's main menu supporting user selections for creating, loading, and deleting saved game
    files and selecting game settings."""

    def __init__(self, game_state: GameState, pc_name_or_file_name: Optional[str] = None) -> None:
        super().__init__(game_state.get_dialog_manager())
        self.game_state = game_state
        self.pc_name_or_file_name = pc_name_or_file_name

        self.saves_path = self.game_state.saves_path

        self.background_text = "Press any key"

    def get_saved_games(self) -> List[str]:
        """Get a list of the saved games."""
        saved_game_files = glob.glob(os.path.join(self.saves_path, "*.xml"))
        return [os.path.basename(saved_game_file)[:-4] for saved_game_file in saved_game_files]

    def get_main_menu_options(self, saved_games: List[str]) -> List[str]:
        """Get a list of the main menu options."""
        main_menu_options: List[str] = []
        if 0 < len(saved_games):
            main_menu_options.append("Continue a Quest")
        main_menu_options.append("Begin a Quest")
        if 0 < len(saved_games):
            main_menu_options.append("Delete a Quest")
        if self.game_state.should_add_math_problems_in_combat():
            main_menu_options.append("Combat Mode: Math")
        else:
            main_menu_options.append("Combat Mode: Classic")
        return main_menu_options

    def game_mode_loop(self) -> None:
        """The game loop for the main menu."""
        self.game_state.draw()

        # Wait for user input - any key press
        while self.game_state.is_running:
            waiting_for_user_input = True
            for event in game_events.get_events():
                if event.type == pygame.QUIT:
                    self.game_state.handle_quit(force=True)
                    return
                elif event.type == pygame.KEYDOWN:
                    AudioPlayer().play_sound("select")
                    waiting_for_user_input = False
                    break
            if waiting_for_user_input:
                pygame.time.wait(25)
            else:
                break

        # Remove the "Press any key" prompt
        self.background_text = ""

        # Prompt user for new game or to load a saved game
        gde = GameDialogEvaluator(self.game_state)
        dm = self.game_state.get_dialog_manager()
        pc_name_or_file_name = self.pc_name_or_file_name
        if pc_name_or_file_name is None:
            saved_games = self.get_saved_games()
            main_menu_options = self.get_main_menu_options(saved_games)
            main_menu_dialog = GameDialog.create_message_dialog()
            main_menu_dialog.add_menu_prompt(main_menu_options, 1)
            dm.add_cascading_dialog(main_menu_dialog)

            while self.game_state.is_running:
                # Update the main menu options if they have changed
                new_main_menu_options = self.get_main_menu_options(saved_games)
                if main_menu_options != new_main_menu_options:
                    main_menu_options = new_main_menu_options
                    selected_menu_position = main_menu_dialog.get_selected_menu_position()
                    main_menu_dialog.clear()
                    main_menu_dialog.add_menu_prompt(new_main_menu_options, 1)
                    if len(main_menu_options) == len(new_main_menu_options) and selected_menu_position is not None:
                        selected_row, selected_col = selected_menu_position
                        main_menu_dialog.set_selected_menu_position(selected_row, selected_col)
                main_menu_dialog.blit(self.game_state.screen, True)

                menu_result = gde.get_menu_result(main_menu_dialog)
                # print('menu_result =', menu_result, flush=True)
                if menu_result == "Continue a Quest":
                    saved_games_dialog = GameDialog.create_message_dialog()
                    saved_games_dialog.add_message("Which quest dost thou want to continue?", fully_populate=True)
                    saved_games_dialog.add_menu_prompt(saved_games, 1)
                    dm.add_cascading_dialog(saved_games_dialog)
                    menu_result = gde.get_menu_result(saved_games_dialog)
                    if menu_result is not None:
                        pc_name_or_file_name = menu_result
                        break
                    dm.remove_cascading_dialog(False)
                if menu_result == "Delete a Quest":
                    saved_games_dialog = GameDialog.create_message_dialog()
                    saved_games_dialog.add_message("Which quest dost thou want to delete?", fully_populate=True)
                    saved_games_dialog.add_menu_prompt(saved_games, 1)
                    dm.add_cascading_dialog(saved_games_dialog)
                    menu_result = gde.get_menu_result(saved_games_dialog)
                    if menu_result is not None:
                        saved_games_dialog.add_yes_no_prompt("Are you sure?")
                        saved_games_dialog.blit(self.game_state.screen, True)
                        if gde.get_menu_result(saved_games_dialog) == "YES":
                            saved_games.remove(menu_result)
                            # Delete the save game by archiving it off
                            saved_game_file = os.path.join(self.saves_path, menu_result + ".xml")
                            self.game_state.archive_saved_game_file(saved_game_file, "deleted")
                    dm.remove_cascading_dialog(False)
                elif menu_result == "Begin a Quest":
                    begin_quest_dialog = GameDialog.create_message_dialog()
                    pc_name_or_file_name = gde.wait_for_user_input(begin_quest_dialog, "What is your name?")[0]

                    if pc_name_or_file_name:
                        if pc_name_or_file_name in saved_games:
                            gde.add_and_wait_for_message(
                                "Thou hast already started a quest.  Dost thou want to start over?",
                                begin_quest_dialog,
                            )
                            begin_quest_dialog.add_yes_no_prompt()
                            begin_quest_dialog.blit(self.game_state.screen, True)
                            menu_result = gde.get_menu_result(begin_quest_dialog)
                            if menu_result == "YES":
                                # Delete the existing save game by archiving it off
                                saved_game_file = os.path.join(
                                    self.saves_path,
                                    pc_name_or_file_name + ".xml",
                                )
                                self.game_state.archive_saved_game_file(saved_game_file, "deleted")
                            elif menu_result != "NO":
                                continue
                        break
                    dm.remove_cascading_dialog(False)
                elif menu_result is not None and menu_result.startswith("Combat Mode:"):
                    self.game_state.toggle_should_add_math_problems_in_combat()

        # Load the saved game
        if self.game_state.is_running:
            self.game_state.load(pc_name_or_file_name)

    def draw_background(self, flip_buffer: bool = False) -> None:
        """Draw the background for the main menu, which is the same as the background for the loading screen."""
        loading_screen = LoadingScreen(GameInfo.title_image, GameInfo.title_music)
        loading_screen.set_background_text(self.background_text)
        loading_screen.draw(flip_buffer)
