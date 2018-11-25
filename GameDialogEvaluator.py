#!/usr/bin/env python

from typing import Optional, List, Union

import pygame

from AudioPlayer import AudioPlayer
from CombatCharacterState import CombatCharacterState
from GameDialog import GameDialog, GameDialogSpacing
from GameTypes import ActionCategoryTypeEnum, DialogAction, DialogActionEnum, DialogCheck, DialogCheckEnum, \
    DialogGoTo, DialogType, DialogVariable, DialogVendorBuyOptions, DialogVendorBuyOptionsVariable, \
    DialogVendorSellOptions, DialogVendorSellOptionsVariable, GameTypes
from GameStateInterface import GameStateInterface
import GameEvents
from Point import Point
import SurfaceEffects


class GameDialogEvaluator:
    def __init__(self, game_state: GameStateInterface) -> None:
        self.game_state = game_state
        self.hero_party = game_state.get_hero_party()
        self.replacement_variables = game_state.get_dialog_replacement_variables()
        self.wait_before_new_text = False

        self.actor: CombatCharacterState = self.hero_party.main_character
        self.targets: List[CombatCharacterState] = self.hero_party.members

    # Set the source - the source may be called out for performing an action
    # The target may be called out in the dialog associated with the action
    def set_actor(self, source: CombatCharacterState) -> None:
        self.actor = source
        self.replacement_variables.generic['[ACTOR]'] = source.get_name()

    # Set the targets on which actions will be performed
    # When the target is singular, it may be called out in the dialog associated with the action
    def set_targets(self, targets: List[CombatCharacterState]) -> None:
        self.targets = targets
        if 1 == len(targets):
            self.replacement_variables.generic['[TARGET]'] = targets[0].get_name()
        else:
            del self.replacement_variables.generic['[TARGET]']

    def restore_default_source_and_target(self) -> None:
        self.set_actor(self.hero_party.main_character)
        self.set_targets(self.hero_party.members)

    def dialog_loop(self, dialog: Union[DialogType, str]) -> None:
        # Save off initial background image and key repeat settings
        background_image = self.game_state.screen.copy()
        (orig_repeat1, orig_repeat2) = pygame.key.get_repeat()
        pygame.key.set_repeat()
        # print( 'Disabled key repeat', flush=True )

        # Clear event queue
        GameEvents.get_events()

        # Create the status and message dialogs
        GameDialog.create_exploring_status_dialog(self.hero_party).blit(self.game_state.screen, False)
        message_dialog = GameDialog.create_message_dialog()

        self.traverse_dialog(message_dialog, dialog)

        # Restore initial background image and key repeat settings
        self.game_state.screen.blit(background_image, (0, 0))
        pygame.key.set_repeat(orig_repeat1, orig_repeat2)

        # Call game_state.draw_map but manually flip the buffer for the case where this method is a mock
        self.game_state.draw_map(False)
        pygame.display.flip()

    def wait_for_acknowledgement(self, message_dialog: Optional[GameDialog] = None) -> None:
        # Skip waiting for acknowledgement of message dialog if the content
        # was already acknowledged.
        if message_dialog is not None and message_dialog.is_acknowledged():
            return

        is_awaiting_acknowledgement = True
        is_waiting_indicator_drawn = False
        while self.game_state.is_running and is_awaiting_acknowledgement:
            # Process events
            events = GameEvents.get_events()
            if 0 == len(events):
                pygame.time.Clock().tick(8)
                if message_dialog is not None:
                    if is_waiting_indicator_drawn:
                        message_dialog.erase_waiting_indicator()
                    else:
                        message_dialog.draw_waiting_indicator()
                    is_waiting_indicator_drawn = not is_waiting_indicator_drawn
                    message_dialog.blit(self.game_state.screen, True)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.is_running = False
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        is_awaiting_acknowledgement = False
                elif event.type == pygame.QUIT:
                    self.game_state.is_running = False

        if self.game_state.is_running:
            if message_dialog is not None:
                message_dialog.acknowledge()
                if is_waiting_indicator_drawn:
                    message_dialog.erase_waiting_indicator()
                    message_dialog.blit(self.game_state.screen, True)

    def get_menu_result(self, menu_dialog: GameDialog) -> Optional[str]:
        menu_result = None
        while self.game_state.is_running and menu_result is None:
            events = GameEvents.get_events()
            if 0 == len(events):
                pygame.time.Clock().tick(30)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.is_running = False
                    elif event.key == pygame.K_RETURN:
                        menu_result = menu_dialog.get_selected_menu_option()
                    elif event.key == pygame.K_SPACE:
                        menu_result = None
                    else:
                        menu_dialog.process_event(event, self.game_state.screen)
                elif event.type == pygame.QUIT:
                    self.game_state.is_running = False

        if menu_result == "":
            menu_result = None

        return menu_result

    def update_status_dialog(self, update_display: bool = False) -> None:
        # TODO: Store off the message_dialog and ensure it is using the correct font color too
        if self.hero_party.get_lowest_health_ratio() >= 0.25:
            GameDialog.set_default_font_color(GameDialog.NOMINAL_HEALTH_FONT_COLOR)
        else:
            GameDialog.set_default_font_color(GameDialog.LOW_HEALTH_FONT_COLOR)

        if self.game_state.is_in_combat():
            GameDialog.create_encounter_status_dialog(
                self.hero_party).blit(self.game_state.screen, update_display)
        else:
            GameDialog.create_exploring_status_dialog(
                self.hero_party).blit(self.game_state.screen, update_display)

    def traverse_dialog(self,
                        message_dialog: GameDialog,
                        dialog: Union[DialogType, str],
                        depth: int = 0) -> None:

        if depth == 0:
            self.wait_before_new_text = False
            # print('Initialized self.traverse_dialog_wait_before_new_text to False', flush=True)
            self.replacement_variables = self.game_state.get_dialog_replacement_variables()
            self.replacement_variables.generic['[NAME]'] = self.hero_party.main_character.get_name()
            self.replacement_variables.generic['[ACTOR]'] = self.actor.get_name()
            if 1 == len(self.targets):
                self.replacement_variables.generic['[TARGET]'] = self.targets[0].get_name()
            else:
                del self.replacement_variables.generic['[TARGET]']

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
                for variable in self.replacement_variables.generic:
                    item = item.replace(variable, str(self.replacement_variables.generic[variable]))

                if not message_dialog.is_empty():
                    message_dialog.add_message('')
                message_dialog.add_message(item)

                message_dialog.blit(self.game_state.screen, True)
                while self.game_state.is_running and message_dialog.has_more_content():
                    self.wait_for_acknowledgement(message_dialog)
                    message_dialog.advance_content()
                    message_dialog.blit(self.game_state.screen, True)
                self.wait_before_new_text = True
                # print('Set self.traverse_dialog_wait_before_new_text to True', flush=True)

            elif isinstance(item, list):
                # print( 'Dialog Sub Tree =', item, flush=True )
                if self.game_state.is_running:
                    self.traverse_dialog(message_dialog, item, depth + 1)

            elif isinstance(item, DialogGoTo):
                # print( 'Dialog Go To =', item, flush=True )
                if item.label in self.game_state.get_dialog_sequences():
                    if self.game_state.is_running:
                        self.traverse_dialog(message_dialog, self.game_state.get_dialog_sequences()[item.label],
                                             depth + 1)
                else:
                    print('ERROR: ' + item.label + ' not found in dialogSequences', flush=True)

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
                message_dialog.add_menu_prompt(options, len(options), GameDialogSpacing.SPACERS)
                message_dialog.blit(self.game_state.screen, True)
                menu_result = None
                while self.game_state.is_running and menu_result is None:
                    menu_result = self.get_menu_result(message_dialog)
                if self.game_state.is_running and menu_result is not None:
                    # print('menu_result =', menu_result, flush=True)
                    self.traverse_dialog(message_dialog, item[menu_result], depth + 1)

            elif isinstance(item, DialogVendorBuyOptions):
                # print('Dialog Vendor Buy Options =', item, flush=True)
                if isinstance(item.name_and_gp_row_data,
                              str) and item.name_and_gp_row_data in self.replacement_variables.vendor_buy_options:
                    name_and_gp_row_data = self.replacement_variables.vendor_buy_options[item.name_and_gp_row_data]
                elif not isinstance(item.name_and_gp_row_data, str):
                    name_and_gp_row_data = item.name_and_gp_row_data
                else:
                    name_and_gp_row_data = []
                if len(name_and_gp_row_data) == 0:
                    print('ERROR: No options from vendor', flush=True)
                    self.traverse_dialog(message_dialog, 'Nature calls and I need to run.  Sorry!', depth + 1)
                    break
                self.wait_before_new_text = False
                # print('Set self.traverse_dialog_wait_before_new_text to False', flush=True)
                message_dialog.add_menu_prompt(name_and_gp_row_data, 2, GameDialogSpacing.OUTSIDE_JUSTIFIED)
                message_dialog.blit(self.game_state.screen, True)
                menu_result = None
                while self.game_state.is_running and menu_result is None:
                    menu_result = self.get_menu_result(message_dialog)
                if menu_result is not None:
                    # print('menu_result =', menu_result, flush=True)
                    self.replacement_variables.generic['[ITEM]'] = menu_result
                    for itemNameAndGp in name_and_gp_row_data:
                        if itemNameAndGp[0] == menu_result:
                            self.replacement_variables.generic['[COST]'] = itemNameAndGp[1]

            elif isinstance(item, DialogVendorSellOptions):
                # print( 'Dialog Vendor Sell Options =', item, flush=True )
                if (isinstance(item.item_types, str)
                        and item.item_types in self.replacement_variables.vendor_sell_options):
                    item_types = self.replacement_variables.vendor_sell_options[item.item_types]
                elif not isinstance(item.item_types, str):
                    item_types = item.item_types
                else:
                    item_types = []
                item_row_data = self.hero_party.get_item_row_data(True, item_types)
                if len(item_row_data) == 0:
                    self.traverse_dialog(message_dialog, 'Thou dost not have any items to sell.', depth + 1)
                    break
                self.wait_before_new_text = False
                # print( 'Set self.traverse_dialog_wait_before_new_text to False', flush=True )
                message_dialog.add_menu_prompt(item_row_data, 2, GameDialogSpacing.OUTSIDE_JUSTIFIED)
                message_dialog.blit(self.game_state.screen, True)
                menu_result = None
                while self.game_state.is_running and menu_result is None:
                    menu_result = self.get_menu_result(message_dialog)
                if menu_result is not None:
                    # print( 'menu_result =', menu_result, flush=True )
                    self.replacement_variables.generic['[ITEM]'] = menu_result
                    self.replacement_variables.generic['[COST]'] = str(self.game_state.get_item(menu_result).gp // 2)

            elif isinstance(item, DialogCheck):
                # print( 'Dialog Check =', item, flush=True )

                check_result = True

                if item.type == DialogCheckEnum.HAS_ITEM or item.type == DialogCheckEnum.LACKS_ITEM:
                    # Perform variable replacement
                    item_name = str(item.name)
                    item_count = 1
                    for variable in self.replacement_variables.generic:
                        if isinstance(item_name, str):
                            item_name = item_name.replace(variable, self.replacement_variables.generic[variable])
                        if isinstance(item.count, str):
                            try:
                                item_count = int(item.count.replace(variable,
                                                                    self.replacement_variables.generic[variable]))
                            except ValueError:
                                print('ERROR: Failed to convert item_count to int:', item.count, flush=True)

                    if item_name == 'gp':
                        check_value = self.hero_party.gp
                    elif item_name == 'lv':
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

                elif item.type == DialogCheckEnum.IS_FACING_DOOR:
                    check_result = self.game_state.is_facing_door()

                elif item.type == DialogCheckEnum.IS_OUTSIDE:
                    check_result = self.game_state.is_outside()

                elif item.type == DialogCheckEnum.IS_INSIDE:
                    check_result = not self.game_state.is_outside()

                elif item.type == DialogCheckEnum.IS_DARK:
                    check_result = self.game_state.is_light_restricted()

                elif item.type == DialogCheckEnum.IS_AT_COORDINATES:
                    check_result = (item.map_name == self.game_state.get_map_name()
                                    and (item.map_pos is None
                                         or item.map_pos == self.hero_party.get_curr_pos_dat_tile()))

                elif item.type == DialogCheckEnum.IS_IN_COMBAT:
                    print('ERROR: DialogCheckEnum.IS_IN_COMBAT is not implemented to check the monster type',
                          flush=True)
                    check_result = self.game_state.is_in_combat()

                elif item.type == DialogCheckEnum.IS_NOT_IN_COMBAT:
                    check_result = not self.game_state.is_in_combat()

                else:
                    print('ERROR: Unsupported DialogCheckEnum of', item.type, flush=True)

                if not check_result:
                    if item.failed_check_dialog is not None:
                        self.traverse_dialog(message_dialog, item.failed_check_dialog, depth + 1)
                    break

            elif isinstance(item, DialogAction):
                # print( 'Dialog Action =', item, flush=True )

                self.wait_before_new_text = False
                # print( 'Set self.traverse_dialog_wait_before_new_text to False', flush=True )

                if (ActionCategoryTypeEnum.MAGICAL == item.category
                        and self.game_state.is_in_combat()
                        and self.actor.are_spells_blocked):
                    message_dialog.add_message('But that spell hath been blocked.')
                    continue

                if item.type == DialogActionEnum.SAVE_GAME:
                    self.game_state.save()
                elif item.type == DialogActionEnum.MAGIC_RESTORE:
                    if item.count == 'unlimited':
                        for target in self.targets:
                            target.mp = target.max_mp
                    else:
                        for target in self.targets:
                            target.mp = min(target.max_mp, target.mp + GameTypes.get_int_value(item.count))
                    self.update_status_dialog(True)

                elif item.type == DialogActionEnum.HEALTH_RESTORE:
                    if item.count == 'unlimited':
                        for target in self.targets:
                            target.hp = target.max_hp
                    else:
                        for target in self.targets:
                            target.hp = min(target.max_hp, target.hp + GameTypes.get_int_value(item.count))
                    self.update_status_dialog(True)

                elif item.type == DialogActionEnum.GAIN_ITEM or item.type == DialogActionEnum.LOSE_ITEM:
                    # Perform variable replacement
                    item_name = str(item.name)
                    item_count = 1
                    for variable in self.replacement_variables.generic:
                        item_name = item_name.replace(variable, self.replacement_variables.generic[variable])
                        if isinstance(item.count, str):
                            try:
                                item_count = int(item.count.replace(variable,
                                                                    self.replacement_variables.generic[variable]))
                            except ValueError:
                                print('ERROR: Failed to convert item.count to int so defaulting to 1:', item.count,
                                      flush=True)

                    if item_name == 'gp':
                        if item.type == DialogActionEnum.GAIN_ITEM:
                            self.hero_party.gp += item_count
                        elif item.type == DialogActionEnum.LOSE_ITEM:
                            self.hero_party.gp -= item_count
                            if self.hero_party.gp < 0:
                                self.hero_party.gp = 0
                        self.update_status_dialog(True)
                    elif item.type == DialogActionEnum.GAIN_ITEM:
                        item_to_gain = self.game_state.get_item(item_name)
                        if item_to_gain is not None:
                            self.hero_party.gain_item(item_to_gain, item_count)
                        else:
                            self.hero_party.gain_progress_marker(item_name)
                    elif item.type == DialogActionEnum.LOSE_ITEM:
                        item_to_lose = self.game_state.get_item(item_name)
                        if item_to_lose is not None:
                            self.hero_party.lose_item(item_to_lose, item_count)
                        else:
                            self.hero_party.lose_progress_marker(item_name)

                elif item.type == DialogActionEnum.SET_LIGHT_DIAMETER:
                    if isinstance(item.count, int):
                        self.game_state.set_light_diameter(item.count)
                    else:
                        self.game_state.set_light_diameter(None)
                    self.game_state.draw_map()

                elif item.type == DialogActionEnum.REPEL_MONSTERS:
                    print('ERROR: DialogActionEnum.REPEL_MONSTERS is not implemented', flush=True)

                elif item.type == DialogActionEnum.GOTO_COORDINATES:
                    for hero in self.hero_party.members:
                        hero.curr_pos_offset_img_px = Point(0, 0)
                        if item.map_pos is not None:
                            hero.curr_pos_dat_tile = hero.dest_pos_dat_tile = item.map_pos
                        if item.map_dir is not None:
                            hero.direction = item.map_dir
                    if item.map_name is not None:
                        self.game_state.set_map(item.map_name)
                    else:
                        self.game_state.set_map(self.game_state.get_map_name())
                    self.game_state.draw_map(flip_buffer=message_dialog.is_empty())
                    if not message_dialog.is_empty():
                        message_dialog.blit(self.game_state.screen, True)

                elif item.type == DialogActionEnum.GOTO_LAST_OUTSIDE_COORDINATES:
                    print('ERROR: DialogActionEnum.GOTO_LAST_OUTSIDE_COORDINATES is not implemented', flush=True)

                elif item.type == DialogActionEnum.PLAY_SOUND:
                    # print( 'Play sound', item.name, flush=True )
                    if isinstance(item.name, str):
                        AudioPlayer().play_sound(item.name)

                elif item.type == DialogActionEnum.PLAY_MUSIC:
                    # print( 'Play music', item.name, flush=True )
                    if isinstance(item.name, str):
                        AudioPlayer().play_music(item.name, interrupt=True)

                elif item.type == DialogActionEnum.VISUAL_EFFECT:
                    if item.name == 'fadeToBlackAndBack':
                        SurfaceEffects.fade_to_black_and_back(self.game_state.screen)
                    elif item.name == 'flickering':
                        SurfaceEffects.flickering(self.game_state.screen)
                    elif item.name == 'rainbowEffect':
                        SurfaceEffects.rainbow_effect(self.game_state.screen,
                                                      self.game_state.get_tile('water').image[0])
                    else:
                        print('ERROR: DialogActionEnum.VISUAL_EFFECT is not implemented for effect', item.name,
                              flush=True)

                elif item.type == DialogActionEnum.START_ENCOUNTER:
                    # TODO: Make this work again
                    pass
                    # self.game_state.initiate_encounter(monster_info=self.game_state.get_monster(item.name),
                    #                                   victory_dialog=item.victory_dialog,
                    #                                   run_away_dialog=item.run_away_dialog,
                    #                                   encounter_music=item.encounter_music,
                    #                                   message_dialog=message_dialog)

                elif item.type == DialogActionEnum.OPEN_DOOR:
                    self.game_state.open_door()

                elif item.type == DialogActionEnum.SLEEP:
                    worked = False
                    for target in self.targets:
                        if self.actor.does_action_work(item.type, item.category, target):
                            target.is_asleep = True
                            worked = False
                            message_dialog.add_message(target.get_name() + ' is asleep.')
                    if not worked:
                        message_dialog.add_message('But that spell did not work.')

                elif item.type == DialogActionEnum.STOPSPELL:
                    worked = False
                    for target in self.targets:
                        if self.actor.does_action_work(item.type, item.category, target):
                            target.are_spells_blocked = True
                            worked = False
                            message_dialog.add_message(target.get_name() + "'s spells are blocked.")
                    if not worked:
                        message_dialog.add_message('But that spell did not work.')

                elif item.type == DialogActionEnum.DAMAGE_TARGET:
                    worked = False
                    for target in self.targets:
                        if self.actor.does_action_work(item.type, item.category, target):
                            # TODO: Need to address visualization of damage to target
                            damage = round(GameTypes.get_int_value(item.count) * target.get_damage_modifier(item.category))
                            target.hp = max(0, target.hp - damage)
                    if not worked:
                        message_dialog.add_message('But that spell did not work.')

                else:
                    print('ERROR: Unsupported DialogActionEnum of', item.type, flush=True)

            else:
                print('ERROR: Not a supported type', item, flush=True)

        if depth == 0 and not message_dialog.is_empty():
            self.wait_for_acknowledgement(message_dialog)


def main() -> None:
    # TODO
    pass


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
        traceback.print_exc()
