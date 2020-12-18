#!/usr/bin/env python

from typing import cast, List, Optional, Union

# import datetime
import glob
import os
import pygame
import random

from AudioPlayer import AudioPlayer
from CombatCharacterState import CombatCharacterState
import GameEvents
from GameState import GameState
from GameDialog import GameDialog, GameDialogSpacing
from GameDialogEvaluator import GameDialogEvaluator
from GameTypes import Direction, DialogType, LeavingTransition, PointTransition, Tool
from Point import Point
import SurfaceEffects


class Game:
    def __init__(self,
                 base_path: str,
                 game_xml_path: str,
                 desired_win_size_pixels: Optional[Point],
                 tile_size_pixels: int) -> None:
        self.game_state = GameState(base_path,
                                    game_xml_path,
                                    desired_win_size_pixels,
                                    tile_size_pixels)
        self.gde = GameDialogEvaluator(self.game_state.game_info, self.game_state)
        self.gde.update_default_dialog_font_color()
        GameDialog.static_init(self.game_state.win_size_tiles, tile_size_pixels)

    def run_game_loop(self, pc_name_or_file_name: Optional[str] = None) -> None:
        self.game_state.is_running = True
        self.title_screen_loop(pc_name_or_file_name)
        self.exploring_loop()

    def title_screen_loop(self, pc_name_or_file_name: Optional[str] = None) -> None:
        #self.game_state.load(pc_name_or_file_name)

        # Play title music and display title screen
        AudioPlayer().play_music(self.game_state.game_info.title_music)
        title_image_size_px = Point(self.game_state.game_info.title_image.get_size())
        title_image_size_px *= max(1, int(min(self.game_state.get_win_size_pixels().w * 0.8 / title_image_size_px.w,
                                              self.game_state.get_win_size_pixels().h * 0.8 / title_image_size_px.h)))
        title_image = pygame.transform.scale(self.game_state.game_info.title_image, title_image_size_px)
        title_image_dest_px = Point(
            (self.game_state.get_win_size_pixels().w - title_image_size_px.w) / 2,
            self.game_state.get_win_size_pixels().h / 2 - title_image_size_px.h)
        self.game_state.screen.fill(pygame.Color('black'))
        self.game_state.screen.blit(title_image, title_image_dest_px)
        pygame.display.flip()

        # Wait for user input - any key press
        while self.game_state.is_running:
            waiting_for_user_input = True
            for event in GameEvents.get_events():
                if event.type == pygame.QUIT:
                    self.game_state.handle_quit(force=True)
                elif event.type == pygame.KEYDOWN:
                    waiting_for_user_input = False
                    break
            if waiting_for_user_input:
                pygame.time.Clock().tick(40)
            else:
                break

        # Prompt user for new game or to load a saved game
        if pc_name_or_file_name is None:
            # Get a list of the saved games
            saved_game_files = glob.glob(os.path.join(self.game_state.game_info.saves_path, '*.xml'))
            saved_games = []
            for saved_game_file in saved_game_files:
                saved_games.append(os.path.basename(saved_game_file)[:-4])

            menu_options = []
            if 0 < len(saved_games):
                menu_options.append('Continue a Quest')
            menu_options.append('Begin a Quest')

            while self.game_state.is_running:
                message_dialog = GameDialog.create_message_dialog()
                message_dialog.add_menu_prompt(menu_options, 1)
                message_dialog.blit(self.game_state.screen, True)
                menu_result = self.gde.get_menu_result(message_dialog)
                print('menu_result =', menu_result, flush=True)
                if menu_result == 'Continue a Quest':
                    message_dialog.clear()
                    message_dialog.add_menu_prompt(saved_games, 1)
                    message_dialog.blit(self.game_state.screen, True)
                    menu_result = self.gde.get_menu_result(message_dialog)
                    if menu_result is not None:
                        pc_name_or_file_name = menu_result
                        break
                elif menu_result == 'Begin a Quest':
                    message_dialog.clear()
                    pc_name_or_file_name = self.gde.wait_for_user_input(message_dialog,  'What is your name?')[0]

                    if pc_name_or_file_name in saved_games:
                        message_dialog.add_message('Thou hast already started a quest.  Dost thou desire to start over?')
                        message_dialog.add_menu_prompt(['Yes', 'No'], 2, GameDialogSpacing.SPACERS)
                        message_dialog.blit(self.game_state.screen, True)
                        menu_result = self.gde.get_menu_result(message_dialog)
                        if menu_result == 'Yes':
                            # Delete the existing save game for this user after archiving it off
                            saved_game_file = os.path.join(self.game_state.game_info.saves_path,
                                                           pc_name_or_file_name + '.xml')
                            self.game_state.archive_saved_game_file(saved_game_file, 'deleted')
                            os.remove(saved_game_file)
                        elif menu_result != 'No':
                            continue
                    break

        # Load the saved game
        self.game_state.load(pc_name_or_file_name)
        self.gde.refresh_game_state()

    def exploring_loop(self) -> None:
        map_name = ''

        while self.game_state.is_running:

            # Generate the map state a mode or map change
            if map_name != self.game_state.map_state.name:
                map_name = self.game_state.map_state.name

                # Play the music for the map
                AudioPlayer().play_music(self.game_state.game_info.maps[self.game_state.map_state.name].music)

                # Bounds checking to ensure a valid hero/center position
                self.game_state.bounds_check_pc_position()

                # Draw the map to the screen
                self.game_state.draw_map()

            if self.game_state.pending_dialog is not None:
                self.gde.dialog_loop(self.game_state.pending_dialog)
                self.game_state.pending_dialog = None

            # Process events
            # print(datetime.datetime.now(), 'exploring_loop:  Getting events...', flush=True)
            events = GameEvents.get_events(True)

            for event in events:
                # print('exploring_loop:  Processing event', event, flush=True)
                moving = False
                menu = False
                talking = False
                searching = False
                pc_dir_old = self.game_state.hero_party.members[0].direction

                if event.type == pygame.QUIT:
                    self.game_state.handle_quit(force=True)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.handle_quit()
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
                    elif event.key == pygame.K_F1:
                        self.game_state.save(quick_save=True)
                else:
                    # print('exploring_loop:  Ignoring event', event, flush=True)
                    continue

                # print(datetime.datetime.now(), 'exploring_loop:  Processed event', event, flush=True)

                # Clear queued events upon launching the menu
                GameEvents.clear_events()
                events = []

                # Allow a change of direction without moving
                if pc_dir_old != self.game_state.hero_party.members[0].direction:
                    # print('Change of direction detected (advancing four ticks)', flush=True)
                    moving = False
                    self.game_state.advance_tick()
                    self.game_state.advance_tick()
                    self.game_state.advance_tick()
                    self.game_state.advance_tick()

                if menu:

                    GameDialog.create_exploring_status_dialog(
                        self.game_state.hero_party).blit(self.game_state.screen, False)
                    menu_dialog = GameDialog.create_exploring_menu()
                    menu_dialog.blit(self.game_state.screen, True)
                    menu_result = self.gde.get_menu_result(menu_dialog)
                    # print('menu_result =', menu_result, flush=True)
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
                        item_row_data = actor.get_item_row_data()
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
                                and decoration.type.remove_with_search):
                            if decoration.type.remove_sound is not None:
                                AudioPlayer().play_sound(decoration.type.remove_sound)
                            self.game_state.remove_decoration(decoration)

                        if decoration.dialog is not None:
                            dialog = decoration.dialog
                            break

                    self.gde.dialog_loop(dialog)

                if moving:
                    self.scroll_tile()

            # print('advancing one tick in exploring_loop', flush=True)
            self.game_state.advance_tick()

    def scroll_tile(self) -> None:

        transition: Optional[Union[LeavingTransition, PointTransition]] = None

        map_image_rect = self.game_state.get_map_image_rect()
        orig_map_image_rect = self.game_state.get_map_image_rect()
        tile_move_steps = self.game_state.game_info.tile_size_pixels // self.game_state.game_info.image_px_step_size

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
                # TODO: Uncomment following statement to disable coordinate logging
                # print('Check for transitions at', hero_dest_dat_tile, flush=True)
                transition = self.game_state.get_point_transition(hero_dest_dat_tile)

            # Check for tile penalty effects
            if dest_tile_type.hp_penalty > 0 and not self.game_state.hero_party.is_ignoring_tile_penalties():
                audio_player.play_sound('walking.wav')
                movement_hp_penalty = dest_tile_type.hp_penalty

            # Check for any status effect changes or healing to occur as the party moves
            has_low_health = self.game_state.hero_party.has_low_health()
            self.game_state.hero_party.inc_step_counter()
            if has_low_health != self.game_state.hero_party.has_low_health():
                # Change default dialog font color
                self.gde.update_default_dialog_font_color()

                # Redraw the map
                self.game_state.draw_map(True)

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
                                           1.0,
                                           self.game_state.game_info.image_px_step_size)
                self.game_state.hero_party.members[0].curr_pos_offset_img_px = Point(
                    map_image_rect.x - orig_map_image_rect.x, map_image_rect.y - orig_map_image_rect.y)
                for hero in self.game_state.hero_party.members[1:]:
                    if hero.curr_pos_dat_tile != hero.dest_pos_dat_tile:
                        hero.curr_pos_offset_img_px = hero.direction.get_vector() * \
                                                      self.game_state.game_info.image_px_step_size * (x+1)

                if self.game_state.is_light_restricted():
                    self.game_state.draw_map(False)

                if movement_hp_penalty > 0:
                    if x == tile_move_steps - 2:
                        flicker_surface = pygame.surface.Surface(self.game_state.screen.get_size())
                        flicker_surface.fill(pygame.Color('red'))
                        flicker_surface.set_alpha(128)
                        self.game_state.screen.blit(flicker_surface, (0, 0))
                    elif x == tile_move_steps - 1:
                        self.game_state.draw_map(False)

            # Redraws the characters when movement_allowed is True
            # print('advancing one tick in scroll_tile', flush=True)
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
            self.gde.update_default_dialog_font_color()
            self.game_state.handle_death()

            # At destination - now determine if an encounter should start
            if not self.game_state.make_map_transition(transition):
                # Check for special monster encounters
                if (self.game_state.get_special_monster() is not None or
                        (len(self.game_state.get_tile_monsters()) > 0 and
                         random.uniform(0, 1) < dest_tile_type.spawn_rate)):
                    self.game_state.initiate_encounter()


def main() -> None:
    import sys
    import os

    pygame.init()
    pygame.mouse.set_visible(False)
    GameEvents.setup_joystick()

    saved_game_file = None
    if len(sys.argv) > 1:
        saved_game_file = sys.argv[1]

    # Initialize the game
    base_path = os.path.split(os.path.abspath(__file__))[0]
    game_xml_path = os.path.join(base_path, 'game.xml')
    win_size_pixels = None  # Point(2560, 1340)
    tile_size_pixels = 20 * 3
    game = Game(base_path, game_xml_path, win_size_pixels, tile_size_pixels)

    # Run the game
    game.run_game_loop(saved_game_file)

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
