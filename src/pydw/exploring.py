#!/usr/bin/env python

"""Module defining the Exploring game mode."""

import logging
import random
from typing import Optional, cast

import pygame

from generic_utils.point import Point
from pydw.combat_character_state import CombatCharacterState
from pydw.game_dialog import GameDialog, GameDialogSpacing
from pydw.game_dialog_evaluator import GameDialogEvaluator
from pydw.game_map import CharacterSprite
from pydw.game_mode import GameMode
from pydw.game_state_interface import GameStateInterface
from pydw.game_types import DialogType, Direction, OutgoingTransition, Tool
from pydw.npc_state import NpcState
from pygame_utils import game_events
from pygame_utils.audio_player import AudioPlayer

logger = logging.getLogger(__name__)


class Exploring(GameMode):
    """Game mode for exploring, which is the main game loop."""

    def __init__(self, game_state: GameStateInterface) -> None:
        super().__init__(game_state.get_dialog_manager())
        self.game_state = game_state
        self.gde = GameDialogEvaluator(game_state)

        # Flag to throttle how often the block sound is played
        self.first_block_occurred = False

    def game_mode_loop(self) -> None:
        """The game loop for the exploring game mode."""
        map_name = ""
        while self.game_state.is_running:
            # Handle a change in maps
            if map_name != self.game_state.get_map_name():
                map_name = self.game_state.get_map_name()
                self.activate()

            # Handle pending dialog
            pending_dialog = self.game_state.get_pending_dialog()
            if pending_dialog is not None:
                self.gde.dialog_loop(pending_dialog)
                self.game_state.clear_pending_dialog()

            self.process_events()
            self.advance_until_ready_for_more_user_input()

    def activate(self) -> None:
        """Handle a transition in control from one game mode to another by drawing the mode and playing music, if
        any."""
        # Set an appropriate status dialog before the superclass activate is called.
        dm = self.game_state.get_dialog_manager()
        if dm.message_dialog is not None or 0 < len(dm.cascading_dialogs):
            self.dialog_manager.status_dialog = GameDialog.create_exploring_status_dialog(
                self.game_state.get_hero_party()
            )
        else:
            self.dialog_manager.status_dialog = GameDialog.create_persistent_status_dialog(
                self.game_state.get_hero_party()
            )
        super().activate()

    def advance_state(self) -> bool:
        """Update the state of the game mode for one tick (frame) of game time, if applicable for the mode.
        Return a boolean indicating if the state was updated, as state updates need to be followed by
        drawing the updated state to the display."""
        self.game_state.get_game_map().update()
        return True

    def draw_background(self, flip_buffer: bool = False) -> None:
        """Draw the background, which is the map in this game mode."""
        self.game_state.get_game_map().draw()

        # Flip the screen buffer
        if flip_buffer:
            pygame.display.flip()

    def get_music(self) -> Optional[str]:
        """Implementation of GameMode.get_music for this game mode."""
        return self.game_state.get_game_info().maps[self.game_state.get_map_name()].music

    def process_events(self) -> None:
        """Process user input via events off the pygame event queue."""
        # logger.debug("Getting events...")
        events = game_events.get_events(True)

        for event in events:
            # logger.debug("Processing event %s", event)

            if event.type == pygame.QUIT:
                self.game_state.handle_quit(force=True)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state.handle_quit()
                elif event.key == pygame.K_RETURN:
                    AudioPlayer().play_sound("select")
                    self.smart_interactions()
                elif event.key == pygame.K_F1:
                    AudioPlayer().play_sound("select")
                    self.game_state.save(quick_save=True)
                # TODO: Enable to play around with day vs night lighting
                # elif event.key == pygame.K_F2:
                #    self.game_state.get_game_map().set_lighting_mode(is_day=True)
                # elif event.key == pygame.K_F3:
                #    self.game_state.get_game_map().set_lighting_mode(is_day=False)
                else:
                    direction = Direction.get_optional_direction(event.key)
                    if direction is None:
                        logger.debug("Ignoring event %s", event)
                        continue
                    self.game_state.get_hero_party().move(direction)
            else:
                logger.debug("Ignoring event %s", event)
                continue

            # logger.debug("Processed event %s", event)

            # Only process the first supported event
            break

    def smart_interactions(self) -> None:
        """Based on context, pick the most likely desired interaction.
        This bypasses the menu for improved quality of life."""
        npc = self.game_state.get_game_map().get_npc_to_talk_to()
        if npc is not None:
            self.handle_talking(npc)
        elif self.game_state.is_facing_openable_item():
            self.handle_opening()
        else:
            self.menu_loop()

    def advance_until_ready_for_more_user_input(self) -> None:
        """Advance one or more ticks after processing user input until ready to except additional user input."""
        # Clear any queued events
        game_events.clear_events()

        if self.game_state.get_hero_party().is_moving():
            self.handle_moving()
        elif self.game_state.get_hero_party().has_turned():
            # On a direction change, unset first_block_occurred
            # if self.first_block_occurred: logger.debug("Clearing first_block_occurred on direction change")
            self.first_block_occurred = False

            change_of_direction_ticks = max(2, CharacterSprite.get_tile_movement_steps() // 3)
            # logger.debug("Advancing %s ticks", change_of_direction_ticks)
            for _ in range(change_of_direction_ticks):
                self.advance_tick()
        else:
            # When not moving, set the first_block_occurred
            # if not self.first_block_occurred: logger.debug("Setting first_block_occurred on stopping")
            self.first_block_occurred = True

            # logger.debug("Advancing one tick")
            self.advance_tick()

    def handle_talking(self, npc: Optional[NpcState] = None) -> None:
        """Handle a user command to talk"""
        if npc is None:
            npc = self.game_state.get_game_map().get_npc_to_talk_to()
        if npc:
            if npc.npc_info and npc.npc_info.dialog:
                dialog = npc.npc_info.dialog
            else:
                dialog = ["They pay you no mind."]
        else:
            dialog = ["There is no one there."]
        self.gde.dialog_loop(dialog, npc)
        if npc:
            npc.done_talking()

    def handle_opening(self) -> None:
        """Handle a user command to open"""
        self.handle_opening_or_searching(is_opening=True)

    def handle_searching(self) -> None:
        """Handle a user command to search"""
        self.handle_opening_or_searching(is_opening=False)

    def handle_opening_or_searching(self, is_opening: bool) -> None:
        """Helper for handling a user command to open or search, as the two actions are very similar."""
        is_searching = not is_opening
        decorations = self.game_state.get_game_map().get_decorations()
        if is_searching:
            dialog: DialogType = ["[NAME] searched the ground and found nothing."]
        else:
            dialog = ["[NAME] found nothing to open."]
            dest_tile = (
                self.game_state.get_hero_party().members[0].curr_pos_dat_tile
                + self.game_state.get_hero_party().members[0].direction.get_vector()
            )
            decorations += self.game_state.get_game_map().get_decorations(dest_tile)

        for decoration in decorations:
            requires_removal = False

            if decoration.type is not None:
                requires_removal = (
                    decoration.type.remove_with_search
                    or decoration.type.remove_with_open
                    or decoration.type.remove_with_key
                )

                if requires_removal:
                    if (is_searching and decoration.type.remove_with_search) or (
                        is_opening and decoration.type.remove_with_open
                    ):
                        if decoration.type.remove_sound is not None:
                            AudioPlayer().play_sound(decoration.type.remove_sound)
                        self.game_state.remove_decoration(decoration)
                        self.draw()

                        if decoration.dialog is not None:
                            dialog = decoration.dialog
                        else:
                            dialog = []
                        break
                    if decoration.type.remove_with_key:
                        key_item = self.game_state.get_game_info().items["Key"]
                        if (
                            self.game_state.get_hero_party().has_item(key_item.name)
                            and isinstance(key_item, Tool)
                            and key_item.use_dialog is not None
                        ):
                            dialog = [
                                "It is locked. Dost thou desire to open it with a key?",
                                {"Yes": key_item.use_dialog, "No": None},
                            ]
                        else:
                            dialog = ["It is locked."]
                        break

            if not requires_removal and decoration.dialog is not None:
                dialog = decoration.dialog

        self.gde.dialog_loop(dialog)

    def menu_loop(self) -> None:
        """The loop for the exploring menu."""
        dm = self.game_state.get_dialog_manager()
        dm.status_dialog = GameDialog.create_exploring_status_dialog(self.game_state.get_hero_party())
        dm.add_cascading_dialog(GameDialog.create_exploring_menu())
        while 0 < len(dm.cascading_dialogs):
            menu_result = self.gde.get_menu_result(dm.cascading_dialogs[-1])
            logger.debug("menu_result = %s", menu_result)
            if menu_result == "TALK":
                dm.remove_cascading_dialog()
                self.handle_talking()
            elif menu_result == "SEARCH":
                dm.remove_cascading_dialog()
                self.handle_searching()
            elif menu_result == "OPEN":
                dm.remove_cascading_dialog()
                self.handle_opening()
            elif menu_result == "STAIRS":
                dm.remove_cascading_dialog()
                if not self.make_map_transition(self.get_point_transition()):
                    self.gde.dialog_loop("There are no stairs here.")
            elif menu_result == "STATUS":
                dm.add_cascading_dialog(GameDialog.create_full_status_dialog(self.game_state.get_hero_party()))
                if self.gde.wait_for_acknowledgement():
                    # Only removing two dialogs when we exit out of the status dialog with acceptance
                    dm.remove_cascading_dialog(flip_buffer=False)
                dm.remove_cascading_dialog()
            elif menu_result == "SPELL":
                # Not removing the menu dialog when done in the spell menu.
                self.spell_submenu_loop()
            elif menu_result == "ITEM":
                # Not removing the menu dialog when done in the item menu.
                self.item_submenu_loop()
            elif menu_result is not None:
                logger.error("ERROR: Unsupported menu_result = %s", menu_result)
            elif menu_result is None:
                dm.remove_cascading_dialog()
        dm.status_dialog = GameDialog.create_persistent_status_dialog(self.game_state.get_hero_party())

    def item_submenu_loop(self) -> None:
        """The loop for the exploring menu's item submenu."""
        dm = self.game_state.get_dialog_manager()
        # TODO: Need to choose the hero to use an item
        actor = self.game_state.get_hero_party().main_character
        self.gde.set_actor(actor)
        item_cols = 2
        item_row_data = actor.get_item_row_data()
        if len(item_row_data) == 0:
            self.gde.dialog_loop("Thou dost not have any items.")
        else:
            item_result: Optional[str] = None
            while 0 < len(dm.cascading_dialogs):
                item_row_data = actor.get_item_row_data()
                if "ITEMS" == dm.cascading_dialogs[-1].title:
                    dm.remove_cascading_dialog(flip_buffer=False)
                if len(item_row_data) == 0:
                    break
                dm.add_cascading_dialog(
                    GameDialog.create_menu_dialog(
                        Point(
                            -1,
                            dm.cascading_dialogs[-1].pos_tile.y + dm.cascading_dialogs[-1].size_tiles.h + 1,
                        ),
                        None,
                        "ITEMS",
                        item_row_data,
                        item_cols,
                        GameDialogSpacing.OUTSIDE_JUSTIFIED,
                    ),
                    item_result,
                )
                item_result = self.gde.get_menu_result(dm.cascading_dialogs[-1])
                logger.debug("item_result = %s", item_result)

                if item_result is None:
                    dm.remove_cascading_dialog()
                    break

                item_options = self.game_state.get_hero_party().main_character.get_item_options(item_result)
                if len(item_options) == 0:
                    self.gde.dialog_loop("[ACTOR] studied the object and was confounded by it.")
                else:
                    dm.add_cascading_dialog(
                        GameDialog.create_menu_dialog(
                            Point(
                                -1,
                                dm.cascading_dialogs[-1].pos_tile.y + dm.cascading_dialogs[-1].size_tiles.h + 1,
                            ),
                            None,
                            None,
                            item_options,
                            len(item_options),
                        )
                    )
                    action_result = self.gde.get_menu_result(dm.cascading_dialogs[-1])
                    logger.debug("action_result = %s", action_result)
                    if action_result == "DROP":
                        self.dialog_manager.add_cascading_dialog(
                            GameDialog.create_yes_no_menu(
                                Point(
                                    -1,
                                    dm.cascading_dialogs[-1].pos_tile.y + dm.cascading_dialogs[-1].size_tiles.h + 1,
                                ),
                                "Do you really want to drop the object?",
                            )
                        )
                        confirm_result = self.gde.get_menu_result(dm.cascading_dialogs[-1])
                        if confirm_result is not None and confirm_result == "YES":
                            self.game_state.get_hero_party().lose_item(item_result)
                        dm.remove_cascading_dialog(False)
                    elif action_result == "EQUIP":
                        self.game_state.get_hero_party().main_character.equip_item(item_result)
                    elif action_result == "UNEQUIP":
                        self.game_state.get_hero_party().main_character.unequip_item(item_result)
                    elif action_result == "USE":
                        item = self.game_state.get_hero_party().get_item(item_result)
                        if item is not None and isinstance(item, Tool) and item.use_dialog is not None:
                            # TODO: Depending on the item may need to select the target(s)
                            targets = [actor]
                            self.gde.set_targets(cast(list[CombatCharacterState], targets))
                            self.gde.dialog_loop(item.use_dialog)
                        else:
                            self.gde.dialog_loop("[ACTOR] studied the object and was confounded by it.")
                        dm.clear_cascading_dialogs()
                    dm.remove_cascading_dialog()

        # Restore the default actor and targets after using the item
        self.gde.restore_default_actor_and_targets()

    def spell_submenu_loop(self) -> None:
        """The loop for the exploring menu's spell submenu."""
        dm = self.game_state.get_dialog_manager()
        # TODO: Need to choose the actor (spellcaster)
        actor = self.game_state.get_hero_party().main_character
        self.gde.set_actor(actor)
        available_spell_names = actor.get_available_spell_names()
        if len(available_spell_names) == 0:
            self.gde.dialog_loop("Thou hast not yet learned any spells.")
        else:
            dm.add_cascading_dialog(
                GameDialog.create_menu_dialog(
                    Point(
                        -1,
                        dm.cascading_dialogs[-1].pos_tile.y + dm.cascading_dialogs[-1].size_tiles.h + 1,
                    ),
                    None,
                    "SPELLS",
                    available_spell_names,
                    1,
                )
            )
            while 0 < len(dm.cascading_dialogs):
                menu_result = self.gde.get_menu_result(dm.cascading_dialogs[-1])
                logger.debug("menu_result = %s", menu_result)
                if menu_result is None:
                    break

                spell = self.game_state.get_game_info().spells[menu_result]
                if actor.mp >= spell.mp:
                    # TODO: Depending on the spell may need to select the target(s)
                    targets = [actor]
                    actor.mp -= spell.mp
                    self.gde.set_targets(cast(list[CombatCharacterState], targets))
                    self.gde.dialog_loop(spell.use_dialog)

                    dm.add_status_dialog(GameDialog.create_exploring_status_dialog(self.game_state.get_hero_party()))
                    dm.clear_cascading_dialogs()
                else:
                    self.gde.dialog_loop("Thou dost not have enough magic to cast the spell.")

            dm.remove_cascading_dialog()

        # Restore the default actor and targets after calling the spell
        self.gde.restore_default_actor_and_targets()

    def handle_moving(self) -> None:
        """Handle a delta between the destination and current position. This includes determining whether the movement
        is allowed, drawing the movement to the display, and applying any consequences of the movement.  Possible
        consequences include a transition to another map, damage applied from the destination tile (which could cause
        a character to die), applying healing over time effects, status changes from changes in health, wearing off of
        timed effects, and initiating combat encounters."""
        transition: Optional[OutgoingTransition] = None

        # Determine the destination tile and pixel count for the scroll
        hero_dest_dat_tile = self.game_state.get_hero_party().members[0].dest_pos_dat_tile

        # Validate if the destination tile is navigable
        movement_allowed = self.game_state.get_game_map().can_move_to_tile(hero_dest_dat_tile)

        # Play a walking sound or bump sound based on whether the movement was allowed
        movement_hp_penalty = 0
        if movement_allowed:
            # On allowed movement, unset first_block_occurred
            # if self.first_block_occurred: logger.debug("Clearing first_block_occurred on allowed movement")
            self.first_block_occurred = False

            dest_tile_type = self.game_state.get_tile_info(hero_dest_dat_tile)

            for hero_idx in range(1, len(self.game_state.get_hero_party().members)):
                hero = self.game_state.get_hero_party().members[hero_idx]
                hero.dest_pos_dat_tile = self.game_state.get_hero_party().members[hero_idx - 1].curr_pos_dat_tile
                if hero.curr_pos_dat_tile != hero.dest_pos_dat_tile:
                    hero.direction = Direction.get_direction(hero.dest_pos_dat_tile - hero.curr_pos_dat_tile)

            # Determine if the movement should result in a transition to another map
            map_size = self.game_state.get_game_map().size()
            leaving_transition = self.game_state.get_game_info().maps[self.game_state.get_map_name()].leaving_transition
            if leaving_transition is not None:
                if leaving_transition.bounding_box:
                    if not leaving_transition.bounding_box.collidepoint(hero_dest_dat_tile.get_as_int_tuple()):
                        transition = leaving_transition
                elif (
                    hero_dest_dat_tile[0] == 0
                    or hero_dest_dat_tile[1] == 0
                    or hero_dest_dat_tile[0] == map_size[0] - 1
                    or hero_dest_dat_tile[1] == map_size[1] - 1
                ):
                    transition = leaving_transition
            if transition is None:
                logger.info("Check for transitions at %s", hero_dest_dat_tile)

                # See if this tile has any associated transitions
                transition = self.get_point_transition(hero_dest_dat_tile, filter_to_automatic_transitions=True)
            else:
                # Map leaving transition
                logger.debug("Leaving map %s", self.game_state.get_map_name())

            # Check for tile penalty effects
            if dest_tile_type.hp_penalty > 0 and not self.game_state.get_hero_party().is_ignoring_tile_penalties():
                movement_hp_penalty = dest_tile_type.hp_penalty

            # Check for any status effect changes or healing to occur as the party moves
            dialog_from_inc_step_count = self.game_state.get_hero_party().inc_step_counter()

            # Apply health penalty
            for hero in self.game_state.get_hero_party().members:
                if not hero.is_ignoring_tile_penalties():
                    hero.hp = max(0, hero.hp - movement_hp_penalty)

            first_frame = True
            while self.game_state.get_hero_party().is_moving():
                # Redraws the characters when movement_allowed is True
                # logger.debug("Advancing one tick")
                if movement_allowed and movement_hp_penalty > 0 and first_frame:
                    AudioPlayer().play_sound("hit_lvl_1")
                    flicker_surface = pygame.surface.Surface(self.game_state.screen.get_size())
                    flicker_surface.fill("red")
                    flicker_surface.set_alpha(128)
                    self.advance_state()
                    self.draw(flip_buffer=False)
                    self.game_state.screen.blit(flicker_surface, (0, 0))
                    self.advance_time(flip_buffer=True)
                    first_frame = False
                elif dialog_from_inc_step_count is not None:
                    self.gde.dialog_loop(dialog_from_inc_step_count)
                    dialog_from_inc_step_count = None
                else:
                    # Update the status dialog
                    self.dialog_manager.status_dialog = GameDialog.create_persistent_status_dialog(
                        self.game_state.get_hero_party()
                    )
                    self.advance_tick()

            # Check for player death or combat at the destination
            if not self.game_state.get_hero_party().has_surviving_members():
                self.game_state.handle_death()
            elif not self.make_map_transition(transition):
                # At destination - now determine if an encounter should start
                # Check for special monster encounters as well as random monsters
                if self.game_state.get_special_monster() is not None or (
                    len(self.game_state.get_tile_monsters()) > 0 and random.uniform(0, 1) < dest_tile_type.spawn_rate
                ):
                    # NOTE: Comment out the following line to disable encounters
                    self.game_state.initiate_encounter()
                    game_events.clear_events()
        else:
            # Reset the destination for each member of the hero party back to the current position
            self.game_state.get_hero_party().members[0].dest_pos_dat_tile = (
                self.game_state.get_hero_party().members[0].curr_pos_dat_tile
            )

            # Handle being blocked by terrain.  Use first_block_occurred in order to forgive the first occurrence as
            # the blocked sound effect was otherwise a bit excessive.
            if self.first_block_occurred:
                # logger.debug("Successive block - playing blocked sound")
                AudioPlayer().play_sound("blocked")

            # On blocked movement, set first_block_occurred
            # if not self.first_block_occurred: logger.debug("First block - not playing blocked sound")
            self.first_block_occurred = True

            # On being blocked, advance the same number of frames as moving.
            # logger.debug("Advancing %s ticks", CharacterSprite.get_tile_movement_steps())
            for _ in range(CharacterSprite.get_tile_movement_steps()):
                self.advance_tick()

    def make_map_transition(self, transition: Optional[OutgoingTransition]) -> bool:
        """Return a boolean indicating if a transition was made."""
        if transition is None:
            return False

        src_map = self.game_state.get_game_info().maps[self.game_state.get_map_name()]
        dest_map = self.game_state.get_game_info().maps[transition.dest_map]

        # Find the destination transition corresponding to this transition
        if transition.dest_name is None:
            try:
                dest_transition = dest_map.transitions_by_map[self.game_state.get_map_name()]
            except KeyError:
                logger.error("Failed to find destination transition by dest_map")
                return False
        else:
            try:
                dest_transition = dest_map.transitions_by_map_and_name[self.game_state.get_map_name()][
                    transition.dest_name
                ]
            except KeyError:
                try:
                    dest_transition = dest_map.transitions_by_name[transition.dest_name]
                except KeyError:
                    logger.error("Failed to find destination transition by dest_name")
                    return False

        # If transitioning from outside to inside, save off last outside position
        if src_map.is_outside and not dest_map.is_outside:
            self.game_state.get_hero_party().set_last_outside_pos(
                self.game_state.get_map_name(),
                self.game_state.get_hero_party().get_curr_pos_dat_tile(),
                self.game_state.get_hero_party().get_direction(),
            )

        # Make the transition and draw the map
        AudioPlayer().play_sound("walk_away")
        self.game_state.get_hero_party().set_pos(dest_transition.point, dest_transition.dir)
        self.game_state.set_map(transition.dest_map, respawn_decorations=transition.respawn_decorations)
        self.draw(flip_buffer=True)

        # Slight pause on a map transition
        pygame.time.wait(250)

        return True

    def get_point_transition(
        self,
        tile: Optional[Point] = None,
        filter_to_automatic_transitions: bool = False,
    ) -> Optional[OutgoingTransition]:
        """Find point transitions for either the specified point or the current position of the player character.
        If filter_to_automatic_transitions is true, only look for automatic point transitions"""
        if tile is None:
            tile = self.game_state.get_hero_party().get_curr_pos_dat_tile()
        for point_transition in self.game_state.get_game_info().maps[self.game_state.get_map_name()].point_transitions:
            if point_transition.point == tile and self.game_state.check_progress_markers(
                point_transition.progress_marker,
                point_transition.inverse_progress_marker,
            ):
                if filter_to_automatic_transitions:
                    if point_transition.is_automatic is None and not self.game_state.is_light_restricted():
                        # By default, make transitions manual in dark places
                        return point_transition
                    if point_transition.is_automatic:
                        return point_transition
                else:
                    return point_transition
        return None
