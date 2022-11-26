#!/usr/bin/env python

from typing import cast, List, Optional

# import datetime
import glob
import os
import random

import pygame

from generic_utils.point import Point

from pygame_utils.audio_player import AudioPlayer
import pygame_utils.game_events as GameEvents

from pydw.combat_character_state import CombatCharacterState
from pydw.game_dialog import GameDialog, GameDialogSpacing
from pydw.game_dialog_evaluator import GameDialogEvaluator
from pydw.game_info import GameInfo
from pydw.game_map import CharacterSprite
from pydw.game_state import GameState
from pydw.game_types import Direction, OutgoingTransition, Tool


class GameLoop:
    def __init__(self,
                 saves_path: str,
                 base_path: str,
                 game_xml_path: str,
                 desired_win_size_pixels: Optional[Point],
                 unscaled_tile_size_pixels: int,
                 desired_tile_scaling_factor: int,
                 verbose: bool = False) -> None:
        self.verbose = verbose
        self.first_block_occurred = False

        # Determine effective window size in both tiles and pixels
        # Initialize the pygame displays
        tile_scaling_factor = desired_tile_scaling_factor
        tile_size_pixels = unscaled_tile_size_pixels * tile_scaling_factor
        if desired_win_size_pixels is None:
            # Find index of largest display
            largest_display_index = largest_display_size = 0
            for display_index, (display_x_size, display_y_size) in enumerate(pygame.display.get_desktop_sizes()):
                current_display_size = display_x_size * display_y_size
                if current_display_size > largest_display_size:
                    largest_display_index = display_index
                    largest_display_size = current_display_size

            # Launch fullscreen on the largest display
            screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA,
                display=largest_display_index)
            self.win_size_pixels = Point(screen.get_size())
        else:
            self.win_size_pixels = desired_win_size_pixels // tile_size_pixels * tile_size_pixels
            pygame.display.set_mode(
                self.win_size_pixels.get_as_int_tuple(),
                pygame.RESIZABLE | pygame.SRCALPHA)
        win_size_tiles = self.win_size_pixels / tile_size_pixels

        # Determine if the tile scaling factor should be reduced
        # Base this decision on the size of the message dialog
        dialog_size_tiles = GameDialog.get_message_dialog_size_tiles(win_size_tiles)
        while tile_scaling_factor > 1 and (dialog_size_tiles.x < 10 or dialog_size_tiles.y < 5):
            tile_scaling_factor -= 1

            # Recompute the sizes after reducing tile_scaling_factor
            tile_size_pixels = unscaled_tile_size_pixels * tile_scaling_factor
            win_size_tiles = self.win_size_pixels / tile_size_pixels
            dialog_size_tiles = GameDialog.get_message_dialog_size_tiles(win_size_tiles)

        if verbose and tile_scaling_factor < desired_tile_scaling_factor:
            print(f'Reduced tile scaling factor to {tile_scaling_factor}', flush=True)

        self.title_image, self.title_music = \
            GameInfo.static_init(base_path, game_xml_path, win_size_tiles, tile_size_pixels)

        self.title_screen('Loading...')

        self.game_state = GameState(saves_path,
                                    base_path,
                                    game_xml_path,
                                    win_size_tiles,
                                    tile_size_pixels)
        self.gde = GameDialogEvaluator(self.game_state.game_info, self.game_state)
        self.gde.update_default_dialog_font_color()

    def run(self, pc_name_or_file_name: Optional[str] = None) -> None:
        self.game_state.is_running = True
        self.title_screen_loop(pc_name_or_file_name)
        self.exploring_loop()

    def title_screen(self, text: str) -> None:
        # Play title music and display title screen
        AudioPlayer().play_music(self.title_music)

        # Scale to up to 90% of the display width and/or 40% of the height
        title_image_size_px = Point(self.title_image.get_size())
        if title_image_size_px.w > self.win_size_pixels.w:
            # Scale down for small window sizes
            title_image_size_px *= 0.9 * self.win_size_pixels.w / title_image_size_px.w
        else:
            # Scale up for large window sizes
            title_image_size_px *= max(1, int(min(self.win_size_pixels.w * 0.9 / title_image_size_px.w,
                                                  self.win_size_pixels.h * 0.4 / title_image_size_px.h)))
        title_image = pygame.transform.scale(self.title_image, title_image_size_px.get_as_int_tuple())
        title_image_dest_px = Point((self.win_size_pixels.w - title_image_size_px.w) / 2,
                                    self.win_size_pixels.h / 2 - title_image_size_px.h)

        screen = pygame.display.get_surface()
        screen.fill('black')
        screen.blit(title_image, title_image_dest_px)
        title_image = GameDialog.font.render(text,
                                             GameDialog.anti_alias,
                                             pygame.Color('white'),
                                             pygame.Color('black'))
        title_image_dest_px = Point((self.win_size_pixels.w - title_image.get_width()) / 2,
                                    3 * self.win_size_pixels.h / 4)
        screen.blit(title_image, title_image_dest_px)
        pygame.display.flip()

    def title_screen_loop(self, pc_name_or_file_name: Optional[str] = None) -> None:
        self.title_screen('Press any key')

        # Wait for user input - any key press
        while self.game_state.is_running:
            waiting_for_user_input = True
            for event in GameEvents.get_events():
                if event.type == pygame.QUIT:
                    self.game_state.handle_quit(force=True)
                elif event.type == pygame.KEYDOWN:
                    AudioPlayer().play_sound('select')
                    waiting_for_user_input = False
                    break
            if waiting_for_user_input:
                pygame.time.wait(25)
            else:
                break

        # Prompt user for new game or to load a saved game
        if pc_name_or_file_name is None:
            # Get a list of the saved games
            saved_game_files = glob.glob(os.path.join(self.game_state.saves_path, '*.xml'))
            saved_games = []
            for saved_game_file in saved_game_files:
                saved_games.append(os.path.basename(saved_game_file)[:-4])

            while self.game_state.is_running:
                menu_options = []
                if 0 < len(saved_games):
                    menu_options.append('Continue a Quest')
                menu_options.append('Begin a Quest')
                if 0 < len(saved_games):
                    menu_options.append('Delete a Quest')
                if self.game_state.should_add_math_problems_in_combat():
                    menu_options.append('Combat Mode: Math')
                else:
                    menu_options.append('Combat Mode: Classic')

                message_dialog = GameDialog.create_message_dialog()
                message_dialog.add_menu_prompt(menu_options, 1)
                message_dialog.blit(self.game_state.screen, True)
                menu_result = self.gde.get_menu_result(message_dialog)
                # print('menu_result =', menu_result, flush=True)
                if menu_result == 'Continue a Quest':
                    message_dialog.clear()
                    message_dialog.add_menu_prompt(saved_games, 1)
                    message_dialog.blit(self.game_state.screen, True)
                    menu_result = self.gde.get_menu_result(message_dialog)
                    if menu_result is not None:
                        pc_name_or_file_name = menu_result
                        break
                if menu_result == 'Delete a Quest':
                    message_dialog.clear()
                    message_dialog.add_menu_prompt(saved_games, 1)
                    message_dialog.blit(self.game_state.screen, True)
                    menu_result = self.gde.get_menu_result(message_dialog)
                    if menu_result is not None:
                        message_dialog.add_yes_no_prompt('Are you sure?')
                        message_dialog.blit(self.game_state.screen, True)
                        if self.gde.get_menu_result(message_dialog) == 'YES':
                            saved_games.remove(menu_result)
                            # Delete the save game by archiving it off
                            saved_game_file = os.path.join(self.game_state.saves_path,
                                                           menu_result + '.xml')
                            self.game_state.archive_saved_game_file(saved_game_file, 'deleted')
                elif menu_result == 'Begin a Quest':
                    message_dialog.clear()
                    pc_name_or_file_name = self.gde.wait_for_user_input(message_dialog,  'What is your name?')[0]

                    if pc_name_or_file_name in saved_games:
                        self.gde.add_and_wait_for_message(
                            'Thou hast already started a quest.  Dost thou want to start over?', message_dialog)
                        message_dialog.add_yes_no_prompt()
                        message_dialog.blit(self.game_state.screen, True)
                        menu_result = self.gde.get_menu_result(message_dialog)
                        if menu_result == 'YES':
                            # Delete the existing save game by archiving it off
                            saved_game_file = os.path.join(self.game_state.saves_path,
                                                           pc_name_or_file_name + '.xml')
                            self.game_state.archive_saved_game_file(saved_game_file, 'deleted')
                        elif menu_result != 'NO':
                            continue
                    break
                elif menu_result is not None and menu_result.startswith('Combat Mode:'):
                    self.game_state.toggle_should_add_math_problems_in_combat()

        # Load the saved game
        self.game_state.load(pc_name_or_file_name)
        self.gde.refresh_game_state()

    def exploring_loop(self) -> None:
        map_name = ''

        while self.game_state.is_running:

            # Generate the map state a mode or map change
            if map_name != self.game_state.get_map_name():
                map_name = self.game_state.get_map_name()

                # Play the music for the map
                AudioPlayer().play_music(self.game_state.game_info.maps[self.game_state.get_map_name()].music)

                # Draw the map to the screen
                self.game_state.draw_map()

                # Clear the event queue for a clean start on the new map
                GameEvents.clear_events()

            if self.game_state.pending_dialog is not None:
                self.gde.dialog_loop(self.game_state.pending_dialog)
                self.game_state.pending_dialog = None

            # Process events
            # print(datetime.datetime.now(), 'exploring_loop:  Getting events...', flush=True)
            events = GameEvents.get_events(True)
            changed_direction = False

            for event in events:
                # print('exploring_loop:  Processing event', event, flush=True)
                move_direction: Optional[Direction] = None
                menu = False
                talking = False
                searching = False
                opening = False

                if event.type == pygame.QUIT:
                    self.game_state.handle_quit(force=True)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.handle_quit()
                    elif event.key == pygame.K_RETURN:
                        # Fast, smart interactions - skip launching the menu
                        if self.game_state.get_npc_to_talk_to() is not None:
                            talking = True
                        elif self.game_state.is_facing_openable_item():
                            opening = True
                        elif self.game_state.make_map_transition(self.game_state.get_point_transition()):
                            # Transitioned to a new map
                            pass
                        else:
                            searching = True
                    elif event.key == pygame.K_SPACE:
                        menu = True
                    elif event.key == pygame.K_F1:
                        AudioPlayer().play_sound('select')
                        self.game_state.save(quick_save=True)
                    else:
                        move_direction = Direction.get_optional_direction(event.key)
                        if move_direction is None:
                            continue
                else:
                    # print('exploring_loop:  Ignoring event', event, flush=True)
                    continue

                # print(datetime.datetime.now(), 'exploring_loop:  Processed event', event, flush=True)

                # Clear queued events upon finding an event to process
                GameEvents.clear_events()
                events = []

                if move_direction:
                    if changed_direction or self.game_state.hero_party.members[0].curr_pos_dat_tile != \
                                            self.game_state.hero_party.members[0].dest_pos_dat_tile:
                        # print('Ignoring move as another move is already in progress', flush=True)
                        continue
                    if move_direction != self.game_state.hero_party.members[0].direction:
                        self.game_state.hero_party.members[0].direction = move_direction
                        changed_direction = True
                    else:
                        self.game_state.hero_party.members[0].dest_pos_dat_tile = \
                            self.game_state.hero_party.members[0].curr_pos_dat_tile + move_direction.get_vector()

                if menu:
                    AudioPlayer().play_sound('select')
                    GameDialog.create_exploring_status_dialog(
                        self.game_state.hero_party).blit(self.game_state.screen, False)
                    menu_dialog = GameDialog.create_exploring_menu()
                    menu_dialog.blit(self.game_state.screen, True)
                    menu_result = self.gde.get_menu_result(menu_dialog)
                    # print('menu_result =', menu_result, flush=True)
                    if menu_result == 'TALK':
                        talking = True
                    elif menu_result == 'SEARCH':
                        searching = True
                    elif menu_result == 'OPEN':
                        opening = True
                    elif menu_result == 'STAIRS':
                        if not self.game_state.make_map_transition(self.game_state.get_point_transition()):
                            self.gde.dialog_loop('There are no stairs here.')
                    elif menu_result == 'STATUS':
                        GameDialog.create_full_status_dialog(
                            self.game_state.hero_party).blit(self.game_state.screen, True)
                        self.gde.wait_for_acknowledgement()
                    elif menu_result == 'SPELL':
                        # TODO: Need to choose the actor (spellcaster)
                        actor = self.game_state.hero_party.main_character
                        self.gde.set_actor(actor)
                        available_spell_names = actor.get_available_spell_names()
                        if len(available_spell_names) == 0:
                            self.gde.dialog_loop('Thou hast not yet learned any spells.')
                        else:
                            menu_dialog = GameDialog.create_menu_dialog(
                                Point(-1, menu_dialog.pos_tile.y + menu_dialog.size_tiles.h + 1),
                                None,
                                'SPELLS',
                                available_spell_names,
                                1)
                            menu_dialog.blit(self.game_state.screen, True)
                            menu_result = self.gde.get_menu_result(menu_dialog)
                            # print( 'menu_result =', menu_result, flush=True )
                            if menu_result is not None:
                                spell = self.game_state.game_info.spells[menu_result]
                                if actor.mp >= spell.mp:
                                    # TODO: Depending on the spell may need to select the target(s)
                                    targets = [actor]
                                    actor.mp -= spell.mp
                                    self.gde.set_targets(cast(List[CombatCharacterState], targets))
                                    self.gde.dialog_loop(spell.use_dialog)

                                    GameDialog.create_exploring_status_dialog(
                                        self.game_state.hero_party).blit(self.game_state.screen, False)
                                else:
                                    self.gde.dialog_loop('Thou dost not have enough magic to cast the spell.')

                        # Restore the default actor and targets after calling the spell
                        self.gde.restore_default_actor_and_targets()

                    elif menu_result == 'ITEM':
                        # TODO: Need to choose the hero to use an item
                        actor = self.game_state.hero_party.main_character
                        self.gde.set_actor(actor)
                        item_cols = 2
                        item_row_data = actor.get_item_row_data()
                        if len(item_row_data) == 0:
                            self.gde.dialog_loop('Thou dost not have any items.')
                        else:
                            menu_dialog = GameDialog.create_menu_dialog(
                                Point(-1, menu_dialog.pos_tile.y + menu_dialog.size_tiles.h + 1),
                                None,
                                'ITEMS',
                                item_row_data,
                                item_cols,
                                GameDialogSpacing.OUTSIDE_JUSTIFIED)
                            menu_dialog.blit(self.game_state.screen, True)
                            item_result = self.gde.get_menu_result(menu_dialog)
                            # print('item_result =', item_result, flush=True)

                            if item_result is not None:
                                item_options = self.game_state.hero_party.main_character.get_item_options(item_result)
                                if len(item_row_data) == 0:
                                    self.gde.dialog_loop("The item vanished in [ACTOR]'s hands.")
                                else:
                                    menu_dialog = GameDialog.create_menu_dialog(
                                        Point(-1, menu_dialog.pos_tile.y + menu_dialog.size_tiles.h + 1),
                                        None,
                                        None,
                                        item_options,
                                        len(item_options))
                                    menu_dialog.blit(self.game_state.screen, True)
                                    action_result = self.gde.get_menu_result(menu_dialog)
                                    # print('action_result =', action_result, flush=True)
                                    if action_result == 'DROP':
                                        # TODO: Add an are you sure prompt here
                                        self.game_state.hero_party.lose_item(item_result)
                                    elif action_result == 'EQUIP':
                                        self.game_state.hero_party.main_character.equip_item(item_result)
                                    elif action_result == 'UNEQUIP':
                                        self.game_state.hero_party.main_character.unequip_item(item_result)
                                    elif action_result == 'USE':
                                        item = self.game_state.hero_party.get_item(item_result)
                                        if item is not None and isinstance(item, Tool) and item.use_dialog is not None:
                                            # TODO: Depending on the item may need to select the target(s)
                                            targets = [actor]
                                            self.gde.set_targets(cast(List[CombatCharacterState], targets))
                                            self.gde.dialog_loop(item.use_dialog)
                                        else:
                                            self.gde.dialog_loop('[ACTOR] studied the object and was confounded by it.')

                        # Restore the default actor and targets after using the item
                        self.gde.restore_default_actor_and_targets()

                    elif menu_result is not None:
                        print('ERROR: Unsupported menu_result =', menu_result, flush=True)

                    # Erase menu
                    self.game_state.draw_map()
                    pygame.display.flip()

                if talking:
                    npc = self.game_state.get_npc_to_talk_to()
                    if npc:
                        if npc.npc_info.dialog is not None:
                            dialog = npc.npc_info.dialog
                            self.game_state.draw_map()
                        else:
                            dialog = ['They pay you no mind.']
                    else:
                        dialog = ['There is no one there.']
                    self.gde.dialog_loop(dialog, npc)

                if searching or opening:
                    decorations = self.game_state.get_decorations()
                    if searching:
                        dialog = ['[NAME] searched the ground and found nothing.']
                    else:
                        dialog = ['[NAME] found nothing to open.']
                        dest_tile = self.game_state.hero_party.members[0].curr_pos_dat_tile \
                                    + self.game_state.hero_party.members[0].direction.get_vector()
                        decorations += self.game_state.get_decorations(dest_tile)

                    for decoration in decorations:
                        requires_removal = False

                        if decoration.type is not None:
                            requires_removal = (decoration.type.remove_with_search or
                                                decoration.type.remove_with_open or
                                                decoration.type.remove_with_key)

                            if requires_removal:
                                if ((searching and decoration.type.remove_with_search) or
                                        (opening and decoration.type.remove_with_open)):
                                    if decoration.type.remove_sound is not None:
                                        AudioPlayer().play_sound(decoration.type.remove_sound)
                                    self.game_state.remove_decoration(decoration)
                                    self.game_state.draw_map()

                                    if decoration.dialog is not None:
                                        dialog = decoration.dialog
                                    else:
                                        dialog = []
                                    break
                                elif decoration.type.remove_with_key:
                                    key_item = self.game_state.game_info.items['Key']
                                    if self.game_state.hero_party.has_item(key_item.name) \
                                            and isinstance(key_item, Tool) \
                                            and key_item.use_dialog is not None:
                                        dialog = ['It is locked. Do you want to open it with a key?',
                                                  {'Yes': key_item.use_dialog,
                                                   'No': None}]
                                    else:
                                        dialog = ['It is locked.']
                                    break

                        if not requires_removal and decoration.dialog is not None:
                            dialog = decoration.dialog

                    self.gde.dialog_loop(dialog)

            if self.game_state.hero_party.members[0].curr_pos_dat_tile != \
               self.game_state.hero_party.members[0].dest_pos_dat_tile:
                self.scroll_tile()
            elif changed_direction:
                # On a direction change, unset first_block_occurred
                # if self.first_block_occurred: print('Clearing first_block_occurred on direction change', flush=True)
                self.first_block_occurred = False

                change_of_direction_ticks = max(2, CharacterSprite.get_tile_movement_steps() // 3)
                # print(f'advancing {change_of_direction_ticks} ticks in exploring_loop', flush=True)
                for _ in range(change_of_direction_ticks):
                    self.game_state.advance_tick()
            else:
                # When not moving, set the first_block_occurred
                # if not self.first_block_occurred: print('Setting first_block_occurred on stopping', flush=True)
                self.first_block_occurred = True

                # print('advancing one tick in exploring_loop', flush=True)
                self.game_state.advance_tick()

    def scroll_tile(self) -> None:

        transition: Optional[OutgoingTransition] = None

        # Determine the destination tile and pixel count for the scroll
        hero_dest_dat_tile = self.game_state.hero_party.members[0].dest_pos_dat_tile

        # Validate if the destination tile is navigable
        movement_allowed = self.game_state.can_move_to_tile(hero_dest_dat_tile)

        # Play a walking sound or bump sound based on whether the movement was allowed
        audio_player = AudioPlayer()
        movement_hp_penalty = 0
        if movement_allowed:
            dest_tile_type = self.game_state.get_tile_info(hero_dest_dat_tile)

            for hero_idx in range(1, len(self.game_state.hero_party.members)):
                hero = self.game_state.hero_party.members[hero_idx]
                hero.dest_pos_dat_tile = self.game_state.hero_party.members[hero_idx-1].curr_pos_dat_tile
                if hero.curr_pos_dat_tile != hero.dest_pos_dat_tile:
                    hero.direction = Direction.get_direction(hero.dest_pos_dat_tile - hero.curr_pos_dat_tile)

            # Determine if the movement should result in a transition to another map
            map_size = self.game_state.game_map.size()
            leaving_transition = self.game_state.game_info.maps[self.game_state.get_map_name()].leaving_transition
            if leaving_transition is not None:
                if leaving_transition.bounding_box:
                    if not leaving_transition.bounding_box.collidepoint(hero_dest_dat_tile.get_as_int_tuple()):
                        transition = leaving_transition
                elif (hero_dest_dat_tile[0] == 0
                      or hero_dest_dat_tile[1] == 0
                      or hero_dest_dat_tile[0] == map_size[0] - 1
                      or hero_dest_dat_tile[1] == map_size[1] - 1):
                    transition = leaving_transition
            if transition is None:
                if self.verbose:
                    encounter_background = self.game_state.get_encounter_background(hero_dest_dat_tile)
                    print('Check for transitions at', hero_dest_dat_tile, encounter_background, flush=True)

                # See if this tile has any associated transitions
                transition = self.game_state.get_point_transition(hero_dest_dat_tile,
                                                                  filter_to_automatic_transitions=True)
            else:
                # Map leaving transition
                # print('Leaving map', self.gameState.mapState.mapName, flush=True)
                pass

            # Check for tile penalty effects
            if dest_tile_type.hp_penalty > 0 and not self.game_state.hero_party.is_ignoring_tile_penalties():
                audio_player.play_sound('hit_lvl_1')
                movement_hp_penalty = dest_tile_type.hp_penalty

            # Check for any status effect changes or healing to occur as the party moves
            has_low_health = self.game_state.hero_party.has_low_health()
            dialog_from_inc_step_count = self.game_state.hero_party.inc_step_counter()
            if has_low_health != self.game_state.hero_party.has_low_health():
                # Change default dialog font color
                self.gde.update_default_dialog_font_color()

                # Redraw the map
                self.game_state.draw_map(True)
            if dialog_from_inc_step_count is not None:
                self.gde.dialog_loop(dialog_from_inc_step_count)

        # Handle being blocked by terrain.  Keep a counter in order to forgive the first occurrence as the blocked
        # sound effect was otherwise a bit excessive.
        if movement_allowed:
            # On allowed movement, unset first_block_occurred
            # if self.first_block_occurred: print('Clearing first_block_occurred on allowed movement', flush=True)
            self.first_block_occurred = False
        else:
            self.game_state.hero_party.members[0].dest_pos_dat_tile = \
                self.game_state.hero_party.members[0].curr_pos_dat_tile
            if self.first_block_occurred:
                # print('Successive block - playing blocked sound', flush=True)
                audio_player.play_sound('blocked')

            # On blocked movement, set first_block_occurred
            # if not self.first_block_occurred: print('First block - not playing blocked sound', flush=True)
            self.first_block_occurred = True

        first_frame = True
        while self.game_state.hero_party.members[0].curr_pos_dat_tile != \
                self.game_state.hero_party.members[0].dest_pos_dat_tile:
            # Redraws the characters when movement_allowed is True
            # print('advancing one tick in scroll_tile', flush=True)
            if movement_allowed and movement_hp_penalty > 0 and first_frame:
                flicker_surface = pygame.surface.Surface(self.game_state.screen.get_size())
                flicker_surface.fill('red')
                flicker_surface.set_alpha(128)
                self.game_state.advance_tick(update_map=True, draw_map=True, advance_time=False, flip_buffer=False)
                self.game_state.screen.blit(flicker_surface, (0, 0))
                self.game_state.advance_tick(update_map=False, draw_map=False, advance_time=True, flip_buffer=True)
                pygame.time.wait(20)
                first_frame = False
            else:
                self.game_state.advance_tick()

        if movement_allowed:
            # Apply health penalty and check for player death
            for hero in self.game_state.hero_party.members:
                if not hero.is_ignoring_tile_penalties():
                    hero.hp -= movement_hp_penalty
            self.gde.update_default_dialog_font_color()
            self.game_state.handle_death()

            # At destination - now determine if an encounter should start
            if not self.game_state.make_map_transition(transition):
                # Check for special monster encounters as well as random monsters
                if (self.game_state.get_special_monster() is not None or
                        (len(self.game_state.get_tile_monsters()) > 0 and
                         random.uniform(0, 1) < dest_tile_type.spawn_rate)):
                    # NOTE: Comment out the following line to disable encounters
                    self.game_state.initiate_encounter()
                    GameEvents.clear_events()
        else:
            for _ in range(CharacterSprite.get_tile_movement_steps()):
                self.game_state.advance_tick()
