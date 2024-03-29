#!/usr/bin/env python

from typing import cast, Optional, List, Tuple, Union

import random
import time

import pygame

from generic_utils.point import Point

from pygame_utils.audio_player import AudioPlayer
import pygame_utils.game_events as GameEvents
import pygame_utils.surface_effects as SurfaceEffects

from pydw.combat_character_state import CombatCharacterState
from pydw.combat_encounter_interface import CombatEncounterInterface
from pydw.game_dialog import GameDialog, GameDialogSpacing
from pydw.game_types import (
    ActionCategoryTypeEnum,
    DialogAction,
    DialogActionEnum,
    DialogCheck,
    DialogCheckEnum,
    DialogGoTo,
    DialogType,
    DialogVariable,
    DialogVendorBuyOptions,
    DialogVendorBuyOptionsVariable,
    DialogVendorSellOptions,
    DialogVendorSellOptionsVariable,
    Direction,
    GameTypes,
    Level,
)
from pydw.game_info import GameInfo
from pydw.game_state_interface import GameStateInterface
from pydw.hero_state import HeroState
from pydw.map_character_state import MapCharacterState
from pydw.monster_state import MonsterState


class GameDialogEvaluator:
    def __init__(
        self,
        game_info: GameInfo,
        game_state: GameStateInterface,
        combat_encounter: Optional[CombatEncounterInterface] = None,
    ) -> None:
        self.game_info = game_info
        self.game_state = game_state
        self.combat_encounter = combat_encounter
        self.wait_before_new_text = False

        self.refresh_game_state()

    def refresh_game_state(self) -> None:
        self.hero_party = self.game_state.get_hero_party()
        self.replacement_variables = self.game_state.get_dialog_replacement_variables()
        self.actor: CombatCharacterState = self.hero_party.main_character
        self.targets: List[CombatCharacterState] = cast(
            List[CombatCharacterState], self.hero_party.members
        )

    # Set the actor - the character performing the action
    # The actor may be called out in the dialog associated with the action
    def set_actor(self, actor: CombatCharacterState) -> None:
        self.actor = actor
        self.replacement_variables.generic["[ACTOR]"] = actor.get_name()

    # Set the targets - the character(s) on which actions will be performed
    # When the target is singular, it may be called out in the dialog associated with the action
    def set_targets(self, targets: List[CombatCharacterState]) -> None:
        self.targets = targets
        self.replacement_variables.generic["[TARGET]"] = ""
        if 1 == len(targets):
            if targets[0] in self.game_state.get_hero_party().combat_members:
                if 1 != len(self.game_state.get_hero_party().combat_members):
                    self.replacement_variables.generic["[TARGET]"] = targets[
                        0
                    ].get_name()
            elif self.combat_encounter is not None and 1 != len(
                self.combat_encounter.get_monsters_still_in_combat()
            ):
                self.replacement_variables.generic["[TARGET]"] = targets[0].get_name()

    def restore_default_actor_and_targets(self) -> None:
        self.set_actor(self.hero_party.main_character)
        self.set_targets(cast(List[CombatCharacterState], self.hero_party.members))

    def set_combat_encounter(self, combat_encounter: CombatEncounterInterface) -> None:
        self.combat_encounter = combat_encounter

    def dialog_loop(
        self, dialog: Union[DialogType, str], npc: Optional[MapCharacterState] = None
    ) -> None:
        # Save off initial background image
        background_image = self.game_state.screen.copy()

        # Clear event queue
        GameEvents.clear_events()

        # Create the status and message dialogs
        GameDialog.create_exploring_status_dialog(self.hero_party).blit(
            self.game_state.screen, False
        )
        message_dialog = GameDialog.create_message_dialog()

        self.traverse_dialog(message_dialog, dialog, npc=npc)

        if self.game_state.is_running:
            # Restore initial background image
            self.game_state.screen.blit(background_image, (0, 0))

            # Call game_state.draw_map but manually flip the buffer for the case where this method is a mock
            self.game_state.draw_map(False)
            pygame.display.flip()

    def add_and_wait_for_message(
        self, message: str, message_dialog: GameDialog
    ) -> None:
        message_dialog.add_message(message)
        self.wait_for_message_to_fully_display(message_dialog)

    def wait_for_message_to_fully_display(self, message_dialog: GameDialog) -> None:
        message_dialog.blit(self.game_state.screen, True)
        clock = pygame.time.Clock()
        while self.game_state.is_running and message_dialog.has_more_content():
            (
                should_wait_for_acknowledgement,
                is_new_content_part_of_quotation,
            ) = message_dialog.advance_content()
            if is_new_content_part_of_quotation:
                AudioPlayer().play_sound("talking")
            if should_wait_for_acknowledgement:
                self.wait_for_acknowledgement(message_dialog)
            message_dialog.blit(self.game_state.screen)
            clock.tick(30)
            pygame.display.flip()

    def wait_for_acknowledgement(
        self, message_dialog: Optional[GameDialog] = None
    ) -> None:
        # Skip waiting for acknowledgement of message dialog if the content
        # was already acknowledged.
        if not self.game_state.is_running or (
            message_dialog is not None and message_dialog.is_acknowledged()
        ):
            return

        # Clear event queue
        GameEvents.clear_events()

        # AudioPlayer().play_sound('prompt')

        is_awaiting_acknowledgement = True
        is_waiting_indicator_drawn = False
        clock = pygame.time.Clock()
        while self.game_state.is_running and is_awaiting_acknowledgement:
            # Process events
            events = GameEvents.get_events()
            if 0 == len(events):
                if message_dialog is not None:
                    if is_waiting_indicator_drawn:
                        message_dialog.erase_waiting_indicator()
                    else:
                        message_dialog.draw_waiting_indicator()
                    is_waiting_indicator_drawn = not is_waiting_indicator_drawn
                    message_dialog.blit(self.game_state.screen)
                clock.tick(8)
                pygame.display.flip()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.handle_quit()
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        is_awaiting_acknowledgement = False
                elif event.type == pygame.QUIT:
                    self.game_state.handle_quit(force=True)

        if self.game_state.is_running:
            AudioPlayer().play_sound("select")

            if message_dialog is not None:
                message_dialog.acknowledge()
                if is_waiting_indicator_drawn:
                    message_dialog.erase_waiting_indicator()
                    message_dialog.blit(self.game_state.screen, True)

        # Since we just waited, clean wait_before_new_text
        self.wait_before_new_text = False

    def wait_for_user_input(
        self,
        message_dialog: GameDialog,
        prompt: str,
        allowed_input: Optional[str] = None,
    ) -> Tuple[str, float]:
        message_dialog.prompt_for_user_text(prompt, allowed_input)
        self.wait_for_message_to_fully_display(message_dialog)

        # AudioPlayer().play_sound('prompt')

        is_waiting_for_user_input = True
        start_time = time.time()
        while self.game_state.is_running and is_waiting_for_user_input:
            # Process events
            events = GameEvents.get_events(
                True, translate_e_to_enter=GameDialog.use_menus_for_text_entry()
            )
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.handle_quit()
                    elif event.key == pygame.K_RETURN:
                        if GameDialog.use_menus_for_text_entry():
                            # Get a menu selection and turn that into an event
                            menu_result = message_dialog.get_selected_menu_option()
                            if menu_result == GameDialog.ENTER_UNICODE:
                                is_waiting_for_user_input = False
                            elif menu_result == GameDialog.BACKSPACE_UNICODE:
                                event = pygame.event.Event(
                                    pygame.KEYDOWN, {"key": pygame.K_BACKSPACE}
                                )
                            else:
                                event = pygame.event.Event(
                                    pygame.KEYDOWN,
                                    {"key": None, "unicode": menu_result},
                                )

                            if is_waiting_for_user_input:
                                message_dialog.process_event(
                                    event, self.game_state.screen
                                )
                        else:
                            is_waiting_for_user_input = False
                    else:
                        message_dialog.process_event(event, self.game_state.screen)
                elif event.type == pygame.QUIT:
                    self.game_state.handle_quit(force=True)

            if 0 == len(events):
                pygame.time.wait(25)
            else:
                pygame.time.wait(100)

        stop_time = time.time()

        # if self.game_state.is_running:
        #    AudioPlayer().play_sound('select')

        return message_dialog.get_user_text(), stop_time - start_time

    def get_menu_result(
        self, menu_dialog: GameDialog, allow_quit: bool = True
    ) -> Optional[str]:
        # AudioPlayer().play_sound('prompt')

        menu_result = None
        while self.game_state.is_running and menu_result is None:
            events = GameEvents.get_events(True)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if allow_quit:
                            self.game_state.handle_quit()
                        else:
                            menu_result = ""
                    elif event.key == pygame.K_RETURN:
                        menu_result = menu_dialog.get_selected_menu_option()
                    elif event.key == pygame.K_SPACE:
                        menu_result = ""
                    else:
                        menu_dialog.process_event(event, self.game_state.screen)
                elif event.type == pygame.QUIT:
                    self.game_state.handle_quit(force=True)

            if 0 == len(events):
                pygame.time.wait(25)
            else:
                pygame.time.wait(200)

        if menu_result == "":
            menu_result = None

        if menu_result is not None:
            AudioPlayer().play_sound("select")

        return menu_result

    def update_default_dialog_font_color(self) -> None:
        old_default = GameDialog.default_font_color
        if self.hero_party.has_low_health():
            new_default = GameDialog.LOW_HEALTH_FONT_COLOR
        else:
            new_default = GameDialog.NOMINAL_HEALTH_FONT_COLOR
        if old_default != new_default:
            GameDialog.set_default_font_color(new_default)

    def update_status_dialog(
        self, flip_buffer: bool = False, message_dialog: Optional[GameDialog] = None
    ) -> None:
        old_default = GameDialog.get_default_font_color()
        self.update_default_dialog_font_color()
        new_default = GameDialog.get_default_font_color()
        if old_default != new_default:
            self.game_state.draw_map(flip_buffer=False)
            if message_dialog is not None:
                message_dialog.set_font_color(new_default)
                message_dialog.blit(self.game_state.screen, flip_buffer=False)

        if self.game_state.is_in_combat():
            GameDialog.create_encounter_status_dialog(self.hero_party).blit(
                self.game_state.screen, flip_buffer
            )
        else:
            GameDialog.create_exploring_status_dialog(self.hero_party).blit(
                self.game_state.screen, flip_buffer
            )

    def traverse_dialog(
        self,
        message_dialog: GameDialog,
        dialog: Union[DialogType, str],
        depth: int = 0,
        add_spacing: bool = True,
        npc: Optional[MapCharacterState] = None,
    ) -> None:
        def add_message(messages: Union[str, List[str]]) -> None:
            if isinstance(messages, str):
                self.add_and_wait_for_message(messages, message_dialog)
            else:
                for message in messages:
                    self.add_and_wait_for_message(message, message_dialog)

        if depth == 0:
            self.wait_before_new_text = False
            # print('Initialized self.traverse_dialog_wait_before_new_text to False', flush=True)
            self.replacement_variables = (
                self.game_state.get_dialog_replacement_variables()
            )
            self.replacement_variables.generic["[NAME]"] = (
                self.hero_party.main_character.get_name()
            )
            self.replacement_variables.generic["[ACTOR]"] = self.actor.get_name()
            if 1 == len(self.targets):
                self.replacement_variables.generic["[TARGET]"] = self.targets[
                    0
                ].get_name()
            elif "[TARGET]" in self.replacement_variables.generic:
                del self.replacement_variables.generic["[TARGET]"]

        # Ensure dialog is a list and not a str to allow iteration
        if isinstance(dialog, str):
            temp = dialog
            dialog = [temp]

        for item in dialog:
            # print('item =', item, flush=True)
            if isinstance(item, str):
                # print('Dialog Text =', item, flush=True)
                # Wait for user to acknowledge that the message is read
                # before iterating to display the next part of the message
                # or exiting out of the loop when the full message has been
                # displayed.
                if self.wait_before_new_text:
                    # print('Waiting because self.traverse_dialog_wait_before_new_text is True', flush=True)
                    self.wait_for_acknowledgement(message_dialog)
                # else:
                #   print('Not waiting because self.traverse_dialog_wait_before_new_text is False', flush=True)

                # Perform variable replacement
                # If a replacement is made, perform capitalization fixing to ensure that any replacement variables
                # at the start of a sentence are appropriately capitalized.
                orig_item = item
                for variable in self.replacement_variables.generic:
                    item = item.replace(
                        variable, str(self.replacement_variables.generic[variable])
                    )
                if orig_item != item:
                    item = GameDialog.fix_capitalization(item)

                if add_spacing and not message_dialog.is_last_row_blank():
                    add_message("")
                add_message(item)

                self.wait_before_new_text = True
                # print('Set self.traverse_dialog_wait_before_new_text to True', flush=True)

            elif isinstance(item, list):
                # print( 'Dialog Sub Tree =', item, flush=True )
                if self.game_state.is_running:
                    self.traverse_dialog(message_dialog, item, depth + 1, npc=npc)

            elif isinstance(item, DialogGoTo):
                # print( 'Dialog Go To =', item, flush=True )
                if item.label in self.game_info.dialog_sequences:
                    if self.game_state.is_running:
                        self.traverse_dialog(
                            message_dialog,
                            self.game_info.dialog_sequences[item.label],
                            depth + 1,
                            npc=npc,
                        )
                else:
                    print(
                        "ERROR: " + item.label + " not found in dialogSequences",
                        flush=True,
                    )

            elif isinstance(item, DialogVariable):
                # print( 'Dialog Variable =', item, flush=True )
                self.replacement_variables.generic[item.name] = item.evaluate()

            elif isinstance(item, DialogVendorBuyOptionsVariable):
                # print('Dialog Vendor Buy Options Variable =', item, flush=True)
                self.replacement_variables.vendor_buy_options[item.name] = item.value

            elif isinstance(item, DialogVendorSellOptionsVariable):
                # print('Dialog Vendor Sell Options Variable =', item, flush=True)
                self.replacement_variables.vendor_sell_options[item.name] = item.value

            elif isinstance(item, dict):
                # print('Dialog Option =', item, flush=True)
                self.wait_before_new_text = False
                # print('Set self.traverse_dialog_wait_before_new_text to False', flush=True)
                options = list(item.keys())
                message_dialog.add_menu_prompt(
                    options, len(options), GameDialogSpacing.SPACERS
                )
                message_dialog.blit(self.game_state.screen, True)
                menu_result = None
                while self.game_state.is_running and menu_result is None:
                    menu_result = self.get_menu_result(message_dialog)
                if self.game_state.is_running and menu_result is not None:
                    # print('menu_result =', menu_result, flush=True)
                    # The user just made a dialog choice which is also an implicit acknowledgment
                    message_dialog.acknowledge()
                    if item[menu_result]:
                        self.traverse_dialog(
                            message_dialog, item[menu_result], depth + 1, npc=npc
                        )

            elif isinstance(item, DialogVendorBuyOptions):
                # print('Dialog Vendor Buy Options =', item, flush=True)
                if (
                    isinstance(item.name_and_gp_row_data, str)
                    and item.name_and_gp_row_data
                    in self.replacement_variables.vendor_buy_options
                ):
                    name_and_gp_row_data = (
                        self.replacement_variables.vendor_buy_options[
                            item.name_and_gp_row_data
                        ]
                    )
                elif not isinstance(item.name_and_gp_row_data, str):
                    name_and_gp_row_data = item.name_and_gp_row_data
                else:
                    name_and_gp_row_data = []
                if len(name_and_gp_row_data) == 0:
                    print("ERROR: No options from vendor", flush=True)
                    self.traverse_dialog(
                        message_dialog,
                        "Nature calls and I need to run.  Sorry!",
                        depth + 1,
                        npc=npc,
                    )
                    break
                self.wait_before_new_text = False
                # print('Set self.traverse_dialog_wait_before_new_text to False', flush=True)
                message_dialog.add_menu_prompt(
                    name_and_gp_row_data, 2, GameDialogSpacing.OUTSIDE_JUSTIFIED
                )
                message_dialog.blit(self.game_state.screen, True)
                menu_result = self.get_menu_result(message_dialog)
                if menu_result is not None:
                    # print('menu_result =', menu_result, flush=True)
                    self.replacement_variables.generic["[ITEM]"] = menu_result
                    for item_name_and_gp in name_and_gp_row_data:
                        if item_name_and_gp[0] == menu_result:
                            self.replacement_variables.generic["[COST]"] = (
                                item_name_and_gp[1]
                            )
                else:
                    self.replacement_variables.generic.pop("[ITEM]", None)
                    self.replacement_variables.generic.pop("[COST]", None)

            elif isinstance(item, DialogVendorSellOptions):
                # print( 'Dialog Vendor Sell Options =', item, flush=True )
                if (
                    isinstance(item.item_types, str)
                    and item.item_types
                    in self.replacement_variables.vendor_sell_options
                ):
                    item_types = self.replacement_variables.vendor_sell_options[
                        item.item_types
                    ]
                elif not isinstance(item.item_types, str):
                    item_types = item.item_types
                else:
                    item_types = []
                item_row_data = self.hero_party.get_item_row_data(True, item_types)
                if len(item_row_data) == 0:
                    self.traverse_dialog(
                        message_dialog,
                        "Thou dost not have any items to sell.",
                        depth + 1,
                        npc=npc,
                    )
                    self.replacement_variables.generic.pop("[ITEM]", None)
                    self.replacement_variables.generic.pop("[COST]", None)
                    continue
                self.wait_before_new_text = False
                # print( 'Set self.traverse_dialog_wait_before_new_text to False', flush=True )
                message_dialog.add_menu_prompt(
                    item_row_data, 2, GameDialogSpacing.OUTSIDE_JUSTIFIED
                )
                message_dialog.blit(self.game_state.screen, True)
                menu_result = self.get_menu_result(message_dialog)
                if menu_result is not None:
                    # print( 'menu_result =', menu_result, flush=True )
                    menu_result_item = self.game_info.get_item(menu_result)
                    if menu_result_item is not None:
                        self.replacement_variables.generic["[ITEM]"] = menu_result
                        self.replacement_variables.generic["[COST]"] = str(
                            menu_result_item.gp // 2
                        )
                    else:
                        print(
                            "ERROR: Failed to find item for menu_result =",
                            menu_result,
                            flush=True,
                        )
                        self.replacement_variables.generic.pop("[ITEM]", None)
                        self.replacement_variables.generic.pop("[COST]", None)
                else:
                    self.replacement_variables.generic.pop("[ITEM]", None)
                    self.replacement_variables.generic.pop("[COST]", None)

            elif isinstance(item, DialogCheck):
                # print( 'Dialog Check =', item, flush=True )

                check_result = True

                if item.type in (DialogCheckEnum.HAS_ITEM, DialogCheckEnum.LACKS_ITEM):
                    # Perform variable replacement
                    item_name = str(item.name)
                    item_count = 1
                    for variable in self.replacement_variables.generic:
                        if isinstance(item_name, str):
                            item_name = item_name.replace(
                                variable, self.replacement_variables.generic[variable]
                            )
                        if isinstance(item.count, str) and -1 != item.count.find(
                            variable
                        ):
                            try:
                                item_count = int(
                                    item.count.replace(
                                        variable,
                                        self.replacement_variables.generic[variable],
                                    )
                                )
                            except ValueError:
                                print(
                                    "ERROR: Failed to convert item_count to int:",
                                    item.count,
                                    flush=True,
                                )

                    if item_name == "gp":
                        check_value = self.hero_party.gp
                    elif item_name == "lv":
                        # Check against the level of the main character
                        check_value = self.hero_party.main_character.level.number
                    else:
                        # Check against the cumulative count for the party
                        check_value = self.hero_party.get_item_count(item_name)

                    # print( 'check_value =', check_value, flush=True )
                    # print( 'item_name =', item_name, flush=True )
                    # print( 'item_count =', item_count, flush=True )
                    check_result = check_value >= item_count
                    if item.type == DialogCheckEnum.LACKS_ITEM:
                        check_result = not check_result

                elif item.type == DialogCheckEnum.IS_FACING_LOCKED_ITEM:
                    check_result = self.game_state.is_facing_locked_item()

                elif item.type == DialogCheckEnum.IS_OUTSIDE:
                    check_result = self.game_state.is_outside()

                elif item.type == DialogCheckEnum.IS_INSIDE:
                    check_result = not self.game_state.is_outside()

                elif item.type == DialogCheckEnum.IS_DARK:
                    check_result = self.game_state.is_light_restricted()

                elif item.type == DialogCheckEnum.IS_AT_COORDINATES:
                    check_result = item.map_name == self.game_state.get_map_name() and (
                        item.map_pos is None
                        or item.map_pos == self.hero_party.get_curr_pos_dat_tile()
                    )

                elif item.type == DialogCheckEnum.IS_IN_COMBAT:
                    check_result = self.game_state.is_in_combat()

                elif item.type == DialogCheckEnum.IS_NOT_IN_COMBAT:
                    check_result = not self.game_state.is_in_combat()

                elif item.type == DialogCheckEnum.IS_COMBAT_ALLOWED:
                    check_result = self.game_state.is_combat_allowed()

                elif item.type == DialogCheckEnum.IS_COMBAT_DISALLOWED:
                    check_result = not self.game_state.is_combat_allowed()

                elif item.type == DialogCheckEnum.IS_TARGET_HERO:
                    check_result = len(self.targets) > 0 and isinstance(
                        self.targets[0], HeroState
                    )

                elif item.type == DialogCheckEnum.IS_TARGET_MONSTER:
                    check_result = (
                        len(self.targets) > 0
                        and isinstance(self.targets[0], MonsterState)
                        and (
                            item.name is None
                            or item.name == self.targets[0].get_type_name()
                        )
                    )

                elif item.type in (
                    DialogCheckEnum.IS_DEFINED,
                    DialogCheckEnum.IS_NOT_DEFINED,
                ):
                    # Perform variable replacement
                    item_name = str(item.name)
                    for variable in self.replacement_variables.generic:
                        if isinstance(item_name, str):
                            item_name = item_name.replace(
                                variable, self.replacement_variables.generic[variable]
                            )

                    check_result = item_name != item.name
                    if item.type == DialogCheckEnum.IS_NOT_DEFINED:
                        check_result = not check_result

                else:
                    print(
                        "ERROR: Unsupported DialogCheckEnum of", item.type, flush=True
                    )

                # On an assert, evaluate the dialog on a failure and then break out.
                if item.is_assert and not check_result:
                    if item.dialog is not None:
                        self.traverse_dialog(
                            message_dialog, item.dialog, depth + 1, npc=npc
                        )
                    break
                # On a check, evaluate the dialog on a success and do NOT break out.
                elif not item.is_assert and check_result and item.dialog is not None:
                    self.traverse_dialog(
                        message_dialog, item.dialog, depth + 1, npc=npc
                    )

            elif isinstance(item, DialogAction):
                # print( 'Dialog Action =', item, flush=True )

                self.wait_before_new_text = False
                # print( 'Set self.traverse_dialog_wait_before_new_text to False', flush=True )

                if (
                    ActionCategoryTypeEnum.MAGICAL == item.category
                    and self.game_state.is_in_combat()
                    and self.actor.are_spells_blocked
                ):
                    add_message("But that spell hath been blocked.")
                    continue

                if item.type == DialogActionEnum.SAVE_GAME:
                    self.game_state.save()

                elif item.type in (
                    DialogActionEnum.GAIN_ITEM,
                    DialogActionEnum.LOSE_ITEM,
                ):
                    # Perform variable replacement
                    item_name = str(item.name)
                    item_count = 1
                    for variable in self.replacement_variables.generic:
                        item_name = item_name.replace(
                            variable, self.replacement_variables.generic[variable]
                        )
                        if isinstance(item.count, str) and -1 != item.count.find(
                            variable
                        ):
                            try:
                                item_count = int(
                                    item.count.replace(
                                        variable,
                                        self.replacement_variables.generic[variable],
                                    )
                                )
                            except ValueError:
                                print(
                                    "ERROR: Failed to convert item.count to int so defaulting to 1:",
                                    item.count,
                                    flush=True,
                                )

                    if item_name == "hp":
                        for hero in self.hero_party.members:
                            if item.type == DialogActionEnum.GAIN_ITEM:
                                hero.hp = min(hero.hp + item_count, hero.max_hp)
                            elif item.type == DialogActionEnum.LOSE_ITEM:
                                if item.count == "unlimited":
                                    hero.hp = 0
                                else:
                                    hero.hp -= item_count
                                hero.hp = max(hero.hp, 0)
                        self.update_status_dialog(
                            flip_buffer=not item.bypass, message_dialog=message_dialog
                        )
                    elif item_name == "gp":
                        if item.type == DialogActionEnum.GAIN_ITEM:
                            self.hero_party.gp += item_count
                        elif item.type == DialogActionEnum.LOSE_ITEM:
                            if item.count == "unlimited":
                                self.hero_party.gp = 0
                            else:
                                self.hero_party.gp -= item_count
                            self.hero_party.gp = max(self.hero_party.gp, 0)
                        self.update_status_dialog(
                            flip_buffer=not item.bypass, message_dialog=message_dialog
                        )
                    elif item_name == "mp":
                        for hero in self.hero_party.members:
                            if item.type == DialogActionEnum.GAIN_ITEM:
                                hero.mp = min(hero.mp + item_count, hero.max_mp)
                            elif item.type == DialogActionEnum.LOSE_ITEM:
                                if item.count == "unlimited":
                                    hero.mp = 0
                                else:
                                    hero.mp -= item_count
                                hero.mp = max(hero.mp, 0)
                        self.update_status_dialog(
                            flip_buffer=not item.bypass, message_dialog=message_dialog
                        )
                    elif item_name == "xp":
                        for hero in self.hero_party.members:
                            if item.type == DialogActionEnum.GAIN_ITEM:
                                hero.xp += item_count
                                hero.level_up_check()
                            elif item.type == DialogActionEnum.LOSE_ITEM:
                                if item.count == "unlimited":
                                    hero.xp = 0
                                else:
                                    hero.xp -= item_count
                                hero.xp = max(hero.xp, 0)
                        self.update_status_dialog(
                            flip_buffer=not item.bypass, message_dialog=message_dialog
                        )
                    elif item.type == DialogActionEnum.GAIN_ITEM:
                        item_to_gain = self.game_info.get_item(item_name)
                        if item_to_gain is not None:
                            self.hero_party.gain_item(item_to_gain, item_count)
                        else:
                            self.hero_party.gain_progress_marker(item_name)
                    elif item.type == DialogActionEnum.LOSE_ITEM:
                        item_to_lose = self.game_info.get_item(item_name)
                        if item_to_lose is not None:
                            self.hero_party.lose_item(item_name, item_count)
                        else:
                            self.hero_party.lose_progress_marker(item_name)

                elif item.type == DialogActionEnum.SET_LIGHT_DIAMETER:
                    if isinstance(item.count, int):
                        self.hero_party.light_diameter = item.count
                        self.hero_party.light_diameter_decay_steps = item.decay_steps
                        self.hero_party.light_diameter_decay_steps_remaining = (
                            item.decay_steps
                        )
                    else:
                        self.hero_party.light_diameter = None
                    self.game_state.draw_map()

                elif item.type == DialogActionEnum.REPEL_MONSTERS:
                    self.hero_party.repel_monsters = True
                    self.hero_party.repel_monsters_decay_steps_remaining = (
                        item.decay_steps
                    )
                    self.hero_party.repel_monster_fade_dialog = item.fade_dialog

                elif item.type == DialogActionEnum.GOTO_COORDINATES:
                    for hero in self.hero_party.members:
                        hero.curr_pos_offset_img_px = Point(0, 0)
                        if item.map_pos is not None:
                            hero.curr_pos_dat_tile = hero.dest_pos_dat_tile = (
                                item.map_pos
                            )
                        if item.map_dir is not None:
                            hero.direction = item.map_dir
                    if item.map_name is not None:
                        self.game_state.set_map(item.map_name)
                    else:
                        self.game_state.set_map(self.game_state.get_map_name())
                    self.game_state.draw_map(
                        flip_buffer=message_dialog.is_empty(), draw_combat=False
                    )
                    if not message_dialog.is_empty():
                        message_dialog.blit(self.game_state.screen, True)

                elif item.type == DialogActionEnum.GOTO_LAST_OUTSIDE_COORDINATES:
                    if self.hero_party.last_outside_map_name in self.game_info.maps:
                        self.hero_party.set_pos(
                            self.hero_party.last_outside_pos_dat_tile,
                            Direction.get_opposite(self.hero_party.last_outside_dir),
                        )
                        self.game_state.set_map(self.hero_party.last_outside_map_name)
                        self.game_state.draw_map(
                            flip_buffer=message_dialog.is_empty(), draw_combat=False
                        )
                    else:
                        add_message("But it did not work.")

                elif item.type == DialogActionEnum.PLAY_SOUND:
                    # print( 'Play sound', item.name, flush=True )
                    if isinstance(item.name, str):
                        AudioPlayer().play_sound(item.name)

                elif item.type == DialogActionEnum.PLAY_MUSIC:
                    # print( 'Play music', item.name, flush=True )
                    if isinstance(item.name, str):
                        AudioPlayer().play_music(item.name, interrupt=True)

                elif item.type == DialogActionEnum.VISUAL_EFFECT:
                    # Update the screen but don't flip the buffers
                    self.game_state.draw_map(flip_buffer=False)
                    if self.combat_encounter is not None:
                        self.combat_encounter.render_monsters()
                    message_dialog.blit(self.game_state.screen, flip_buffer=False)
                    self.update_status_dialog(
                        flip_buffer=False, message_dialog=message_dialog
                    )

                    # TODO: Can this be done via reflection?
                    if item.name == "fadeToBlackAndBack":
                        SurfaceEffects.fade_to_black_and_back(self.game_state.screen)
                    elif item.name == "fadeOutToBlack":
                        SurfaceEffects.fade_out_to_black(self.game_state.screen)
                    elif item.name == "fadeInFromBlack":
                        SurfaceEffects.fade_in_from_black(self.game_state.screen)
                    elif item.name == "flickering":
                        SurfaceEffects.flickering(self.game_state.screen)
                    elif item.name == "rainbowEffect":
                        SurfaceEffects.rainbow_effect(self.game_state, message_dialog)

                    elif item.name == "hideDialog":
                        # Before hiding the dialog first ensure the contents are acknowledged then clear them
                        self.wait_for_acknowledgement(message_dialog)
                        message_dialog.clear()
                        self.game_state.draw_map(flip_buffer=True)
                    elif item.name == "evilDeathLoop":
                        SurfaceEffects.black_red_monochrome_effect(
                            self.game_state.screen, flip_buffer=False
                        )
                        self.game_state.draw_map(draw_only_character_sprites=True)

                        # Endless loop where quiting is the only exit
                        while self.game_state.is_running:
                            # Process events
                            events = GameEvents.get_events()
                            if 0 == len(events):
                                pygame.time.wait(25)
                            for event in events:
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        self.game_state.handle_quit()
                                elif event.type == pygame.QUIT:
                                    self.game_state.handle_quit(force=True)

                    else:
                        print(
                            "ERROR: DialogActionEnum.VISUAL_EFFECT is not implemented for effect",
                            item.name,
                            flush=True,
                        )

                elif item.type == DialogActionEnum.START_ENCOUNTER:
                    monster_name = item.name
                    if monster_name is not None:
                        monster_name = random.choice(monster_name.split("|"))
                    if monster_name not in self.game_info.monsters:
                        print(
                            "ERROR: No defined monster with name",
                            monster_name,
                            flush=True,
                        )
                    else:
                        # Before initiating the combat encounter ensure the contents of the dialog are acknowledged
                        self.wait_for_acknowledgement(message_dialog)

                        self.game_state.initiate_encounter(
                            monster_info=self.game_info.monsters[monster_name],
                            approach_dialog=item.approach_dialog,
                            victory_dialog=item.victory_dialog,
                            run_away_dialog=item.run_away_dialog,
                            encounter_music=item.encounter_music,
                            message_dialog=message_dialog,
                        )

                elif item.type == DialogActionEnum.OPEN_LOCKED_ITEM:
                    removed_map_decoration = self.game_state.open_locked_item()
                    self.game_state.draw_map(flip_buffer=message_dialog.is_empty())
                    if not message_dialog.is_empty():
                        message_dialog.blit(self.game_state.screen, True)
                    if (
                        removed_map_decoration is not None
                        and removed_map_decoration.dialog is not None
                    ):
                        self.traverse_dialog(
                            message_dialog,
                            removed_map_decoration.dialog,
                            depth + 1,
                            npc=npc,
                        )

                elif item.type == DialogActionEnum.MAGIC_RESTORE:
                    worked = False
                    for target in self.targets:
                        if self.actor.does_action_work(
                            item.type, item.category, target, item.bypass, item.name
                        ):
                            if item.count == "unlimited":
                                target.mp = target.max_mp
                            else:
                                target.mp = min(
                                    target.max_mp,
                                    target.mp + GameTypes.get_int_value(item.count),
                                )
                            worked = True
                    if not item.bypass and not worked:
                        if ActionCategoryTypeEnum.MAGICAL == item.category:
                            add_message("But that spell did not work.")
                        else:
                            add_message("But it did nothing.")
                    else:
                        self.update_status_dialog(
                            flip_buffer=not item.bypass, message_dialog=message_dialog
                        )

                elif item.type == DialogActionEnum.HEALTH_RESTORE:
                    worked = False
                    for target in self.targets:
                        if self.actor.does_action_work(
                            item.type, item.category, target, item.bypass, item.name
                        ):
                            if item.count == "unlimited":
                                target.hp = target.max_hp
                            else:
                                target.hp = min(
                                    target.max_hp,
                                    target.hp + GameTypes.get_int_value(item.count),
                                )
                            worked = True
                            if not item.bypass:
                                add_message(target.get_name() + " hath recovered.")
                    if not item.bypass and not worked:
                        if ActionCategoryTypeEnum.MAGICAL == item.category:
                            add_message("But that spell did not work.")
                        else:
                            add_message("But it did nothing.")
                    else:
                        self.update_status_dialog(
                            flip_buffer=not item.bypass, message_dialog=message_dialog
                        )

                elif item.type == DialogActionEnum.SLEEP:
                    worked = False
                    for target in self.targets:
                        if self.actor.does_action_work(
                            item.type, item.category, target, item.bypass, item.name
                        ):
                            target.is_asleep = True
                            worked = True
                            add_message(target.get_name() + " is asleep.")
                    if not worked:
                        if ActionCategoryTypeEnum.MAGICAL == item.category:
                            add_message("But that spell did not work.")
                        else:
                            add_message("But it did nothing.")

                elif item.type == DialogActionEnum.STOPSPELL:
                    worked = False
                    for target in self.targets:
                        if self.actor.does_action_work(
                            item.type, item.category, target, item.bypass, item.name
                        ):
                            target.are_spells_blocked = True
                            worked = True
                            add_message(target.get_name() + "'s spells are blocked.")
                    if not worked:
                        if ActionCategoryTypeEnum.MAGICAL == item.category:
                            add_message("But that spell did not work.")
                        else:
                            add_message("But it did nothing.")

                elif item.type == DialogActionEnum.DAMAGE_TARGET:
                    worked = False
                    damaged_targets = []

                    if item.problem is not None:
                        # Prompt user for problem and get their answer
                        user_answer, seconds_waiting = self.wait_for_user_input(
                            message_dialog,
                            item.problem.problem,
                            item.problem.answer_allowed_characters,
                        )
                        # print('User answer to problem', item.problem.problem, 'was', user_answer, 'in',
                        #      round(seconds_waiting, 2), 'seconds; expected answer', item.problem.answer, flush=True)

                    for target in self.targets:
                        if self.actor.does_action_work(
                            item.type, item.category, target, item.bypass, item.name
                        ):
                            worked = True
                            is_critical_hit = None
                            if item.problem is not None:
                                if user_answer == item.problem.answer:
                                    # TODO: Make 5 second time threshold configurable
                                    is_critical_hit = seconds_waiting < 5.0
                                else:
                                    add_message(
                                        "Wrong!  The correct answer is "
                                        + str(item.problem.answer)
                                    )

                            if item.count != "default":
                                if is_critical_hit is None:
                                    is_critical_hit = False

                                damage = round(
                                    GameTypes.get_int_value(item.count)
                                    * target.get_damage_modifier(item.category)
                                )
                                # print('Using item damage', flush=True)
                            else:
                                # If is_critical_hit is None, then this method determines is_critical_hit.
                                # Else it respects the value of is_critical_hit which is provided.
                                (
                                    damage,
                                    is_critical_hit,
                                ) = self.actor.get_attack_damage(
                                    target, item.category, is_critical_hit
                                )
                                # print('Using self.actor.get_attack_damage(...) damage', flush=True)

                            if is_critical_hit:
                                if damage > 64:
                                    AudioPlayer().play_sound("critical_hit_lvl_2")
                                else:
                                    AudioPlayer().play_sound("critical_hit_lvl_1")

                            # Ensure there is damage if the user was correct and no damage if the user was wrong
                            if item.problem is not None:
                                if user_answer == item.problem.answer:
                                    damage = max(1, damage)
                                    allow_dodge = False
                                    if is_critical_hit:
                                        if target.allows_critical_hits():
                                            add_message("That's right! Excellent move!")
                                        else:
                                            add_message(
                                                "That's right! Excellent move!!!"
                                            )
                                    else:
                                        add_message("That's right!")
                                else:
                                    damage = 0
                            else:
                                allow_dodge = (
                                    ActionCategoryTypeEnum.PHYSICAL == item.category
                                )
                                if is_critical_hit:
                                    add_message("Excellent move!")

                            if 0 < damage:
                                # Check for a dodge
                                if allow_dodge and target.is_dodging_attack():
                                    AudioPlayer().play_sound("attack_miss_lvl1")
                                    add_message(
                                        f"{target.get_name()} dodges {self.actor.get_name()}'s strike."
                                    )
                                else:
                                    if damage > 32:
                                        AudioPlayer().play_sound("hit_lvl_4")
                                    elif damage > 16:
                                        AudioPlayer().play_sound("hit_lvl_3")
                                    elif damage > 8:
                                        AudioPlayer().play_sound("hit_lvl_2")
                                    else:
                                        AudioPlayer().play_sound("hit_lvl_1")

                                    damaged_targets.append(target)

                                    target.hp = max(0, target.hp - damage)
                                    if target == self.hero_party.main_character:
                                        add_message(
                                            f"Thy hit points reduced by {damage}."
                                        )
                                    else:
                                        add_message(
                                            f"{target.get_name()}'s hit points reduced by {damage}."
                                        )
                            else:
                                AudioPlayer().play_sound("attack_miss_lvl2")
                                if isinstance(target, HeroState):
                                    add_message(
                                        target.get_name() + " dodges the strike."
                                    )
                                else:
                                    add_message("A miss! No damage hath been scored!")
                    if not worked:
                        if ActionCategoryTypeEnum.MAGICAL == item.category:
                            add_message("But that spell did not work.")
                        else:
                            add_message("But it did nothing.")
                    elif 0 < len(damaged_targets) and self.combat_encounter is not None:
                        self.update_status_dialog(False, message_dialog)
                        self.combat_encounter.render_damage_to_targets(damaged_targets)

                elif item.type == DialogActionEnum.WAIT:
                    if isinstance(item.count, int):
                        pygame.time.wait(item.count)
                    else:
                        print(
                            "ERROR: Wait not supported for item.count of",
                            item.count,
                            flush=True,
                        )

                elif item.type == DialogActionEnum.SET_LEVEL:
                    level_name = ""
                    if item.name is not None:
                        level_name = item.name
                    for hero in self.hero_party.members:
                        hero.level = Level.create_null(level_name)
                        hero.max_hp = hero.level.hp
                        hero.max_mp = hero.level.mp
                        hero.hp = min(hero.hp, hero.max_hp)
                        hero.mp = min(hero.mp, hero.max_mp)
                    self.update_status_dialog(
                        flip_buffer=not item.bypass, message_dialog=message_dialog
                    )

                elif item.type == DialogActionEnum.JOIN_PARTY:
                    if item.name is not None:
                        if self.hero_party.get_member(item.name) is None:
                            # Add NPC with the same name, if any.  If not, default to the NPC the PC is talking to.
                            npc_to_join_party = self.game_state.get_npc_by_name(
                                item.name
                            )
                            if npc_to_join_party is None:
                                print(
                                    f"Failed to find an NPC with name {item.name}",
                                    flush=True,
                                )
                                npc_to_join_party = npc

                            if npc_to_join_party is not None:
                                self.hero_party.add_non_combat_member(
                                    item.name, npc_to_join_party
                                )
                            else:
                                print(
                                    "ERROR: JOIN_PARTY failed because the NPC is None",
                                    flush=True,
                                )
                        else:
                            print(
                                f"Not adding {item.name} to the party because they are already a member",
                                flush=True,
                            )

                    else:
                        print(
                            "ERROR: JOIN_PARTY failed because the name is None",
                            flush=True,
                        )

                elif item.type == DialogActionEnum.LEAVE_PARTY:
                    if item.name is not None:
                        self.hero_party.remove_member(item.name)
                    else:
                        print(
                            "ERROR: LEAVE_PARTY failed because the name is None",
                            flush=True,
                        )

                else:
                    print(
                        "ERROR: Unsupported DialogActionEnum of", item.type, flush=True
                    )

            else:
                print("ERROR: Not a supported type", item, flush=True)

        if depth == 0 and not message_dialog.is_empty():
            self.wait_for_acknowledgement(message_dialog)
