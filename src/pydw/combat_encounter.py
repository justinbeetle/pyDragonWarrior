#!/usr/bin/env python

from typing import cast, List, Optional, Tuple, Union

import random

import pygame

from generic_utils.point import Point

from pygame_utils.audio_player import AudioPlayer
import pygame_utils.game_events as GameEvents

from pydw.combat_character_state import CombatCharacterState
from pydw.combat_encounter_interface import CombatEncounterInterface
from pydw.game_dialog import GameDialog, GameDialogSpacing
from pydw.game_dialog_evaluator import GameDialogEvaluator
from pydw.game_info import GameInfo
from pydw.game_state_interface import GameStateInterface
from pydw.game_types import (
    DialogAction,
    DialogActionEnum,
    DialogType,
    EncounterBackground,
    GameTypes,
    MonsterAction,
    MonsterInfo,
    Problem,
    SpecialMonster,
    TargetTypeEnum,
    Tool,
)
from pydw.hero_party import HeroParty
from pydw.hero_state import HeroState
from pydw.monster_party import MonsterParty
from pydw.monster_state import MonsterState


class CombatEncounter(CombatEncounterInterface):
    MONSTER_SPACING_PIXELS = -5
    DAMAGE_FLICKER_PIXELS = 4
    default_encounter_music = ""

    @staticmethod
    def static_init(default_encounter_music: str) -> None:
        CombatEncounter.default_encounter_music = default_encounter_music

    def __init__(
        self,
        game_info: GameInfo,
        game_state: GameStateInterface,
        monster_party: MonsterParty,
        encounter_background: EncounterBackground,
        message_dialog: Optional[GameDialog] = None,
        approach_dialog: Optional[DialogType] = None,
        victory_dialog: Optional[DialogType] = None,
        run_away_dialog: Optional[DialogType] = None,
        encounter_music: Optional[str] = None,
    ) -> None:
        self.is_first_turn = True
        self.game_info = game_info
        self.game_state = game_state
        self.hero_party = game_state.get_hero_party()
        self.monster_party = monster_party
        self.approach_dialog = approach_dialog
        self.victory_dialog = victory_dialog
        self.run_away_dialog = run_away_dialog

        if self.game_state.is_light_restricted():
            self.game_state.screen.fill("black")
        else:
            self.game_state.draw_map(flip_buffer=False, draw_status=False)
        self.background_image = game_state.screen.copy()

        if message_dialog is not None:
            self.message_dialog = message_dialog
            self.message_dialog.add_message("")
        else:
            self.message_dialog = GameDialog.create_message_dialog()
        self.gde = GameDialogEvaluator(game_info, game_state, self)
        self.gde.update_status_dialog(message_dialog=self.message_dialog)

        if encounter_music is not None:
            self.encounter_music = encounter_music
        else:
            self.encounter_music = CombatEncounter.default_encounter_music

        self.hero_party.clear_combat_status_affects()

        # Scale the encounter image
        # Pixelize the encounter backgrounds so they better fit with the pixelized graphics of the game
        pixelize_factor = 5
        encounter_image_size_px = Point(encounter_background.image.get_size())
        encounter_image_size_px *= min(
            self.game_state.get_win_size_pixels().w * 0.6 / encounter_image_size_px.w,
            self.game_state.get_win_size_pixels().h * 0.4 / encounter_image_size_px.h,
        )
        encounter_image_size_px = (
            encounter_image_size_px // pixelize_factor * pixelize_factor
        )
        self.encounter_image = pygame.transform.scale(
            pygame.transform.smoothscale(
                encounter_background.image,
                (encounter_image_size_px // pixelize_factor).get_as_int_tuple(),
            ),
            encounter_image_size_px.get_as_int_tuple(),
        )

    def encounter_loop(self) -> None:
        # Start encounter music
        AudioPlayer().play_music(self.encounter_music, self.encounter_music)

        # Phase in the encounter background
        self.render_encounter_background_phase_in()

        # Clear event queue
        GameEvents.clear_events()

        # Add the approach dialog
        if self.approach_dialog is not None:
            self.gde.traverse_dialog(self.message_dialog, self.approach_dialog, depth=1)
        else:
            self.add_message(self.monster_party.get_default_approach_dialog())

        # Clear the event queue and wait for user acknowledgement
        GameEvents.clear_events()

        # Check if monsters run away at the start of the encounter
        last_turn_was_monster_turn = False
        for monster in self.monster_party.members:
            if monster.is_still_in_combat():
                if monster.should_run_away(self.hero_party.main_character):
                    last_turn_was_monster_turn = True
                    monster.has_run_away = True
                    AudioPlayer().play_sound("run_away")
                    self.add_message(monster.get_name() + " is running away.")
                    self.render_monsters()

                    # Wait for acknowledgement if all monsters run away
                    if not self.still_in_encounter():
                        self.wait_for_acknowledgement()

        # Iterate through turns in the encounter until the encounter ends
        while self.still_in_encounter():
            for combatant in self.get_turn_order():
                if combatant.is_still_in_combat():
                    if isinstance(combatant, MonsterState):
                        if last_turn_was_monster_turn:
                            self.wait_for_acknowledgement()
                        last_turn_was_monster_turn = True
                        self.execute_monster_turn(combatant)
                    elif isinstance(combatant, HeroState):
                        last_turn_was_monster_turn = False
                        self.execute_player_turn(combatant)
                    if not self.still_in_encounter():
                        break

        # Handle the outcome of the encounter
        AudioPlayer().stop_music()
        if self.hero_party.has_surviving_members():
            if self.hero_party.is_still_in_combat():
                self.handle_victory()
            elif self.run_away_dialog is not None:
                self.gde.traverse_dialog(self.message_dialog, self.run_away_dialog)
        else:
            self.game_state.handle_death(self.message_dialog)

        # Clear combat status effects now that combat is over
        self.hero_party.clear_combat_status_affects()

        # Wait for final acknowledgement
        self.wait_for_acknowledgement()

        # Restore initial background image
        self.game_state.screen.blit(self.background_image, (0, 0))

        # Call game_state.draw_map but manually flip the buffer for the case where this method is a mock
        self.game_state.draw_map(False, draw_combat=False)
        pygame.display.flip()

    def render_encounter_background_phase_in(self) -> None:
        clock = pygame.time.Clock()
        for percent in range(5, 100, 5):
            self.render_encounter_background(True, percent)
            GameDialog.create_encounter_status_dialog(self.hero_party).blit(
                self.game_state.screen
            )
            clock.tick(40)
            pygame.display.flip()

        # Final render to drop to complete the background and drop in the monsters
        self.render_monsters()

    def render_encounter_background(
        self, render_background: bool = True, percent: int = 100
    ) -> Tuple[Point, Point]:
        # Determine the size and screen position for the full background image
        encounter_image_size_px = Point(self.encounter_image.get_size())
        encounter_image_dest_px = Point(
            (self.game_state.get_win_size_pixels().w - encounter_image_size_px.w) / 2,
            self.message_dialog.pos_tile.y * self.game_info.tile_size_pixels
            - encounter_image_size_px.h
            + CombatEncounter.DAMAGE_FLICKER_PIXELS,
        )

        # Determine what subset of the encounter background to render based on the specified percent
        encounter_image_rect = self.encounter_image.get_rect()
        encounter_image_screen_rect = encounter_image_rect.move(encounter_image_dest_px)
        if percent < 100:
            inflate_pixels = encounter_image_size_px * (percent / 100 - 1)
            encounter_image_rect.inflate_ip(inflate_pixels)
            encounter_image_screen_rect.inflate_ip(inflate_pixels)

        # Draw the background image, then the border, then the encounter image
        if render_background:
            self.game_state.screen.blit(self.background_image, (0, 0))
        outside_border_width = 4
        pygame.draw.rect(
            self.game_state.screen,
            "black",
            encounter_image_screen_rect.inflate(
                outside_border_width, outside_border_width
            ),
        )
        self.game_state.screen.blit(
            self.encounter_image, encounter_image_screen_rect, encounter_image_rect
        )

        # Return the size and screen position for the full background image - they are used in render_monsters
        return encounter_image_size_px, encounter_image_dest_px

    def render_monsters(
        self,
        flicker_image_monsters: Optional[List[CombatCharacterState]] = None,
        force_display_monsters: Optional[List[CombatCharacterState]] = None,
        render_background: bool = True,
        render_dialogs: bool = True,
        flicker_color: pygame.Color = pygame.Color("red"),
    ) -> None:
        if flicker_image_monsters is None:
            flicker_image_monsters = []
        if force_display_monsters is None:
            force_display_monsters = []

        # Render the encounter background
        (
            encounter_image_size_px,
            encounter_image_dest_px,
        ) = self.render_encounter_background(render_background)

        # Render the monsters
        monster_width_px = CombatEncounter.MONSTER_SPACING_PIXELS * (
            len(self.monster_party.members) - 1
        )
        for monster in self.monster_party.members:
            monster_width_px += monster.monster_info.image.get_width()
        monster_pos_x = (self.game_state.get_win_size_pixels().x - monster_width_px) / 2
        for monster in self.monster_party.members:
            if monster.is_still_in_combat() or monster in force_display_monsters:
                if monster in flicker_image_monsters:
                    monster_image = monster.monster_info.image.copy()
                    monster_image.fill("black", special_flags=pygame.BLEND_RGB_MULT)
                    monster_image.fill(
                        flicker_color, special_flags=pygame.BLEND_RGB_ADD
                    )
                else:
                    monster_image = monster.monster_info.image
                monster_image_dest_px = Point(
                    monster_pos_x,
                    encounter_image_dest_px.y
                    + encounter_image_size_px.y
                    - monster.monster_info.image.get_height()
                    - self.game_info.tile_size_pixels,
                )
                self.game_state.screen.blit(monster_image, monster_image_dest_px)

            monster_pos_x += (
                CombatEncounter.MONSTER_SPACING_PIXELS
                + monster.monster_info.image.get_width()
            )

        # Render the dialogs
        if render_dialogs:
            self.message_dialog.blit(self.game_state.screen)
            self.gde.update_status_dialog()

    def render_damage_to_targets(self, targets: List[CombatCharacterState]) -> None:
        # Determine if rendering damage to the hero party or monster party.
        # NOTE: At present not supporting concurrent damage to members of both parties
        if 0 == len(targets):
            # No targets so this is a no-op
            return

        if isinstance(targets[0], MonsterState):
            self.render_damage_to_monster_party(targets)
        else:
            self.render_damage_to_hero_party()

    def render_damage_to_monster_party(
        self, targets: List[CombatCharacterState]
    ) -> None:
        self.render_flickering_monsters(targets, pygame.Color("red"))

    def render_monster_casting(self, casting_monster: CombatCharacterState) -> None:
        self.render_flickering_monsters([casting_monster], pygame.Color("white"))

    def render_flickering_monsters(
        self, monsters: List[CombatCharacterState], flicker_color: pygame.Color
    ) -> None:
        clock = pygame.time.Clock()
        for _ in range(10):
            self.render_monsters(monsters, monsters, flicker_color=flicker_color)
            clock.tick(30)
            pygame.display.flip()

            self.render_monsters([], monsters)
            clock.tick(30)
            pygame.display.flip()

        # Final render to drop any of the targets which were killed
        self.render_monsters()

    def render_damage_to_hero_party(self) -> None:
        status_dialog = GameDialog.create_encounter_status_dialog(self.hero_party)
        clock = pygame.time.Clock()
        offset_pixels = Point(
            CombatEncounter.DAMAGE_FLICKER_PIXELS, CombatEncounter.DAMAGE_FLICKER_PIXELS
        )
        for _ in range(10):
            if not self.hero_party.is_still_in_combat():
                # On a death blow, the background flickers red
                self.game_state.screen.fill("red")
            else:
                self.game_state.screen.blit(self.background_image, (0, 0))
            self.render_monsters(render_background=False, render_dialogs=False)
            status_dialog.blit(self.game_state.screen, offset_pixels=offset_pixels)
            self.message_dialog.blit(
                self.game_state.screen, offset_pixels=offset_pixels
            )
            clock.tick(30)
            pygame.display.flip()

            self.game_state.screen.blit(self.background_image, (0, 0))
            self.render_monsters(render_dialogs=False)
            status_dialog.blit(self.game_state.screen)
            self.message_dialog.blit(self.game_state.screen)
            clock.tick(30)
            pygame.display.flip()

    def get_monsters_still_in_combat(self) -> List[CombatCharacterState]:
        return self.monster_party.get_still_in_combat_members()

    def get_turn_order(self) -> List[Union[HeroState, MonsterState]]:
        # TODO: In the future rework this method to better support parties with multiple members
        turn_order: List[Union[HeroState, MonsterState]] = []
        skip_hero_party = False
        if self.is_first_turn:
            self.is_first_turn = False
            skip_hero_party = self.monster_party.members[0].has_initiative(
                self.hero_party.main_character
            )
        if skip_hero_party:
            if 1 == len(self.monster_party.members):
                monster_names = self.monster_party.members[0].get_name()
            else:
                monster_names = "They"
            hero_names = MonsterParty.concatenate_string_list(
                [
                    hero.get_name()
                    for hero in self.hero_party.get_still_in_combat_members()
                ]
            )
            was_were = (
                "was"
                if 1 == len(self.hero_party.get_still_in_combat_members())
                else "were"
            )
            self.add_message(
                f"{monster_names} attacked before {hero_names} {was_were} ready."
            )
        else:
            for hero in self.hero_party.combat_members:
                if hero.is_still_in_combat():
                    turn_order.append(hero)
        for monster in self.monster_party.members:
            if monster.is_still_in_combat():
                turn_order.append(monster)
        return turn_order

    def still_in_encounter(self) -> bool:
        return (
            self.game_state.is_running
            and self.monster_party.is_still_in_combat()
            and self.hero_party.is_still_in_combat()
        )

    def check_wake_up(self, combatant: CombatCharacterState) -> None:
        if combatant.is_asleep:
            if combatant.is_still_asleep():
                self.add_message(combatant.get_name() + " is still asleep.")
            else:
                self.add_message(combatant.get_name() + " awakes.")

    def execute_monster_turn(self, monster: MonsterState) -> None:
        self.add_message("")

        # Check if the monster wakes up
        self.check_wake_up(monster)
        if monster.is_asleep:
            return

        # Check if the monster is going to run away.  Only random monsters should ever run away.
        if monster.should_run_away(self.hero_party.main_character):
            monster.has_run_away = True
            AudioPlayer().play_sound("run_away")
            self.add_message(monster.get_name() + " is running away.")
            self.render_monsters()
            return

        # Determine the target for the monster action (if needed)
        target = random.choice(self.hero_party.get_still_in_combat_members())

        # Determine the monster action
        chosen_monster_action: Optional[MonsterAction] = None
        # TODO: Could move this into the MonsterState class
        for monster_action_rule in monster.monster_info.monster_action_rules:
            monster_health_ratio = monster.hp / monster.max_hp
            if monster_health_ratio > monster_action_rule.health_ratio_threshold:
                continue
            if monster_action_rule.action.is_sleep_action() and target.is_asleep:
                continue
            if (
                monster_action_rule.action.is_stopspell_action()
                and target.are_spells_blocked
            ):
                continue
            if random.uniform(0, 1) <= monster_action_rule.probability:
                chosen_monster_action = monster_action_rule.action
                break

        if chosen_monster_action is None:
            print("ERROR: Failed to select action for monster ", monster, flush=True)
            self.add_message(
                monster.get_name()
                + " stares at "
                + target.get_name()
                + " with evil eyes."
            )
            return

        # Revise the target for the selected action
        self.gde.set_actor(monster)
        if TargetTypeEnum.SINGLE_ALLY == chosen_monster_action.target_type:
            self.gde.set_targets([monster])
        elif TargetTypeEnum.ALL_ALLIES == chosen_monster_action.target_type:
            self.gde.set_targets(self.monster_party.get_still_in_combat_members())
        elif TargetTypeEnum.SINGLE_ENEMY == chosen_monster_action.target_type:
            self.gde.set_targets([target])
        else:  # TargetTypeEnum.ALL_ENEMIES
            self.gde.set_targets(self.hero_party.get_still_in_combat_members())

        # Perform the monster action
        self.gde.traverse_dialog(
            self.message_dialog,
            chosen_monster_action.use_dialog,
            depth=1,
            add_spacing=False,
        )

    def execute_player_turn(self, hero: HeroState) -> None:
        self.add_message("")

        # Check if the hero wakes up
        self.check_wake_up(hero)
        if hero.is_asleep:
            self.wait_for_acknowledgement()
            return

        # Setup for the encounter prompt
        options = ["FIGHT", "RUN"]
        if 0 < len(hero.get_available_spells()):
            options.append("SPELL")
        if 0 < len(
            hero.get_item_row_data(limit_to_unequipped=True, filter_types=["Tool"])
        ):
            options.append("ITEM")
        prompt = "Command?"
        if 1 < len(self.hero_party.combat_members):
            prompt = "Command " + hero.get_name() + "?"

        use_dialog = None
        target_type = None
        prev_menu_result = None
        GameEvents.clear_events()  # Clear event queue
        while self.game_state.is_running:
            # Get selected action for turn
            self.message_dialog.add_encounter_prompt(options=options, prompt=prompt)
            if prev_menu_result is not None:
                self.message_dialog.set_selected_menu_option(prev_menu_result)
            self.message_dialog.blit(self.game_state.screen, True)
            menu_result = None
            while self.game_state.is_running and menu_result is None:
                menu_result = self.gde.get_menu_result(self.message_dialog)
            if not self.game_state.is_running:
                return
            prev_menu_result = menu_result

            # Process encounter menu selection to set use_dialog and target_type
            if menu_result == "FIGHT":
                weapon = self.game_info.default_weapon
                if hero.weapon is not None:
                    weapon = hero.weapon
                use_dialog = weapon.use_dialog
                target_type = weapon.target_type

                if self.game_state.should_add_math_problems_in_combat():
                    CombatEncounter.add_problem_to_use_dialog(use_dialog)

            elif menu_result == "RUN":
                target = random.choice(self.monster_party.get_still_in_combat_members())
                if target.is_blocking_escape(hero):
                    AudioPlayer().play_sound("attack_miss_lvl2")
                    self.add_message(
                        hero.get_name()
                        + " started to run away but was blocked in front."
                    )
                else:
                    AudioPlayer().play_sound("run_away")
                    self.add_message(hero.get_name() + " started to run away.")
                    hero.has_run_away = True
                return

            elif menu_result == "SPELL":
                available_spell_names = hero.get_available_spell_names()
                if len(available_spell_names) == 0:
                    self.add_message("Thou hast not yet learned any spells.")
                    continue

                menu_dialog = GameDialog.create_menu_dialog(
                    Point(-1, 1), None, "SPELLS", available_spell_names, 1
                )
                menu_dialog.blit(self.game_state.screen, True)
                menu_result = self.gde.get_menu_result(menu_dialog)
                menu_dialog.erase(self.game_state.screen, self.background_image)

                # print('menu_result =', menu_result, flush=True)
                if menu_result is None:
                    continue
                spell = hero.get_spell(menu_result)
                if spell is not None and hero.mp >= spell.mp:
                    hero.mp -= spell.mp
                    use_dialog = spell.use_dialog
                    target_type = spell.target_type
                else:
                    self.add_message(
                        "Thou dost not have enough magic to cast the spell."
                    )
                    continue
                menu_dialog.erase(self.game_state.screen, self.background_image, True)

            elif menu_result == "ITEM":
                item_cols = 2
                item_row_data = hero.get_item_row_data(
                    limit_to_unequipped=True, filter_types=["Tool"]
                )
                if len(item_row_data) == 0:
                    self.add_message("Thou dost not have any tools.")
                    continue

                menu_dialog = GameDialog.create_menu_dialog(
                    Point(-1, 1),
                    None,
                    "ITEMS",
                    item_row_data,
                    item_cols,
                    GameDialogSpacing.OUTSIDE_JUSTIFIED,
                )
                menu_dialog.blit(self.game_state.screen, True)
                item_result = self.gde.get_menu_result(menu_dialog)
                menu_dialog.erase(self.game_state.screen, self.background_image)

                # print( 'item_result =', item_result, flush=True )
                if item_result is None:
                    continue
                item = hero.get_item(item_result)
                if item is None or not isinstance(item, Tool):
                    continue
                if item.use_dialog is not None:
                    use_dialog = item.use_dialog
                    target_type = item.target_type
                else:
                    self.add_message(
                        hero.get_name()
                        + " studied the object and was confounded by it."
                    )
                    return
            else:
                continue

            # If here the turn was successfully completed
            break

        if use_dialog is None or target_type is None:
            self.add_message("Thou held back in defense.")
            return

        # Select the target for the selected action
        self.gde.set_actor(hero)
        if TargetTypeEnum.SELF == target_type:
            self.gde.set_targets([hero])
        if TargetTypeEnum.SINGLE_ALLY == target_type:
            still_in_combat_heroes = self.hero_party.get_still_in_combat_members()
            if 1 == len(still_in_combat_heroes):
                self.gde.set_targets(still_in_combat_heroes)
            else:
                # TODO: Prompt for selection of which ally to target
                self.gde.set_targets([still_in_combat_heroes[0]])
        elif TargetTypeEnum.ALL_ALLIES == target_type:
            self.gde.set_targets(self.hero_party.get_still_in_combat_members())
        elif TargetTypeEnum.SINGLE_ENEMY == target_type:
            still_in_combat_monsters = self.monster_party.get_still_in_combat_members()
            if 1 == len(still_in_combat_monsters):
                self.gde.set_targets(still_in_combat_monsters)
            else:
                # TODO: Prompt for selection of which enemy to target
                self.gde.set_targets([still_in_combat_monsters[0]])
        elif TargetTypeEnum.ALL_ENEMIES:
            self.gde.set_targets(self.monster_party.get_still_in_combat_members())
        else:
            print("ERROR: Unsupported target type", target_type, flush=True)

        # Perform the action
        self.gde.traverse_dialog(self.message_dialog, use_dialog, depth=1)

    def handle_victory(self) -> None:
        if 0 < self.monster_party.get_defeated_count():
            AudioPlayer().play_sound("combat_won")
            gp = self.monster_party.get_gp()
            xp = self.monster_party.get_xp()
            # TODO: Update text for multiple monster encounters
            if gp != 0 or xp != 0:
                self.add_message(
                    f"\nThou hast done well in defeating {self.monster_party.get_defeated_monster_summary()}. "
                    f"Thy experience increases by {xp}. Thy gold increases by {gp}."
                )
            self.hero_party.gp += gp
            for hero in self.hero_party.combat_members:
                if hero.is_still_in_combat():
                    hero.xp += xp
                    old_level = hero.level
                    old_spells = hero.get_available_spells()
                    if hero.level_up_check():
                        self.wait_for_acknowledgement()
                        AudioPlayer().play_sound("level_up")
                        GameDialog.create_encounter_status_dialog(self.hero_party).blit(
                            self.game_state.screen, False
                        )
                        # TODO: Update text for multiple hero encounters
                        self.add_message(
                            "\nCourage and wit have served thee well. Thou hast been promoted to the next level."
                        )
                        strength_increase = hero.level.strength - old_level.strength
                        agility_increase = hero.level.agility - old_level.agility
                        hp_increase = hero.level.hp - old_level.hp
                        mp_increase = hero.level.mp - old_level.mp
                        if strength_increase > 0:
                            self.add_message(
                                f"Thy strength increases by {strength_increase}."
                            )
                        if agility_increase > 0:
                            self.add_message(
                                f"Thy agility increases by {agility_increase}."
                            )
                        if hp_increase > 0:
                            self.add_message(
                                f"Thy maximum hit points increase by {hp_increase}."
                            )
                        if mp_increase > 0:
                            self.add_message(
                                f"Thy maximum magic points increase by {mp_increase}."
                            )
                        # print('old_spells =', len(old_spells), flush=True)
                        # print('new_spells =', len(hero.get_available_spells()), flush=True)
                        if len(hero.get_available_spells()) > len(old_spells):
                            self.add_message("Thou hast learned a new spell.")

        if self.victory_dialog is not None:
            self.gde.traverse_dialog(self.message_dialog, self.victory_dialog)

    def add_message(self, message: str) -> None:
        self.gde.add_and_wait_for_message(message, self.message_dialog)

    def wait_for_acknowledgement(self) -> None:
        self.gde.wait_for_acknowledgement(self.message_dialog)

    @staticmethod
    def add_problem_to_use_dialog(
        dialog: DialogType, problem: Optional[Problem] = None
    ) -> None:
        damage_action = GameTypes.get_dialog_action(
            dialog, DialogActionEnum.DAMAGE_TARGET
        )
        if damage_action is not None and isinstance(damage_action, DialogAction):
            if problem is None:
                # problem = CombatEncounter.gen_any_problem()
                problem = CombatEncounter.gen_cam_problem()
            damage_action.problem = problem

    @staticmethod
    def gen_addition_problem(min_term: int = 0, max_term: int = 12) -> Problem:
        addend_1 = random.randrange(min_term, max_term)
        addend_2 = random.randrange(min_term, max_term)
        summation = addend_1 + addend_2
        return Problem(
            str(addend_1) + " + " + str(addend_2) + " =", str(summation), "0123456789"
        )

    @staticmethod
    def gen_subtraction_problem(
        min_term: int = 0,
        max_term: int = 12,
        minuend_min: Optional[int] = None,
        minuend_max: Optional[int] = None,
    ) -> Problem:
        if minuend_min is not None and minuend_max is not None:
            minuend = random.randrange(12, 16)
            subtrahend = random.randrange(
                min(min_term, minuend), min(max_term, minuend)
            )
        else:
            term1 = random.randrange(min_term, max_term)
            term2 = random.randrange(min_term, max_term)
            minuend = term1 + term2
            subtrahend = random.choice((term1, term2))
        difference = minuend - subtrahend
        return Problem(
            str(minuend) + " - " + str(subtrahend) + " =", str(difference), "0123456789"
        )

    @staticmethod
    def gen_multiplication_problem(
        min_term: int = 0,
        max_term: int = 12,
        multiplicand_1_range: Optional[List[int]] = None,
        multiplicand_2_range: Optional[List[int]] = None,
    ) -> Problem:
        if multiplicand_1_range is None:
            multiplicand_1 = random.randrange(min_term, max_term)
        else:
            multiplicand_1 = random.choice(multiplicand_1_range)

        if multiplicand_2_range is None:
            multiplicand_2 = random.randrange(min_term, max_term)
        else:
            multiplicand_2 = random.choice(multiplicand_2_range)

        # If using the ranges, swap values half the time to randomize the order of the multiplicands.
        if (
            multiplicand_1_range is not None or multiplicand_2_range is not None
        ) and 0 == random.randrange(0, 1):
            multiplicand_1, multiplicand_2 = multiplicand_2, multiplicand_1

        product = multiplicand_1 * multiplicand_2
        return Problem(
            str(multiplicand_1) + " x " + str(multiplicand_2) + " =",
            str(product),
            "0123456789",
        )

    @staticmethod
    def gen_division_problem(
        min_term: int = 0,
        max_term: int = 12,
        multiplicand_1_range: Optional[List[int]] = None,
        multiplicand_2_range: Optional[List[int]] = None,
    ) -> Problem:
        if multiplicand_1_range is None:
            multiplicand_1 = random.randrange(min_term, max_term)
        else:
            multiplicand_1 = random.choice(multiplicand_1_range)

        if multiplicand_2_range is None:
            multiplicand_2 = random.randrange(min_term, max_term)
        else:
            multiplicand_2 = random.choice(multiplicand_2_range)

        # If using the ranges, swap values half the time to randomize the order of the multiplicands.
        if (
            multiplicand_1_range is not None or multiplicand_2_range is not None
        ) and 0 == random.randrange(0, 1):
            multiplicand_1, multiplicand_2 = multiplicand_2, multiplicand_1

        dividend = multiplicand_1 * multiplicand_2
        divisor = random.choice((multiplicand_1, multiplicand_2))
        if divisor == 0:
            divisor = 1
        quotient = dividend // divisor
        return Problem(
            str(dividend) + " / " + str(divisor) + " =", str(quotient), "0123456789"
        )

    @staticmethod
    def gen_any_problem(min_term: int = 0, max_term: int = 12) -> Problem:
        random_val = random.randrange(0, 3)
        if 0 == random_val:
            return CombatEncounter.gen_addition_problem(min_term, max_term)
        if 1 == random_val:
            return CombatEncounter.gen_subtraction_problem(min_term, max_term)
        if 2 == random_val:
            return CombatEncounter.gen_multiplication_problem(min_term, max_term)
        return CombatEncounter.gen_division_problem(min_term, max_term)

    @staticmethod
    def gen_cam_problem() -> Problem:
        random_val = random.choices([0, 1, 2, 3], weights=(1, 1, 8, 3))[0]
        if 0 == random_val:
            return CombatEncounter.gen_addition_problem(min_term=0, max_term=20)
        if 1 == random_val:
            return CombatEncounter.gen_subtraction_problem(min_term=0, max_term=20)
        if 2 == random_val:
            return CombatEncounter.gen_multiplication_problem(min_term=0, max_term=12)
        return CombatEncounter.gen_division_problem(min_term=0, max_term=12)


def main() -> None:
    # Initialize pygame
    pygame.init()
    pygame.font.init()

    # Setup the screen
    win_size_pixels = Point(1280, 960)
    tile_size_pixels = 48
    win_size_tiles = (win_size_pixels / tile_size_pixels).ceil()
    win_size_pixels = win_size_tiles * tile_size_pixels
    screen = pygame.display.set_mode(
        win_size_pixels.get_as_int_tuple(), pygame.SRCALPHA | pygame.HWSURFACE
    )
    screen.fill("pink")

    # Initialize GameInfo
    import os

    base_path = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    game_xml_path = os.path.join(base_path, "game.xml")
    GameInfo.static_init(base_path, game_xml_path, win_size_tiles, tile_size_pixels)
    game_info = GameInfo(base_path, game_xml_path, tile_size_pixels, win_size_pixels)

    # Find an encounter image to use
    for game_map in game_info.maps.values():
        if game_map.encounter_background is not None:
            encounter_background = game_map.encounter_background
            break

    # Verify an encounter image was found
    if encounter_background is None:
        print("Failed to find an encounter image", flush=True)
        AudioPlayer().terminate()
        pygame.quit()
        return

    # Setup a mock game state
    from unittest import mock
    from unittest.mock import MagicMock
    from pydw.game_types import DialogReplacementVariables

    mock_game_state = mock.create_autospec(spec=GameStateInterface)
    mock_game_state.screen = screen
    mock_game_state.is_running = True
    mock_game_state.is_light_restricted = MagicMock(return_value=False)
    mock_game_state.get_win_size_pixels = MagicMock(return_value=win_size_pixels)
    mock_game_state.get_dialog_replacement_variables = MagicMock(
        return_value=DialogReplacementVariables()
    )
    mock_game_state.should_add_math_problems_in_combat = MagicMock(return_value=False)

    def handle_quit_side_effect(force: bool = False) -> None:
        _ = force  # appease pylint - force is needed to conform to the interface
        mock_game_state.is_running = False

    mock_game_state.handle_quit = MagicMock(side_effect=handle_quit_side_effect)

    # Create a series of hero party and monster party tuples for encounters
    from pydw.game_types import Direction

    combat_parties = []
    for i in range(1, 4):
        hero_party = HeroParty(
            HeroState(
                game_info.character_types["hero"],
                Point(),
                Direction.NORTH,
                "Camden",
                20000,
            )
        )
        monster_party = MonsterParty(
            cast(
                List[Union[MonsterInfo, SpecialMonster, MonsterState]],
                list(game_info.monsters.values())[0:i],
            )
        )
        monster_party.add_monster(list(game_info.monsters.values())[0])
        combat_parties.append((hero_party, monster_party))
    for monster_name in [
        "Metal Slime",
        "Golem",
        "Knight",
        "Magiwyvern",
        "Starwyvern",
        "Red Dragon",
    ]:
        hero_party = HeroParty(
            HeroState(
                game_info.character_types["hero"],
                Point(),
                Direction.NORTH,
                "Camden",
                20000,
            )
        )
        hero_party.main_character.gain_item(game_info.items["Fairy Flute"])
        monster_party = MonsterParty([game_info.monsters[monster_name]])
        combat_parties.append((hero_party, monster_party))

    # Run a series of combat encounters
    CombatEncounter.static_init("combat")
    for hero_party, monster_party in combat_parties:
        if not mock_game_state.is_running:
            break

        mock_game_state.get_hero_party = MagicMock(return_value=hero_party)
        combat_encounter = CombatEncounter(
            game_info, mock_game_state, monster_party, encounter_background
        )
        combat_encounter.encounter_loop()
        pygame.time.wait(200)

    # Terminate pygame
    AudioPlayer().terminate()
    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import sys
        import traceback

        print(
            traceback.format_exception(
                None, e, e.__traceback__  # <- type(e) by docs, but ignored
            ),
            file=sys.stderr,
            flush=True,
        )
        traceback.print_exc()
