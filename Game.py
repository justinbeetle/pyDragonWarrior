#!/usr/bin/env python

from typing import cast, List, Optional, Union

import pygame
import random

from AudioPlayer import AudioPlayer
from CombatCharacterState import CombatCharacterState
from GameState import GameState
from GameDialog import GameDialog, GameDialogSpacing
from GameDialogEvaluator import GameDialogEvaluator
from GameTypes import Direction, DialogType, LeavingTransition, PointTransition, Tool
import GameEvents
from Point import Point
import SurfaceEffects


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
        self.gde = GameDialogEvaluator(self.game_state.game_info, self.game_state)
        GameDialog.static_init(self.game_state.win_size_tiles, tile_size_pixels)

    def run_game_loop(self) -> None:
        self.game_state.is_running = True
        self.title_screen_loop()
        self.exploring_loop()

    def title_screen_loop(self) -> None:
        # TODO: Implement
        pass

    def exploring_loop(self) -> None:
        pygame.key.set_repeat(10, 10)
        map_name = ''

        while self.game_state.is_running:

            # Generate the map state a mode or map change
            if (map_name != self.game_state.map_state.name):
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
                    self.game_state.handle_quit()
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
                            # print( 'item_result =', item_result, flush=True )

                            if item_result is not None:
                                item_options = self.game_state.hero_party.main_character.get_item_options(item_result)
                                if len(item_row_data) == 0:
                                    self.gde.dialog_loop('[ACTOR] studied the object and was confounded by it.')
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
                                            self.gde.dialog_loop('[ACTOR] struggled with the object before giving up.')

                        # Restore the default actor and targets after using the item
                        self.gde.restore_default_actor_and_targets()

                    elif menu_result is not None:
                        print('ERROR: Unsupported menu_result =', menu_result, flush=True)

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
                # TODO: Uncomment following statement to disable coordinate logging
                print('Check for transitions at', hero_dest_dat_tile, flush=True)
                transition = self.game_state.get_point_transition(hero_dest_dat_tile)

            # Check for tile penalty effects
            if dest_tile_type.hp_penalty > 0 and not self.game_state.hero_party.is_ignoring_tile_penalties():
                audio_player.play_sound('walking.wav')
                movement_hp_penalty = dest_tile_type.hp_penalty

            # Check for any status effect changes or healing to occur as the party moves
            self.game_state.hero_party.inc_step_counter()
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
    win_size_pixels = None  # Point(1280, 960) # TODO: Get good size for system from OS or switch to full screen
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
