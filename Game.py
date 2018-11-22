#!/usr/bin/env python

import random

from AudioPlayer import AudioPlayer
from GameInfo import GameInfo
from GameState import GameMode, GameState
from GameDialog import *
from GameDialogEvaluator import GameDialogEvaluator
import GameEvents
import SurfaceEffects
from MonsterState import MonsterState


class Game:
    def __init__(self,
                 base_path: str,
                 game_xml_path: str,
                 desired_win_size_pixels: Optional[Point],
                 tile_size_pixels: int,
                 saved_game_file: Optional[str] = None) -> None:
        self.game_state = GameState(base_path,
                                    game_xml_path,
                                    desired_win_size_pixels,
                                    tile_size_pixels,
                                    saved_game_file)
        self.gde = GameDialogEvaluator(self.game_state)
        GameDialog.init(self.game_state.win_size_tiles, tile_size_pixels)

    def run_game_loop(self) -> None:
        self.game_state.is_running = True
        while self.game_state.is_running:
            if GameMode.TITLE_SCREEN == self.game_state.game_mode:
                self.title_screen_loop()
            elif GameMode.EXPLORING == self.game_state.game_mode:
                self.exploring_loop()
            elif GameMode.ENCOUNTER == self.game_state.game_mode:
                self.encounter_loop()

    def title_screen_loop(self) -> None:
        # TODO: Implement
        # for now transition straight to exploring
        self.game_state.game_mode = GameMode.EXPLORING

    '''
    def traverse_dialog(self,
                        message_dialog: GameDialog,
                        dialog: Union[DialogType, str],
                        depth: int = 0) -> None:

        if depth == 0:
            self.traverse_dialog_wait_before_new_text = False
            # print( 'Intialized self.traverseDialogWaitBeforeNewText to False', flush=True )
            self.dialog_variable_replacement: Dict[str, str] = {}
            self.dialog_vendor_buy_options_variable_replacement: Dict[
                str, DialogVendorBuyOptionsParamWithoutReplacementType] = {}
            self.dialog_vendor_sell_options_variable_replacement: Dict[
                str, DialogVendorSellOptionsParamWithoutReplacementType] = {}
            self.dialog_variable_replacement['[NAME]'] = self.game_state.hero_party.main_character.name
            self.dialog_variable_replacement['[NEXT_LEVEL_XP]'] = str(
                self.game_state.hero_party.main_character.calc_xp_to_next_level(self.game_state.game_info.levels))
            map_origin = self.game_state.game_info.maps[self.game_state.map_state.name].origin
            if map_origin is not None:
                map_coord = self.game_state.hero_party.members[0].curr_pos_dat_tile - map_origin
                self.dialog_variable_replacement['[X]'] = str(abs(map_coord.x))
                self.dialog_variable_replacement['[Y]'] = str(abs(map_coord.y))
                if map_coord.x < 0:
                    self.dialog_variable_replacement['[X_DIR]'] = 'West'
                else:
                    self.dialog_variable_replacement['[X_DIR]'] = 'East'
                if map_coord.y < 0:
                    self.dialog_variable_replacement['[Y_DIR]'] = 'North'
                else:
                    self.dialog_variable_replacement['[Y_DIR]'] = 'South'

        # Ensure dialog is a list and not a str to allow iteration
        if isinstance(dialog, str):
            temp = dialog
            dialog = [temp]

        for item in dialog:
            # print( 'item =', item, flush=True )
            if isinstance(item, str):
                # print( 'Dialog Text =', item, flush=True )
                # Wait for user to acknowledge that the message is read
                # before iterating to display the next part of the message
                # or exiting out of the loop when the full message has been
                # displayed.
                if self.traverse_dialog_wait_before_new_text:
                    # print( 'Waiting because self.traverseDialogWaitBeforeNewText is True', flush=True )
                    self.gde.wait_for_acknowledgement(message_dialog)
                # else:
                #   print( 'Not waiting because self.traverseDialogWaitBeforeNewText is False', flush=True )

                # Perform variable replacement
                for variable in self.dialog_variable_replacement:
                    item = item.replace(variable, str(self.dialog_variable_replacement[variable]))

                if not message_dialog.is_empty():
                    message_dialog.add_message('')
                message_dialog.add_message(item)

                message_dialog.blit(self.game_state.screen, True)
                while self.game_state.is_running and message_dialog.has_more_content():
                    self.gde.wait_for_acknowledgement(message_dialog)
                    message_dialog.advance_content()
                    message_dialog.blit(self.game_state.screen, True)
                self.traverse_dialog_wait_before_new_text = True
                # print( 'Set self.traverseDialogWaitBeforeNewText to True', flush=True )

            elif isinstance(item, list):
                # print( 'Dialog Sub Tree =', item, flush=True )
                if self.game_state.is_running:
                    self.gde.traverse_dialog(message_dialog, item, depth + 1)

            elif isinstance(item, DialogGoTo):
                # print( 'Dialog Go To =', item, flush=True )
                if item.label in self.game_state.game_info.dialog_sequences:
                    if self.game_state.is_running:
                        self.gde.traverse_dialog(message_dialog, self.game_state.game_info.dialog_sequences[item.label],
                                             depth + 1)
                else:
                    print('ERROR: ' + item.label + ' not found in dialogSequences', flush=True)

            elif isinstance(item, DialogVariable):
                # print( 'Dialog Variable =', item, flush=True )
                try:
                    (minVal, maxVal) = GameTypes.parse_int_range(item.value)
                    item.value = str(random.randint(minVal, maxVal))
                    # print( 'Dialog Variable (after value int conversion) =', item, flush=True )
                except:
                    pass
                self.dialog_variable_replacement[item.name] = item.value

            elif isinstance(item, DialogVendorBuyOptionsVariable):
                # print('Dialog Vendor Buy Options Variable =', item, flush=True)
                self.dialog_vendor_buy_options_variable_replacement[item.name] = item.value

            elif isinstance(item, DialogVendorSellOptionsVariable):
                # print('Dialog Vendor Sell Options Variable =', item, flush=True)
                self.dialog_vendor_sell_options_variable_replacement[item.name] = item.value

            elif isinstance(item, dict):
                # print('Dialog Option =', item, flush=True)
                self.traverse_dialog_wait_before_new_text = False
                # print('Set self.traverseDialogWaitBeforeNewText to False', flush=True)
                options = list(item.keys())
                message_dialog.add_menu_prompt(options, len(options), GameDialogSpacing.SPACERS)
                message_dialog.blit(self.game_state.screen, True)
                menu_result = None
                while self.game_state.is_running and menu_result is None:
                    menu_result = self.gde.get_menu_result(message_dialog)
                if self.game_state.is_running and menu_result is not None:
                    # print('menu_result =', menu_result, flush=True)
                    self.gde.traverse_dialog(message_dialog, item[menu_result], depth + 1)

            elif isinstance(item, DialogVendorBuyOptions):
                # print('Dialog Vendor Buy Options =', item, flush=True)
                if isinstance(item.name_and_gp_row_data,
                              str) and item.name_and_gp_row_data in self.dialog_vendor_buy_options_variable_replacement:
                    name_and_gp_row_data = self.dialog_vendor_buy_options_variable_replacement[
                        item.name_and_gp_row_data]
                elif not isinstance(item.name_and_gp_row_data, str):
                    name_and_gp_row_data = item.name_and_gp_row_data
                else:
                    name_and_gp_row_data = []
                if len(name_and_gp_row_data) == 0:
                    print('ERROR: No options from vendor', flush=True)
                    self.gde.traverse_dialog(message_dialog, 'Nature calls and I need to run.  Sorry!', depth + 1)
                    break
                self.traverse_dialog_wait_before_new_text = False
                # print('Set self.traverseDialogWaitBeforeNewText to False', flush=True)
                message_dialog.add_menu_prompt(name_and_gp_row_data, 2, GameDialogSpacing.OUTSIDE_JUSTIFIED)
                message_dialog.blit(self.game_state.screen, True)
                menu_result = None
                while self.game_state.is_running and menu_result is None:
                    menu_result = self.gde.get_menu_result(message_dialog)
                if menu_result is not None:
                    # print('menu_result =', menu_result, flush=True)
                    self.dialog_variable_replacement['[ITEM]'] = menu_result
                    for itemNameAndGp in name_and_gp_row_data:
                        if itemNameAndGp[0] == menu_result:
                            self.dialog_variable_replacement['[COST]'] = itemNameAndGp[1]

            elif isinstance(item, DialogVendorSellOptions):
                # print( 'Dialog Vendor Sell Options =', item, flush=True )
                if (isinstance(item.item_types, str)
                        and item.item_types in self.dialog_vendor_sell_options_variable_replacement):
                    item_types = self.dialog_vendor_sell_options_variable_replacement[item.item_types]
                elif not isinstance(item.item_types, str):
                    item_types = item.item_types
                else:
                    item_types = []
                item_row_data = self.game_state.hero_party.main_character.get_item_row_data(True, item_types)
                if len(item_row_data) == 0:
                    self.gde.traverse_dialog(message_dialog, 'Thou dost not have any items to sell.', depth + 1)
                    break
                self.traverse_dialog_wait_before_new_text = False
                # print( 'Set self.traverseDialogWaitBeforeNewText to False', flush=True )
                message_dialog.add_menu_prompt(item_row_data, 2, GameDialogSpacing.OUTSIDE_JUSTIFIED)
                message_dialog.blit(self.game_state.screen, True)
                menu_result = None
                while self.game_state.is_running and menu_result is None:
                    menu_result = self.gde.get_menu_result(message_dialog)
                if menu_result is not None:
                    # print( 'menu_result =', menu_result, flush=True )
                    self.dialog_variable_replacement['[ITEM]'] = menu_result
                    self.dialog_variable_replacement['[COST]'] =\
                        str(self.game_state.game_info.items[menu_result].gp // 2)

            elif isinstance(item, DialogCheck):
                # print( 'Dialog Check =', item, flush=True )

                check_result = True

                if item.type == DialogCheckEnum.HAS_ITEM or item.type == DialogCheckEnum.LACKS_ITEM:
                    # Perform variable replacement
                    item_name = str(item.name)
                    item_count = 1
                    for variable in self.dialog_variable_replacement:
                        if isinstance(item_name, str):
                            item_name = item_name.replace(variable, self.dialog_variable_replacement[variable])
                        if isinstance(item.count, str):
                            try:
                                item_count = int(item.count.replace(variable, self.dialog_variable_replacement[variable]))
                            except:
                                print('ERROR: Failed to convert item_count to int:', item.count, flush=True)

                    if item_name == 'gp':
                        check_value = self.game_state.hero_party.gp
                    elif item_name == 'lv':
                        check_value = self.game_state.hero_party.main_character.level.number
                    else:
                        check_value = self.game_state.hero_party.get_item_count(item_name)

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
                    check_result = item.map_name == self.game_state.map_state.name \
                                   and (item.map_pos is None
                                        or item.map_pos == self.game_state.hero_party.members[0].curr_pos_dat_tile)

                elif item.type == DialogCheckEnum.IS_IN_COMBAT:
                    print('ERROR: DialogCheckEnum.IS_IN_COMBAT is not implemented to check the monster type',
                          flush=True)
                    check_result = GameMode.ENCOUNTER == self.game_state.game_mode  # and (item.name is None or item.name ==

                elif item.type == DialogCheckEnum.IS_NOT_IN_COMBAT:
                    check_result = GameMode.ENCOUNTER != self.game_state.game_mode

                else:
                    print('ERROR: Unsupported DialogCheckEnum of', item.type, flush=True)

                if not check_result:
                    if item.failed_check_dialog is not None:
                        self.gde.traverse_dialog(message_dialog, item.failed_check_dialog, depth + 1)
                    break

            elif isinstance(item, DialogAction):
                # print( 'Dialog Action =', item, flush=True )

                self.traverse_dialog_wait_before_new_text = False
                # print( 'Set self.traverseDialogWaitBeforeNewText to False', flush=True )

                if item.type == DialogActionEnum.SAVE_GAME:
                    self.game_state.save()
                elif item.type == DialogActionEnum.MAGIC_RESTORE:
                    if item.count == 'unlimited':
                        for hero in self.game_state.hero_party.members:
                            hero.mp = hero.level.mp
                    else:
                        (minRestore, maxRestore) = GameTypes.parse_int_range(item.count)
                        # TODO: Need to know which character to which magic restore should apply
                        self.game_state.hero_party.main_character.mp += random.randint(minRestore, maxRestore)
                    for hero in self.game_state.hero_party.members:
                        hero.mp = min(hero.mp, hero.level.mp)
                    GameDialog.create_exploring_status_dialog(
                        self.game_state.hero_party).blit(self.game_state.screen, True)

                elif item.type == DialogActionEnum.HEALTH_RESTORE:
                    if item.count == 'unlimited':
                        for hero in self.game_state.hero_party.members:
                            hero.hp = hero.level.hp
                    else:
                        (minRestore, maxRestore) = GameTypes.parse_int_range(item.count)
                        # TODO: Need to know which character to which health restore should apply
                        self.game_state.hero_party.main_character.hp += random.randint(minRestore, maxRestore)
                    for hero in self.game_state.hero_party.members:
                        hero.hp = min(hero.hp, hero.level.hp)
                    GameDialog.create_exploring_status_dialog(
                        self.game_state.hero_party).blit(self.game_state.screen, True)

                elif item.type == DialogActionEnum.GAIN_ITEM or item.type == DialogActionEnum.LOSE_ITEM:
                    # Perform variable replacement
                    item_name = str(item.name)
                    item_count = 1
                    for variable in self.dialog_variable_replacement:
                        item_name = item_name.replace(variable, self.dialog_variable_replacement[variable])
                        if isinstance(item.count, str):
                            try:
                                item_count = int(item.count.replace(variable,
                                                                    self.dialog_variable_replacement[variable]))
                            except:
                                print('ERROR: Failed to convert item_count to int so defaulting to 1:', item_count,
                                      flush=True)

                    if item_name == 'gp':
                        if item.type == DialogActionEnum.GAIN_ITEM:
                            self.game_state.hero_party.gp += item_count
                        elif item.type == DialogActionEnum.LOSE_ITEM:
                            self.game_state.hero_party.gp -= item_count
                            if self.game_state.hero_party.gp < 0:
                                self.game_state.hero_party.gp = 0
                        GameDialog.create_exploring_status_dialog(
                            self.game_state.hero_party).blit(self.game_state.screen, True)
                    elif item.type == DialogActionEnum.GAIN_ITEM:
                        if item_name in self.game_state.game_info.items:
                            self.game_state.hero_party.gain_item(self.game_state.game_info.items[item_name], item_count)
                        else:
                            self.game_state.hero_party.gain_progress_marker(item_name)
                    elif item.type == DialogActionEnum.LOSE_ITEM:
                        if item_name in self.game_state.game_info.items:
                            self.game_state.hero_party.lose_item(self.game_state.game_info.items[item_name], item_count)
                        else:
                            self.game_state.hero_party.lose_progress_marker(item_name)

                elif item.type == DialogActionEnum.SET_LIGHT_DIAMETER:
                    if isinstance(item.count, int):
                        self.game_state.light_diameter = item.count
                    else:
                        self.game_state.light_diameter = None
                    self.game_state.draw_map()

                elif item.type == DialogActionEnum.REPEL_MONSTERS:
                    print('ERROR: DialogActionEnum.REPEL_MONSTERS is not implemented', flush=True)

                elif item.type == DialogActionEnum.GOTO_COORDINATES:
                    for hero in self.game_state.hero_party.members:
                        hero.curr_pos_offset_img_px = Point(0, 0)
                        if item.map_pos is not None:
                            hero.curr_pos_dat_tile = hero.dest_pos_dat_tile = item.map_pos
                        if item.map_dir is not None:
                            hero.direction = item.map_dir
                    if item.map_name is not None:
                        self.game_state.set_map(item.map_name)
                    else:
                        self.game_state.set_map(self.game_state.map_state.name)
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
                        AudioPlayer().play_music(
                            item.name,
                            self.game_state.game_info.maps[self.game_state.map_state.name].music)

                elif item.type == DialogActionEnum.VISUAL_EFFECT:
                    if item.name == 'fadeToBlackAndBack':
                        SurfaceEffects.fade_to_black_and_back(self.game_state.screen)
                    elif item.name == 'flickering':
                        SurfaceEffects.flickering(self.game_state.screen)
                    elif item.name == 'rainbowEffect':
                        SurfaceEffects.rainbow_effect(self.game_state.screen,
                                                      self.game_state.game_info.tiles['water'].image[0])
                    else:
                        print('ERROR: DialogActionEnum.VISUAL_EFFECT is not implemented for effect', item.name,
                              flush=True)

                elif item.type == DialogActionEnum.ATTACK_MONSTER:
                    monster_info = None
                    if item.name in self.game_state.game_info.monsters:
                        monster_info = self.game_state.game_info.monsters[item.name]
                    self.encounter_loop(monster_info=monster_info,
                                        victory_dialog=item.victory_dialog,
                                        run_away_dialog=item.run_away_dialog,
                                        encounter_music=item.encounter_music,
                                        message_dialog=message_dialog)

                elif item.type == DialogActionEnum.OPEN_DOOR:
                    self.game_state.open_door()

                else:
                    print('ERROR: Unsupported DialogActionEnum of', item.type, flush=True)

            else:
                print('ERROR: Not a supported type', item, flush=True)

        if depth == 0 and not message_dialog.is_empty():
            self.gde.wait_for_acknowledgement(message_dialog)

    def dialog_loop(self,
                    dialog: Union[DialogType, str]) -> None:
        # TODO: move screen and isRunning to GameState then move this functionality to GameDialog using GameState

        # Save off initial key repeat settings
        (orig_repeat1, orig_repeat2) = pygame.key.get_repeat()
        pygame.key.set_repeat()
        # print( 'Disabled key repeat', flush=True )
        GameEvents.get_events()  # Clear event queue

        # Create the status and message dialogs
        GameDialog.create_exploring_status_dialog(self.game_state.hero_party).blit(self.game_state.screen, False)
        messageDialog = GameDialog.create_message_dialog()

        self.gde.traverse_dialog(messageDialog, dialog)

        # Restore initial key repeat settings
        pygame.key.set_repeat(orig_repeat1, orig_repeat2)

        # Redraw the map
        self.game_state.draw_map(True)

    def wait_for_acknowledgement(self, message_dialog: Optional[GameDialog] = None) -> None:
        # TODO: move screen and isRunning to GameState then move this functionality to GameDialog using GameState

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
        # TODO: move screen and isRunning to GameState then move this functionality to GameDialog using GameState

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
                        menu_result = ""
                    else:
                        menu_dialog.process_event(event, self.game_state.screen)
                elif event.type == pygame.QUIT:
                    self.game_state.is_running = False

        if menu_result == "":
            menu_result = None

        return menu_result
    '''

    def exploring_loop(self) -> None:

        pygame.key.set_repeat(10, 10)
        map_name = self.game_state.map_state.name

        while self.game_state.is_running and GameMode.EXPLORING == self.game_state.game_mode:

            # Generate the map state a mode or map change
            if (self.game_state.last_game_mode != self.game_state.game_mode or
                    map_name != self.game_state.map_state.name):
                self.game_state.last_game_mode = self.game_state.game_mode
                map_name = self.game_state.map_state.name

                # Play the music for the map
                audio_player = AudioPlayer()
                audio_player.play_music(self.game_state.game_info.maps[self.game_state.map_state.name].music)

                # Bounds checking to ensure a valid hero/center position
                self.game_state.bounds_check_pc_position()

                # Draw the map to the screen
                self.game_state.draw_map()

            if self.game_state.pending_dialog is not None:
                self.gde.dialog_loop(self.game_state.pending_dialog)
                self.game_state.pending_dialog = None

            # Process events
            events = GameEvents.get_events()

            for event in events:
                moving = False
                menu = False
                talking = False
                searching = False
                pc_dir_old = self.game_state.hero_party.members[0].direction

                if event.type == pygame.QUIT:
                    self.game_state.is_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.is_running = False
                    elif event.key == pygame.K_RETURN:
                        menu = True
                    elif event.key == pygame.K_DOWN:
                        self.game_state.hero_party.members[0].direction = Direction.SOUTH
                        moving = True
                    elif event.key == pygame.K_UP:
                        self.game_state.hero_party.members[0].direction = Direction.NORTH
                        moving = True
                    elif event.key == pygame.K_LEFT:
                        self.game_state.hero_party.members[0].direction = Direction.WEST
                        moving = True
                    elif event.key == pygame.K_RIGHT:
                        self.game_state.hero_party.members[0].direction = Direction.EAST
                        moving = True

                # Allow a change of direction without moving
                if pc_dir_old != self.game_state.hero_party.members[0].direction:
                    # print('Change of direction detected', flush=True)
                    moving = False
                    self.game_state.advance_tick()
                    self.game_state.advance_tick()
                    self.game_state.advance_tick()
                    self.game_state.advance_tick()

                if menu:
                    # Save off initial screen and key repeat settings
                    (orig_repeat1, orig_repeat2) = pygame.key.get_repeat()
                    pygame.key.set_repeat()
                    # print( 'Disabled key repeat', flush=True )
                    pygame.event.get()  # Clear event queue

                    GameDialog.create_exploring_status_dialog(
                        self.game_state.hero_party).blit(self.game_state.screen, False)
                    menu_dialog = GameDialog.create_exploring_menu()
                    menu_dialog.blit(self.game_state.screen, True)
                    menu_result = self.gde.get_menu_result(menu_dialog)
                    # print( 'menu_result =', menu_result, flush=True )
                    if menu_result == 'TALK':
                        talking = True
                    elif menu_result == 'STAIRS':
                        if not self.game_state.make_map_transition(self.game_state.get_point_transition()):
                            self.gde.dialog_loop('There are no stairs here.')
                    elif menu_result == 'STATUS':
                        GameDialog.create_full_status_dialog(
                            self.game_state.hero_party).blit(self.game_state.screen, True)
                        self.gde.wait_for_acknowledgement()
                    elif menu_result == 'SEARCH':
                        searching = True
                    elif menu_result == 'SPELL':
                        # TODO: Need to choose the spellcaster
                        availableSpellNames = self.game_state.get_available_spell_names()
                        if len(availableSpellNames) == 0:
                            self.gde.dialog_loop('Thou hast not yet learned any spells.')
                        else:
                            menu_dialog = GameDialog.create_menu_dialog(
                                Point(-1, menu_dialog.pos_tile.y + menu_dialog.size_tiles.h + 1),
                                None,
                                'SPELLS',
                                availableSpellNames,
                                1)
                            menu_dialog.blit(self.game_state.screen, True)
                            menu_result = self.gde.get_menu_result(menu_dialog)
                            # print( 'menu_result =', menu_result, flush=True )
                            if menu_result is not None:
                                spell = self.game_state.game_info.spells[menu_result]
                                if self.game_state.hero_party.main_character.mp >= spell.mp:
                                    self.game_state.hero_party.main_character.mp -= spell.mp

                                    AudioPlayer().play_sound('castSpell.wav')
                                    SurfaceEffects.flickering(self.game_state.screen)

                                    if spell.max_hp_recover > 0:
                                        # TODO: Need to choose the target for the spell
                                        hp_recover = random.randint(spell.min_hp_recover, spell.max_hp_recover)
                                        self.game_state.hero_party.main_character.hp = min(
                                            self.game_state.hero_party.main_character.level.hp,
                                            self.game_state.hero_party.main_character.hp + hp_recover)
                                    elif spell.name == 'Radiant':
                                        if (self.game_state.light_diameter is not None
                                                and self.game_state.light_diameter < 7):
                                            # TODO: Add diminishing light diameter
                                            self.game_state.light_diameter = 7
                                            self.game_state.draw_map()
                                    elif spell.name == 'Outside':
                                        # TODO: If not on the overworld map, go to the last coordinates from the
                                        #       overworld map
                                        print('Spell not implemented', flush=True)
                                    elif spell.name == 'Return':
                                        # TODO: Return shouldn't work from caves and the return coordinates shouldn't be
                                        #       hardcoded
                                        for hero in self.game_state.hero_party.members:
                                            hero.curr_pos_dat_tile = Point(43, 44)
                                            hero.curr_pos_offset_img_px = Point(0, 0)
                                            hero.direction = Direction.SOUTH
                                        self.game_state.set_map('overworld')
                                    elif spell.name == 'Repel':
                                        print('Spell not implemented', flush=True)

                                    GameDialog.create_exploring_status_dialog(
                                        self.game_state.hero_party).blit(self.game_state.screen, False)
                                    self.gde.dialog_loop('[NAME] cast the spell of ' + spell.name + '.')

                                else:
                                    self.gde.dialog_loop('Thou dost not have enough magic to cast the spell.')

                    elif menu_result == 'ITEM':
                        # TODO: Need to choose the hero to use an item
                        item_row_data = self.game_state.hero_party.main_character.get_item_row_data()
                        if len(item_row_data) == 0:
                            self.gde.dialog_loop('Thou dost not have any items.')
                        else:
                            menu_dialog = GameDialog.create_menu_dialog(
                                Point(-1, menu_dialog.pos_tile.y + menu_dialog.size_tiles.h + 1),
                                None,
                                'ITEMS',
                                item_row_data,
                                2,
                                GameDialogSpacing.OUTSIDE_JUSTIFIED)
                            menu_dialog.blit(self.game_state.screen, True)
                            item_result = self.gde.get_menu_result(menu_dialog)
                            # print( 'item_result =', item_result, flush=True )

                            if item_result is not None:
                                item_options = self.game_state.hero_party.main_character.get_item_options(item_result)
                                if len(item_row_data) == 0:
                                    self.gde.dialog_loop('[NAME] studied the object and was confounded by it.')
                                else:
                                    menu_dialog = GameDialog.create_menu_dialog(
                                        Point(-1, menu_dialog.pos_tile.y + menu_dialog.size_tiles.h + 1),
                                        None,
                                        None,
                                        item_options,
                                        len(item_options))
                                    menu_dialog.blit(self.game_state.screen, True)
                                    action_result = self.gde.get_menu_result(menu_dialog)
                                    # print( 'action_result =', action_result, flush=True )
                                    if action_result == 'DROP':
                                        # TODO: Add an are you sure prompt here
                                        self.game_state.hero_party.lose_item(
                                            self.game_state.game_info.items[item_result])
                                    elif action_result == 'EQUIP':
                                        self.game_state.hero_party.main_character.equip_item(item_result)
                                    elif action_result == 'UNEQUIP':
                                        self.game_state.hero_party.main_character.unequip_item(item_result)
                                    elif action_result == 'USE':
                                        item = self.game_state.game_info.items[item_result]
                                        if isinstance(item, Tool) and item.use_dialog is not None:
                                            self.gde.dialog_loop(item.use_dialog)

                    elif menu_result != None:
                        print('ERROR:  Unsupoorted menu_result =', menu_result, flush=True)

                    # Erase menu and restore initial key repeat settings
                    pygame.key.set_repeat(orig_repeat1, orig_repeat2)
                    self.game_state.draw_map()
                    pygame.display.flip()

                if talking:
                    talk_dest_dat_tile = self.game_state.hero_party.members[0].curr_pos_dat_tile\
                                       + self.game_state.hero_party.members[0].direction.get_vector()
                    talk_dest_tile_type = self.game_state.get_tile_info(talk_dest_dat_tile)
                    if talk_dest_tile_type.can_talk_over:
                        talk_dest_dat_tile = talk_dest_dat_tile \
                                             + self.game_state.hero_party.members[0].direction.get_vector()
                    dialog: DialogType = ['There is no one there.']
                    for npc in self.game_state.npcs:
                        if (npc.npc_info is not None and
                                (talk_dest_dat_tile == npc.curr_pos_dat_tile or
                                 talk_dest_dat_tile == npc.dest_pos_dat_tile)):
                            if npc.npc_info.dialog is not None:
                                dialog = npc.npc_info.dialog

                                # NPC should turn to face you
                                if (npc.direction !=
                                        self.game_state.hero_party.members[0].direction.get_opposite()):
                                    self.game_state.erase_character(npc)
                                    npc.direction =\
                                        self.game_state.hero_party.members[0].direction.get_opposite()
                                    self.game_state.draw_character(npc)
                                    pygame.display.flip()
                            else:
                                dialog = ['They pay you no mind.']
                            break
                    self.gde.dialog_loop(dialog)

                if searching:
                    dialog = ['[NAME] searched the ground and found nothing.']
                    for decoration in self.game_state.get_decorations():
                        if (decoration.type is not None
                                and self.game_state.game_info.decorations[decoration.type].remove_with_search):
                            self.game_state.remove_decoration(decoration)

                        if decoration.dialog is not None:
                            dialog = decoration.dialog
                            break

                    self.gde.dialog_loop(dialog)

                if moving:
                    self.scroll_tile()

            self.game_state.advance_tick()

    def encounter_loop(self,
                       monster_info: Optional[MonsterInfo] = None,
                       victory_dialog: Optional[DialogType] = None,
                       run_away_dialog: Optional[DialogType] = None,
                       encounter_music: Optional[str] = None,
                       message_dialog: Optional[GameDialog] = None) -> None:
        # TODO: Rework this to invoke from an existing dialog or None.
        #       Allow a specific monster to be passed in.
        #       Allow run away and victory dialog to be passed in and triggered.

        # Clear any menus
        self.game_state.draw_map(False)

        encounter_image = self.game_state.game_info.maps[self.game_state.map_state.name].encounter_image
        if encounter_image is None:
            print('ERROR: Cannot host an encounter on a map without an encounter image', flush=True)
            return

        # Save off initial screen and key repeat settings
        (orig_repeat1, orig_repeat2) = pygame.key.get_repeat()
        pygame.key.set_repeat()
        # print( 'Disabled key repeat', flush=True )
        pygame.event.get()  # Clear event queue
        orig_screen = self.game_state.screen.copy()

        # Determine the monster for the encounter
        special_monster_info = None
        if monster_info is None:
            # Check for special monsters
            special_monster_info = self.game_state.get_special_monster()
            if special_monster_info is not None:
                monster_info = self.game_state.game_info.monsters[special_monster_info.name]
                victory_dialog = special_monster_info.victory_dialog
                run_away_dialog = special_monster_info.run_away_dialog

            # Pick the monster
            if monster_info is None:
                monster_info = self.game_state.game_info.monsters[
                    random.choice(self.game_state.get_tile_monsters())]

        # Initialize hero and monster  states
        self.game_state.hero_party.clear_combat_status_affects()
        monster = MonsterState(monster_info, special_monster_info)

        # Start encounter music
        if encounter_music is None:
            encounter_music = '06_-_Dragon_Warrior_-_NES_-_Fight.ogg'
        audio_player = AudioPlayer();
        audio_player.play_music(encounter_music)
        # audio_player.playMusic('14_Dragon_Quest_1_-_A_Monster_Draws_Near.mp3',
        #                        '24_Dragon_Quest_1_-_Monster_Battle.mp3')

        # Start the encounter dialog (used to position the encounter background)
        if message_dialog is None:
            message_dialog = GameDialog.create_message_dialog()
        else:
            message_dialog.add_message('')
        message_dialog.add_message('A ' + monster.get_name() + ' draws near!')

        # Render the encounter background
        damage_flicker_pixels = 4
        encounter_image_size_pixels = Point(encounter_image.get_size())
        encounter_image_dest_pixels = Point(
            (self.game_state.win_size_pixels.w - encounter_image_size_pixels.w) / 2,
            message_dialog.pos_tile.y * self.game_state.game_info.tile_size_pixels
            - encounter_image_size_pixels.h + damage_flicker_pixels)
        self.game_state.screen.blit(encounter_image, encounter_image_dest_pixels)

        # Render the monster
        monster_image_size_pixels = Point(monster_info.image.get_size())
        monster_image_dest_pixels = Point(
            (self.game_state.win_size_pixels.x - monster_image_size_pixels.x) / 2,
            encounter_image_dest_pixels.y + encounter_image_size_pixels.y
            - monster_image_size_pixels.y - self.game_state.game_info.tile_size_pixels)
        self.game_state.screen.blit(monster.monster_info.image, monster_image_dest_pixels)

        # Display status, command prompt dialog, and command menu
        is_start = True
        while self.game_state.is_running:
            GameDialog.create_encounter_status_dialog(self.game_state.hero_party).blit(self.game_state.screen, False)

            # The first time through, check to see if the monster runs away or takes the initiative
            skip_hero_attack = False
            if is_start:
                is_start = False

                # Check if the monster is going to run away.
                if monster.should_run_away(self.game_state.hero_party.main_character):
                    # TODO: Play sound?
                    monster.has_run_away = True
                    message_dialog.add_message('The ' + monster.get_name() + ' is running away.')
                    break

                # Check if the monster takes the initiative and attacks first
                if monster.has_initiative(self.game_state.hero_party.main_character):
                    message_dialog.add_message('The ' + monster.get_name() + ' attacked before '
                                               + self.game_state.hero_party.main_character.get_name() + ' was ready')
                    skip_hero_attack = True

            # Perform player character turn
            if not skip_hero_attack:

                message_dialog.add_message('')

                if self.game_state.hero_party.main_character.is_asleep:
                    # Check if player wakes up
                    if self.game_state.hero_party.main_character.is_still_asleep():
                        if self.game_state.hero_party.main_character.turns_asleep == 1:
                            message_dialog.add_message(self.game_state.hero_party.main_character.get_name()
                                                       + ' is asleep.')
                        else:
                            message_dialog.add_message(self.game_state.hero_party.main_character.get_name()
                                                       + ' is still asleep.')
                    else:
                        message_dialog.add_message(self.game_state.hero_party.main_character.get_name() + ' awakes.')

                while self.game_state.is_running and not self.game_state.hero_party.main_character.is_asleep:

                    message_dialog.add_encounter_prompt()
                    message_dialog.blit(self.game_state.screen, True)
                    menu_result = None
                    while self.game_state.is_running and menu_result is None:
                        menu_result = self.gde.get_menu_result(message_dialog)
                    if not self.game_state.is_running:
                        break

                    # Process encounter menu selection
                    if menu_result == 'FIGHT':

                        message_dialog.add_message(self.game_state.hero_party.main_character.name + ' attacks!')

                        # Check for a critical strike
                        if self.game_state.hero_party.main_character.critical_hit_check(monster):
                            # TODO: Play sound?
                            message_dialog.add_message('Excellent move!')
                            damage = self.game_state.hero_party.main_character.calc_critical_hit_damage_to_monster(
                                monster)
                        else:
                            damage = self.game_state.hero_party.main_character.calc_regular_hit_damage_to_monster(
                                monster)

                        # Check for a monster dodge
                        if 0 == damage or monster.is_dodging_attack():
                            audio_player.play_sound('Dragon Warrior [Dragon Quest] SFX (9).wav')
                            message_dialog.add_message(
                                'The ' + monster.get_name() + ' dodges '
                                + self.game_state.hero_party.main_character.get_name() + "'s strike.")
                        else:
                            # TODO: Play different sound based on damage of attack
                            audio_player.play_sound('Dragon Warrior [Dragon Quest] SFX (5).wav')
                            message_dialog.add_message(
                                'The ' + monster.get_name() + "'s hit points reduced by " + str(damage) + '.')
                            monster.hp -= damage
                            for flickerTimes in range(10):
                                self.game_state.screen.blit(monster.monster_info.dmg_image, monster_image_dest_pixels)
                                pygame.display.flip()
                                pygame.time.Clock().tick(30)
                                self.game_state.screen.blit(monster.monster_info.image, monster_image_dest_pixels)
                                pygame.display.flip()
                                pygame.time.Clock().tick(30)

                        # The <monster name> is asleep.
                        # Thou hast done well in defeating the <monster name>.
                        # Thy Experience increases by #.  Thy GOLD increases by #.
                        # The <monster name> is running away.
                        # <player name> started to run away.
                        # <player name> started to run away but was blocked in front.
                        # The <monster name> attacked before <player name> was ready.
                        # The <monster name> attacks! Thy Hit Points decreased by 1.
                    elif menu_result == 'RUN':
                        if monster.is_blocking_escape(self.game_state.hero_party.main_character):
                            # TODO: Play sound?
                            message_dialog.add_message(
                                self.game_state.hero_party.main_character.get_name()
                                + ' started to run away but was blocked in front.')
                        else:
                            audio_player.play_sound('runAway.wav')
                            message_dialog.add_message(self.game_state.hero_party.main_character.get_name()
                                                       + ' started to run away.')

                            if run_away_dialog is not None:
                                self.gde.traverse_dialog(message_dialog, run_away_dialog, depth=1)

                            self.game_state.hero_party.main_character.has_run_away = True
                            break

                    elif menu_result == 'SPELL':
                        available_spell_names = self.game_state.get_available_spell_names()
                        if len(available_spell_names) == 0:
                            message_dialog.add_message('Thou hast not yet learned any spells.')
                            continue
                        else:
                            menu_dialog = GameDialog.create_menu_dialog(
                                Point(-1, 1),
                                None,
                                'SPELLS',
                                available_spell_names,
                                1)
                            menu_dialog.blit(self.game_state.screen, True)
                            menu_result = self.gde.get_menu_result(menu_dialog)
                            # print( 'menu_result =', menu_result, flush=True )
                            if menu_result is not None:
                                spell = self.game_state.game_info.spells[menu_result]
                                if self.game_state.hero_party.main_character.mp >= spell.mp:
                                    self.game_state.hero_party.main_character.mp -= spell.mp

                                    AudioPlayer().play_sound('castSpell.wav')
                                    SurfaceEffects.flickering(self.game_state.screen)

                                    spell_worked = True
                                    if self.game_state.hero_party.main_character.does_spell_work(spell, monster):
                                        if spell.max_hp_recover > 0:
                                            hp_recover = random.randint(spell.min_hp_recover, spell.max_hp_recover)
                                            self.game_state.hero_party.main_character.hp = min(
                                                self.game_state.hero_party.main_character.level.hp,
                                                self.game_state.hero_party.main_character.hp + hp_recover)
                                        elif spell.max_damage_by_hero > 0:
                                            damage = random.randint(spell.min_damage_by_hero,
                                                                    spell.max_damage_by_hero)
                                            message_dialog.add_message('The ' + monster.get_name()
                                                                       + "'s hit points reduced by "
                                                                       + str(damage) + '.')
                                            monster.hp -= damage
                                        elif 'SLEEP' == spell.name.upper():
                                            monster.is_asleep = True
                                        elif 'STOPSPELL' == spell.name.upper():
                                            monster.are_spells_blocked = True
                                        else:
                                            spell_worked = False
                                    else:
                                        spell_worked = False

                                    if spell_worked:
                                        message_dialog.add_message(
                                            self.game_state.hero_party.main_character.name
                                            + ' cast the spell of ' + spell.name.lower() + '.')
                                    else:
                                        message_dialog.add_message(
                                            self.game_state.hero_party.main_character.get_name()
                                            + ' cast the spell of ' + spell.name.lower()
                                            + ' but the spell did not work.')

                                    GameDialog.create_encounter_status_dialog(self.game_state.hero_party).blit(
                                        self.game_state.screen, False)

                                else:
                                    message_dialog.add_message('Thou dost not have enough magic to cast the spell.')
                                    continue
                            menu_dialog.erase(self.game_state.screen, orig_screen, True)
                    elif menu_result == 'ITEM':
                        print('Items are not implemented', flush=True)
                        continue
                    else:
                        continue

                    # If here the turn was successfully completed
                    break

                # Check for ran away death or monster death
                if not self.game_state.hero_party.is_still_in_combat() or not monster.is_alive():
                    break

                message_dialog.blit(self.game_state.screen, True)
                self.gde.wait_for_acknowledgement(message_dialog)

            # Perform monster turn
            message_dialog.add_message('')

            # Check if the monster wakes up
            if monster.is_asleep:
                if monster.is_still_asleep():
                    if monster.turns_asleep == 1:
                        message_dialog.add_message(monster.get_name() + ' is asleep.')
                    else:
                        message_dialog.add_message(monster.get_name() + ' is still asleep.')
                else:
                    message_dialog.add_message(monster.get_name() + ' awakes.')

            if monster.is_asleep:
                # Skip to next player turn
                continue

            # Check if the monster is going to run away.  Only random monsters should ever run away.
            if monster.should_run_away(self.game_state.hero_party.main_character):
                # TODO: Play sound?
                monster.has_run_away = True
                message_dialog.add_message('The ' + monster.get_name() + ' is running away.')
                break

            # Determine the monster action
            chosen_monster_action = MonsterActionEnum.ATTACK
            for monster_action in monster.monster_info.monster_actions:
                monster_health_ratio = monster.hp / monster.max_hp
                if monster_health_ratio > monster_action.health_ratio_threshold:
                    continue
                if (MonsterActionEnum.SLEEP == monster_action.type
                        and self.game_state.hero_party.main_character.is_asleep):
                    continue
                if (MonsterActionEnum.STOPSPELL == monster_action.type
                        and self.game_state.hero_party.main_character.are_spells_blocked):
                    continue
                if random.uniform(0, 1) < monster_action.probability:
                    chosen_monster_action = monster_action.type
                    break

            # Perform the monster action
            damage = 0
            if chosen_monster_action == MonsterActionEnum.HEAL or chosen_monster_action == MonsterActionEnum.HEALMORE:
                AudioPlayer().play_sound('castSpell.wav')
                SurfaceEffects.flickering(self.game_state.screen)
                if chosen_monster_action == MonsterActionEnum.HEAL:
                    message_dialog.add_message('The ' + monster.get_name() + ' chants the spell of heal.')
                else:
                    message_dialog.add_message('The ' + monster.get_name() + ' chants the spell of healmore.')
                if monster.are_spells_blocked:
                    message_dialog.add_message('But that spell hath been blocked.')
                else:
                    message_dialog.add_message('The ' + monster.get_name() + ' hath recovered.')
                    monster.hp = monster.max_hp
            elif chosen_monster_action == MonsterActionEnum.HURT or chosen_monster_action == MonsterActionEnum.HURTMORE:
                AudioPlayer().play_sound('castSpell.wav')
                SurfaceEffects.flickering(self.game_state.screen)
                if chosen_monster_action == MonsterActionEnum.HURT:
                    spell = self.game_state.game_info.spells['Hurt']
                else:
                    spell = self.game_state.game_info.spells['Hurtmore']
                message_dialog.add_message('The ' + monster.get_name() + ' chants the spell of '
                                           + spell.name.lower() + '.')
                damage = random.randint(spell.min_damage_by_monster, spell.max_damage_by_monster)
                if self.game_state.hero_party.main_character.armor is not None:
                    # TODO: Allow damage reduction from other sources
                    damage = round(damage * self.game_state.hero_party.main_character.armor.hurt_dmg_modifier)
                if not monster.does_spell_work(spell, self.game_state.hero_party.main_character):
                    message_dialog.add_message('But that spell hath been blocked.')
                    damage = 0
            elif chosen_monster_action == MonsterActionEnum.SLEEP:
                AudioPlayer().play_sound('castSpell.wav')
                SurfaceEffects.flickering(self.game_state.screen)
                message_dialog.add_message('The ' + monster.get_name() + ' chants the spell of sleep.')
                if monster.does_spell_work(self.game_state.game_info.spells['Sleep'],
                                           self.game_state.hero_party.main_character):
                    message_dialog.add_message('Thou art asleep.')
                    self.game_state.hero_party.main_character.is_asleep = True
                else:
                    message_dialog.add_message('But that spell hath been blocked.')
            elif chosen_monster_action == MonsterActionEnum.STOPSPELL:
                AudioPlayer().play_sound('castSpell.wav')
                SurfaceEffects.flickering(self.game_state.screen)
                message_dialog.add_message('The ' + monster.get_name() + ' chants the spell of stopspell.')
                if monster.does_spell_work(self.game_state.game_info.spells['Stopspell'],
                                           self.game_state.hero_party.main_character):
                    message_dialog.add_message(self.game_state.hero_party.main_character.name
                                               + "'s spells hath been blocked.")
                    self.game_state.hero_party.main_character.are_spells_blocked = True
                else:
                    # TODO: Different messages depending on why the spell did not work?
                    message_dialog.add_message('But that spell did not work.')
                    # message_dialog.add_message('But that spell hath been blocked.')
            elif (chosen_monster_action == MonsterActionEnum.BREATH_FIRE
                  or chosen_monster_action == MonsterActionEnum.BREATH_STRONG_FIRE):
                AudioPlayer().play_sound('fireBreathingAttack.wav')
                message_dialog.add_message('The ' + monster.get_name() + ' is breathing fire.')
                if chosen_monster_action == MonsterActionEnum.BREATH_FIRE:
                    damage = random.randint(16, 23)
                else:
                    damage = random.randint(65, 72)
                if self.game_state.hero_party.main_character.armor is not None:
                    # TODO: Allow damage reduction from other sources
                    damage = round(damage * self.game_state.hero_party.main_character.armor.fire_dmg_modifier)
            else:  # chosen_monster_action == MonsterActionEnum.ATTACK
                damage = self.game_state.hero_party.main_character.calc_hit_damage_from_monster(monster)
                if 0 == damage:
                    # TODO: Play sound?
                    message_dialog.add_message(
                        'The ' + monster.get_name() + ' attacks! '
                        + self.game_state.hero_party.main_character.name + ' dodges the strike.')
                else:
                    # TODO: Play different sound based on strength of attack
                    audio_player.play_sound('Dragon Warrior [Dragon Quest] SFX (5).wav')
                    message_dialog.add_message('The ' + monster.get_name() + ' attacks!')

            if damage != 0:
                message_dialog.add_message('Thy hit points reduced by ' + str(damage) + '.')
                self.game_state.hero_party.main_character.hp -= damage
                if self.game_state.hero_party.main_character.hp < 0:
                    self.game_state.hero_party.main_character.hp = 0
                for flickerTimes in range(10):
                    offset_pixels = Point(damage_flicker_pixels, damage_flicker_pixels)
                    self.game_state.screen.blit(orig_screen, (0, 0))
                    self.game_state.screen.blit(encounter_image, encounter_image_dest_pixels)
                    self.game_state.screen.blit(monster.monster_info.image, monster_image_dest_pixels)
                    GameDialog.create_encounter_status_dialog(
                        self.game_state.hero_party).blit(self.game_state.screen, False, offset_pixels)
                    message_dialog.blit(self.game_state.screen, True, offset_pixels)
                    pygame.time.Clock().tick(30)
                    self.game_state.screen.blit(orig_screen, (0, 0))
                    self.game_state.screen.blit(encounter_image, encounter_image_dest_pixels)
                    self.game_state.screen.blit(monster.monster_info.image, monster_image_dest_pixels)
                    GameDialog.create_encounter_status_dialog(
                        self.game_state.hero_party).blit(self.game_state.screen, False)
                    message_dialog.blit(self.game_state.screen, True)
                    pygame.time.Clock().tick(30)

                # Check for player death
                if self.game_state.hero_party.main_character.hp <= 0:
                    break

        audio_player.stop_music()
        if self.game_state.hero_party.main_character.hp <= 0:
            self.check_for_player_death(message_dialog)
        elif monster.hp <= 0:
            audio_player.play_sound('17_-_Dragon_Warrior_-_NES_-_Enemy_Defeated.ogg')
            self.game_state.draw_map(False)
            self.game_state.screen.blit(encounter_image, encounter_image_dest_pixels)
            message_dialog.add_message(
                'Thou has done well in defeating the ' + monster.get_name() + '. Thy experience increases by ' + str(
                    monster.xp) + '. Thy gold increases by ' + str(monster.gp) + '.')
            self.game_state.hero_party.gp += monster.gp
            self.game_state.hero_party.main_character.xp += monster.xp
            GameDialog.create_exploring_status_dialog(
                self.game_state.hero_party).blit(self.game_state.screen, False)
            if self.game_state.hero_party.main_character.level_up_check(self.game_state.game_info.levels):
                self.gde.wait_for_acknowledgement(message_dialog)
                audio_player.play_sound('18_-_Dragon_Warrior_-_NES_-_Level_Up.ogg')
                message_dialog.add_message(
                    '\nCourage and wit have served thee well. Thou hast been promoted to the next level.')
                GameDialog.create_exploring_status_dialog(
                    self.game_state.hero_party).blit(self.game_state.screen, False)

            message_dialog.blit(self.game_state.screen, True)

            if victory_dialog is not None:
                self.gde.traverse_dialog(message_dialog, victory_dialog)

            self.gde.wait_for_acknowledgement(message_dialog)

        # Restore initial key repeat settings
        pygame.key.set_repeat(orig_repeat1, orig_repeat2)

        # Draw the map
        if self.game_state.hero_party.main_character.hp > 0:
            self.game_state.draw_map(True)

        # Return to exploring after completion of encounter
        self.game_state.last_game_mode = GameMode.ENCOUNTER
        self.game_state.game_mode = GameMode.EXPLORING

    def check_for_player_death(self, message_dialog: Optional[GameDialog] = None) -> None:
        if self.game_state.hero_party.main_character.hp <= 0:
            # Player death
            self.game_state.hero_party.main_character.hp = 0
            AudioPlayer().stop_music()
            AudioPlayer().play_sound('20_-_Dragon_Warrior_-_NES_-_Dead.ogg')
            GameDialog.create_exploring_status_dialog(
                self.game_state.hero_party).blit(self.game_state.screen, False)
            if message_dialog is None:
                message_dialog = GameDialog.create_message_dialog()
            else:
                message_dialog.add_message('')
            message_dialog.add_message('Thou art dead.')
            self.gde.wait_for_acknowledgement(message_dialog)
            for hero in self.game_state.hero_party.members:
                hero.curr_pos_dat_tile = hero.dest_pos_dat_tile = self.game_state.game_info.death_hero_pos_dat_tile
                hero.curr_pos_offset_img_px = Point(0, 0)
                hero.direction = self.game_state.game_info.death_hero_pos_dir
                hero.hp = hero.level.hp
                hero.mp = hero.level.mp
            self.game_state.pending_dialog = self.game_state.game_info.death_dialog
            self.game_state.hero_party.gp = self.game_state.hero_party.gp // 2
            self.game_state.set_map(self.game_state.game_info.death_map, respawn_decorations=True)

    def scroll_tile(self) -> None:

        transition: Optional[Union[LeavingTransition, PointTransition]] = None

        map_image_rect = self.game_state.get_map_image_rect()
        orig_map_image_rect = self.game_state.get_map_image_rect()
        # NOTE: tile_size_pixels must be divisible by image_px_step_size
        image_px_step_size = self.game_state.game_info.tile_size_pixels // 8
        tile_move_steps = self.game_state.game_info.tile_size_pixels // image_px_step_size

        # Determine the destination tile and pixel count for the scroll
        hero_dest_dat_tile = self.game_state.hero_party.members[0].curr_pos_dat_tile \
                             + self.game_state.hero_party.members[0].direction.get_vector()

        # Validate if the destination tile is navigable
        movement_allowed = self.game_state.can_move_to_tile(hero_dest_dat_tile)

        # Play a walking sound or bump sound based on whether the movement was allowed
        audio_player = AudioPlayer()
        movement_hp_penalty = 0
        if movement_allowed:
            dest_tile_type = self.game_state.get_tile_info(hero_dest_dat_tile)

            self.game_state.hero_party.members[0].dest_pos_dat_tile = hero_dest_dat_tile
            for hero_idx in range(1, len(self.game_state.hero_party.members)):
                hero = self.game_state.hero_party.members[hero_idx]
                hero.dest_pos_dat_tile = self.game_state.hero_party.members[hero_idx-1].curr_pos_dat_tile
                if hero.curr_pos_dat_tile != hero.dest_pos_dat_tile:
                    hero.direction = Direction.get_direction(hero.dest_pos_dat_tile - hero.curr_pos_dat_tile)

            # Determine if the movement should result in a transition to another map
            if (self.game_state.game_info.maps[self.game_state.map_state.name].leaving_transition is not None
                and (hero_dest_dat_tile[0] == 0
                     or hero_dest_dat_tile[1] == 0
                     or hero_dest_dat_tile[0] ==
                     self.game_state.game_info.maps[self.game_state.map_state.name].size[0] - 1
                     or hero_dest_dat_tile[1] ==
                     self.game_state.game_info.maps[self.game_state.map_state.name].size[1] - 1)):
                # Map leaving transition
                # print('Leaving map', self.gameState.mapState.mapName, flush=True)
                transition = self.game_state.game_info.maps[self.game_state.map_state.name].leaving_transition
            else:
                # See if this tile has any associated transitions
                print('Check for transitions at', hero_dest_dat_tile,
                      flush=True)  # TODO: Uncomment for coordinate logging
                transition = self.game_state.get_point_transition(hero_dest_dat_tile)

            # Check for tile penalty effects
            if dest_tile_type.hp_penalty > 0 and not self.game_state.hero_party.is_ignoring_tile_penalties():
                audio_player.play_sound('walking.wav')
                movement_hp_penalty = dest_tile_type.hp_penalty
        else:
            audio_player.play_sound('bump.wav')

        for x in range(tile_move_steps):

            if movement_allowed:
                # Erase the characters
                self.game_state.erase_characters()

                # Scroll the view
                SurfaceEffects.scroll_view(self.game_state.screen,
                                           self.game_state.get_map_image(),
                                           self.game_state.hero_party.members[0].direction,
                                           map_image_rect,
                                           1,
                                           image_px_step_size)
                self.game_state.hero_party.members[0].curr_pos_offset_img_px = Point(
                    map_image_rect.x - orig_map_image_rect.x, map_image_rect.y - orig_map_image_rect.y)
                for hero in self.game_state.hero_party.members[1:]:
                    if hero.curr_pos_dat_tile != hero.dest_pos_dat_tile:
                        hero.curr_pos_offset_img_px = hero.direction.get_vector() * image_px_step_size * (x+1)

                if self.game_state.is_light_restricted():
                    self.game_state.draw_map(False)

                if movement_hp_penalty > 0:
                    if x == tile_move_steps - 2:
                        flicker_surface = pygame.Surface(self.game_state.screen.get_size())
                        flicker_surface.fill(pygame.Color('red'))
                        flicker_surface.set_alpha(128)
                        self.game_state.screen.blit(flicker_surface, (0, 0))
                    elif x == tile_move_steps - 1:
                        self.game_state.draw_map(False)

            # Redraws the characters when movement_allowed is True
            self.game_state.advance_tick(movement_allowed)

        if movement_allowed:
            prev_pos_dat_tile = self.game_state.hero_party.members[0].curr_pos_dat_tile
            for hero in self.game_state.hero_party.members:
                hero.curr_pos_dat_tile = hero.dest_pos_dat_tile
                hero.curr_pos_offset_img_px = Point(0, 0)

            # Redraw the map on a transition between interior and exterior
            if (self.game_state.is_interior(prev_pos_dat_tile) !=
                    self.game_state.is_interior(self.game_state.hero_party.members[0].curr_pos_dat_tile)):
                self.game_state.draw_map(True)

            # Apply health penalty and check for player death
            for hero in self.game_state.hero_party.members:
                if not hero.is_ignoring_tile_penalties():
                    hero.hp -= movement_hp_penalty
            self.check_for_player_death()

            # At destination - now determine if an encounter should start
            if not self.game_state.make_map_transition(transition):
                # Check for special monster encounters
                if self.game_state.get_special_monster() is not None:
                    self.game_state.game_mode = GameMode.ENCOUNTER
                # Check for random encounters
                elif (len(self.game_state.get_tile_monsters()) > 0 and
                      random.uniform(0, 1) < dest_tile_type.spawn_rate):
                    self.game_state.game_mode = GameMode.ENCOUNTER


def main() -> None:
    import sys
    import os

    pygame.init()
    pygame.mouse.set_visible(False)

    joysticks = []
    print('pygame.joystick.get_count() =', pygame.joystick.get_count(), flush=True)
    for joystickId in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(joystickId)
        print('joystick.get_id() =', joystick.get_id(), flush=True)
        print('joystick.get_name() =', joystick.get_name(), flush=True)
        # if joystick.get_name() == 'Controller (Xbox One For Windows)':
        print('Initializing joystick...', flush=True)
        joystick.init()
        joysticks.append(joystick)

    saved_game_file = None
    if len(sys.argv) > 1:
        saved_game_file = sys.argv[1]

    # Initialize the game
    base_path = os.path.split(os.path.abspath(__file__))[0]
    game_xml_path = os.path.join(base_path, 'game.xml')
    win_size_pixels = None  # Point(1280, 960) # TODO: Get good size for system from OS or switch to fullscreen
    tile_size_pixels = 16 * 3
    game = Game(base_path, game_xml_path, win_size_pixels, tile_size_pixels, saved_game_file)

    # Run the game
    game.run_game_loop()

    # Exit the game
    AudioPlayer().terminate()
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
        traceback.print_exc()
