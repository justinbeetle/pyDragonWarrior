#!/usr/bin/env python

from typing import cast, List, Optional, Union

import pygame
import random

from AudioPlayer import AudioPlayer
from CombatCharacterState import CombatCharacterState
from CombatEncounterInterface import CombatEncounterInterface
from GameDialog import GameDialog, GameDialogSpacing
from GameDialogEvaluator import GameDialogEvaluator
import GameEvents
from GameInfo import GameInfo
from GameStateInterface import GameStateInterface
from GameTypes import DialogType, MonsterInfo, SpecialMonster, TargetTypeEnum, Tool
from HeroParty import HeroParty
from HeroState import HeroState
from MonsterParty import MonsterParty
from MonsterState import MonsterState
from Point import Point
import SurfaceEffects


class CombatEncounter(CombatEncounterInterface):
    MONSTER_SPACING_PIXELS = 20
    DAMAGE_FLICKER_PIXELS = 4
    default_encounter_music = ''

    @staticmethod
    def static_init(default_encounter_music: str) -> None:
        CombatEncounter.default_encounter_music = default_encounter_music

    def __init__(self,
                 game_info: GameInfo,
                 game_state: GameStateInterface,
                 monster_party: MonsterParty,
                 encounter_image: pygame.Surface,
                 message_dialog: Optional[GameDialog] = None,
                 approach_dialog: Optional[DialogType] = None,
                 victory_dialog: Optional[DialogType] = None,
                 run_away_dialog: Optional[DialogType] = None,
                 encounter_music: Optional[str] = None) -> None:
        self.is_first_turn = True
        self.game_info = game_info
        self.game_state = game_state
        self.gde = GameDialogEvaluator(game_info, game_state, self)
        self.hero_party = game_state.get_hero_party()
        self.monster_party = monster_party
        self.background_image = game_state.screen.copy()
        self.encounter_image = encounter_image
        self.approach_dialog = approach_dialog
        self.victory_dialog = victory_dialog
        self.run_away_dialog = run_away_dialog
        if message_dialog is not None:
            self.message_dialog = message_dialog
            self.message_dialog.add_message('')
        else:
            self.message_dialog = GameDialog.create_message_dialog()
        if encounter_music is not None:
            self.encounter_music = encounter_music
        else:
            self.encounter_music = CombatEncounter.default_encounter_music

        self.hero_party.clear_combat_status_affects()

    def encounter_loop(self) -> None:
        # Start encounter music
        AudioPlayer().play_music(self.encounter_music)
        # AudioPlayer().playMusic('14_Dragon_Quest_1_-_A_Monster_Draws_Near.mp3',
        #                         '24_Dragon_Quest_1_-_Monster_Battle.mp3')

        # Save off initial key repeat settings
        (orig_repeat1, orig_repeat2) = pygame.key.get_repeat()
        pygame.key.set_repeat()
        # print('Disabled key repeat', flush=True)

        # Clear event queue
        GameEvents.get_events()

        # Render the status dialog, monsters, and approach dialog
        GameDialog.create_encounter_status_dialog(self.hero_party).blit(self.game_state.screen, False)
        self.render_monsters()
        if self.approach_dialog is not None:
            self.gde.traverse_dialog(self.message_dialog, self.approach_dialog, depth=1)
        else:
            self.message_dialog.add_message(self.monster_party.get_default_approach_dialog())
        self.message_dialog.blit(self.game_state.screen, True)

        # Check if monsters run away at the start of the encounter
        last_turn_was_monster_turn = False
        for monster in self.monster_party.members:
            if monster.is_still_in_combat():
                if monster.should_run_away(self.hero_party.main_character):
                    if last_turn_was_monster_turn:
                        self.gde.wait_for_acknowledgement(self.message_dialog)
                    else:
                        # Pause to allow time to see the monsters before they run away
                        for pauseTicks in range(10):
                            pygame.time.Clock().tick(30)
                    last_turn_was_monster_turn = True
                    monster.has_run_away = True
                    self.message_dialog.add_message(monster.get_name() + ' is running away.')
                    self.render_monsters()

        # Iterate through turns in the encounter until the encounter ends
        while self.still_in_encounter():
            for combatant in self.get_turn_order():
                if combatant.is_still_in_combat():
                    if isinstance(combatant, MonsterState):
                        if last_turn_was_monster_turn:
                            self.gde.wait_for_acknowledgement(self.message_dialog)
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
            else:
                self.handle_running_away()
        else:
            self.handle_death()

        # Wait for final acknowledgement
        self.gde.wait_for_acknowledgement(self.message_dialog)

        # Restore initial background image and key repeat settings
        self.game_state.screen.blit(self.background_image, (0, 0))
        pygame.key.set_repeat(orig_repeat1, orig_repeat2)

        # Call game_state.draw_map but manually flip the buffer for the case where this method is a mock
        self.game_state.draw_map(False)
        pygame.display.flip()

    def render_monsters(self,
                        damage_image_monsters: List[CombatCharacterState] = [],
                        force_display_monsters: List[CombatCharacterState] = []) -> None:
        # Render the encounter background
        encounter_image_size_px = Point(self.encounter_image.get_size())
        encounter_image_dest_px = Point(
            (self.game_state.get_win_size_pixels().w - encounter_image_size_px.w) / 2,
            self.message_dialog.pos_tile.y * self.game_info.tile_size_pixels
            - encounter_image_size_px.h + CombatEncounter.DAMAGE_FLICKER_PIXELS)
        self.game_state.screen.blit(self.encounter_image, encounter_image_dest_px)

        # Render the monsters
        monster_width_px = CombatEncounter.MONSTER_SPACING_PIXELS * (len(self.monster_party.members) - 1)
        for monster in self.monster_party.members:
            monster_width_px += monster.monster_info.image.get_width()
        monster_pos_x = (self.game_state.get_win_size_pixels().x - monster_width_px) / 2
        for monster in self.monster_party.members:
            if monster.is_still_in_combat() or monster in force_display_monsters:
                if monster in damage_image_monsters:
                    monster_image = monster.monster_info.dmg_image
                else:
                    monster_image = monster.monster_info.image
                monster_image_dest_px = Point(monster_pos_x,
                                              encounter_image_dest_px.y + encounter_image_size_px.y
                                              - monster.monster_info.image.get_height()
                                              - self.game_info.tile_size_pixels)
                self.game_state.screen.blit(monster_image, monster_image_dest_px)

            monster_pos_x += CombatEncounter.MONSTER_SPACING_PIXELS + monster.monster_info.image.get_width()

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

    def render_damage_to_monster_party(self, targets: List[CombatCharacterState]) -> None:
        for flickerTimes in range(10):
            self.render_monsters(targets, targets)
            pygame.display.flip()
            pygame.time.Clock().tick(30)

            self.render_monsters([], targets)
            pygame.display.flip()
            pygame.time.Clock().tick(30)

        # Final render to drop any of the targets which were killed
        self.render_monsters()

    def render_damage_to_hero_party(self) -> None:
        status_dialog = GameDialog.create_encounter_status_dialog(self.hero_party)
        for flickerTimes in range(10):
            offset_pixels = Point(CombatEncounter.DAMAGE_FLICKER_PIXELS, CombatEncounter.DAMAGE_FLICKER_PIXELS)
            self.game_state.screen.blit(self.background_image, (0, 0))
            self.render_monsters()
            status_dialog.blit(self.game_state.screen, False, offset_pixels)
            self.message_dialog.blit(self.game_state.screen, True, offset_pixels)

            pygame.time.Clock().tick(30)
            self.game_state.screen.blit(self.background_image, (0, 0))
            self.render_monsters()
            status_dialog.blit(self.game_state.screen, False)
            self.message_dialog.blit(self.game_state.screen, True)
            pygame.time.Clock().tick(30)

    def get_turn_order(self) -> List[Union[HeroState, MonsterState]]:
        # TODO: In the future rework this method to better support parties with multiple members
        turn_order: List[Union[HeroState, MonsterState]] = []
        skip_hero_party = False
        if self.is_first_turn:
            self.is_first_turn = False
            skip_hero_party = self.monster_party.members[0].has_initiative(self.hero_party.main_character)
        if skip_hero_party:
            self.message_dialog.add_message(self.monster_party.members[0].get_name() + ' attacked before '
                                            + self.hero_party.main_character.get_name() + ' was ready.')
        else:
            for hero in self.hero_party.members:
                if hero.is_still_in_combat():
                    turn_order.append(hero)
        for monster in self.monster_party.members:
            if monster.is_still_in_combat():
                turn_order.append(monster)
        return turn_order

    def still_in_encounter(self) -> bool:
        return (self.game_state.is_running
                and self.monster_party.is_still_in_combat()
                and self.hero_party.is_still_in_combat())

    def check_wake_up(self, combatant: CombatCharacterState) -> None:
        if combatant.is_asleep:
            if combatant.is_still_asleep():
                if combatant.turns_asleep == 1:
                    self.message_dialog.add_message(combatant.get_name() + ' is asleep.')
                else:
                    self.message_dialog.add_message(combatant.get_name() + ' is still asleep.')
            else:
                self.message_dialog.add_message(combatant.get_name() + ' awakes.')

    def execute_monster_turn(self, monster: MonsterState) -> None:
        self.message_dialog.add_message('')

        # Check if the monster wakes up
        self.check_wake_up(monster)
        if monster.is_asleep:
            return

        # Check if the monster is going to run away.  Only random monsters should ever run away.
        if monster.should_run_away(self.hero_party.main_character):
            # TODO: Play sound?
            monster.has_run_away = True
            self.message_dialog.add_message(monster.get_name() + ' is running away.')
            self.render_monsters()
            return

        # Determine the target for the monster action (if needed)
        target = random.choice(self.hero_party.get_still_in_combat_members())

        # Determine the monster action
        # TODO: Could move this into the MonsterState class
        chosen_monster_action = self.game_info.default_monster_action
        for monster_action_rule in monster.monster_info.monster_action_rules:
            monster_health_ratio = monster.hp / monster.max_hp
            if monster_health_ratio > monster_action_rule.health_ratio_threshold:
                continue
            if monster_action_rule.action.is_sleep_action() and target.is_asleep:
                continue
            if monster_action_rule.action.is_stopspell_action() and target.are_spells_blocked:
                continue
            if random.uniform(0, 1) < monster_action_rule.probability:
                chosen_monster_action = monster_action_rule.action
                break

        # Revise the target for the selected action
        self.gde.set_actor(monster)
        if TargetTypeEnum.SINGLE_ALLY == chosen_monster_action.target_type:
            self.gde.set_targets([monster])
        elif TargetTypeEnum.ALL_ALLIES == chosen_monster_action.target_type:
            self.gde.set_targets(cast(List[CombatCharacterState], self.monster_party.get_still_in_combat_members()))
        elif TargetTypeEnum.SINGLE_ENEMY == chosen_monster_action.target_type:
            self.gde.set_targets([target])
        else:  # TargetTypeEnum.ALL_ENEMIES
            self.gde.set_targets(cast(List[CombatCharacterState], self.hero_party.get_still_in_combat_members()))

        # Perform the monster action
        self.gde.traverse_dialog(self.message_dialog, chosen_monster_action.use_dialog, depth=1, add_spacing=False)

    def execute_player_turn(self, hero: HeroState) -> None:
        self.message_dialog.add_message('')

        # Check if the hero wakes up
        self.check_wake_up(hero)
        if hero.is_asleep:
            self.gde.wait_for_acknowledgement(self.message_dialog)
            return

        while self.game_state.is_running:

            # Get selected action for turn
            self.message_dialog.add_encounter_prompt()
            self.message_dialog.blit(self.game_state.screen, True)
            menu_result = None
            while self.game_state.is_running and menu_result is None:
                menu_result = self.gde.get_menu_result(self.message_dialog)
            if not self.game_state.is_running:
                return

            # Process encounter menu selection to set use_dialog and target_type
            use_dialog = None
            target_type = None
            if menu_result == 'FIGHT':
                weapon = self.game_info.default_weapon
                if hero.weapon is not None:
                    weapon = hero.weapon
                use_dialog = weapon.use_dialog
                target_type = weapon.target_type

            elif menu_result == 'RUN':
                target = random.choice(self.monster_party.get_still_in_combat_members())
                if target.is_blocking_escape(hero):
                    # TODO: Play sound?
                    self.message_dialog.add_message(
                        hero.get_name() + ' started to run away but was blocked in front.')
                else:
                    AudioPlayer().play_sound('runAway.wav')
                    self.message_dialog.add_message(hero.get_name() + ' started to run away.')
                    hero.has_run_away = True
                return

            elif menu_result == 'SPELL':
                available_spell_names = hero.get_available_spell_names()
                if len(available_spell_names) == 0:
                    self.message_dialog.add_message('Thou hast not yet learned any spells.')
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
                        spell = hero.get_spell(menu_result)
                        if spell is not None and hero.mp >= spell.mp:
                            hero.mp -= spell.mp
                            use_dialog = spell.use_dialog
                            target_type = spell.target_type
                        else:
                            self.message_dialog.add_message('Thou dost not have enough magic to cast the spell.')
                            continue
                    menu_dialog.erase(self.game_state.screen, self.background_image, True)
            elif menu_result == 'ITEM':
                item_row_data = hero.get_item_row_data(limit_to_unequipped=True, filter_types=['Tool'])
                if len(item_row_data) == 0:
                    self.message_dialog.add_message('Thou dost not have any tools.')
                    continue
                else:
                    menu_dialog = GameDialog.create_menu_dialog(
                        Point(-1, 1),
                        None,
                        'ITEMS',
                        item_row_data,
                        2,
                        GameDialogSpacing.OUTSIDE_JUSTIFIED)
                    menu_dialog.blit(self.game_state.screen, True)
                    item_result = self.gde.get_menu_result(menu_dialog)
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
                        self.message_dialog.add_message(hero.get_name()
                                                        + ' studied the object and was confounded by it.')
            else:
                continue

            # If here the turn was successfully completed
            break

        # Select the target for the selected action
        self.gde.set_actor(hero)
        if TargetTypeEnum.SELF == target_type:
            self.gde.set_targets([hero])
        if TargetTypeEnum.SINGLE_ALLY == target_type:
            still_in_combat_members = self.hero_party.get_still_in_combat_members()
            if 1 == len(still_in_combat_members):
                self.gde.set_targets(still_in_combat_members)
            else:
                # TODO: Prompt for selection of which ally to target
                self.gde.set_targets([still_in_combat_members[0]])
        elif TargetTypeEnum.ALL_ALLIES == target_type:
            self.gde.set_targets(cast(List[CombatCharacterState], self.hero_party.get_still_in_combat_members()))
        elif TargetTypeEnum.SINGLE_ENEMY == target_type:
            still_in_combat_members = self.monster_party.get_still_in_combat_members()
            if 1 == len(still_in_combat_members):
                self.gde.set_targets(still_in_combat_members)
            else:
                # TODO: Prompt for selection of which enemey to target
                self.gde.set_targets([still_in_combat_members[0]])
        else:  # TargetTypeEnum.ALL_ENEMIES
            self.gde.set_targets(cast(List[CombatCharacterState], self.monster_party.get_still_in_combat_members()))

        # Perform the action
        self.gde.traverse_dialog(self.message_dialog, use_dialog, depth=1)

    def handle_victory(self) -> None:
        if 0 < self.monster_party.get_defeated_count():
            AudioPlayer().play_sound('17_-_Dragon_Warrior_-_NES_-_Enemy_Defeated.ogg')
            gp = self.monster_party.get_gp()
            xp = self.monster_party.get_xp()
            # TODO: Update text for multiple monster encounters
            self.message_dialog.add_message(
                '\nThou has done well in defeating ' + self.monster_party.get_defeated_monster_summary()
                + '. Thy experience increases by ' + str(xp) + '. Thy gold increases by ' + str(gp) + '.')
            self.hero_party.gp += gp
            for hero in self.hero_party.members:
                if hero.is_still_in_combat():
                    hero.xp += xp
                    if hero.level_up_check():
                        self.gde.wait_for_acknowledgement(self.message_dialog)
                        AudioPlayer().play_sound('18_-_Dragon_Warrior_-_NES_-_Level_Up.ogg')
                        GameDialog.create_exploring_status_dialog(self.hero_party).blit(self.game_state.screen, False)
                        # TODO: Update text for multiple hero encounters
                        self.message_dialog.add_message(
                            '\nCourage and wit have served thee well. Thou hast been promoted to the next level.')
                        self.message_dialog.blit(self.game_state.screen, True)

        if self.victory_dialog is not None:
            self.gde.traverse_dialog(self.message_dialog, self.victory_dialog)

    def handle_running_away(self) -> None:
        if self.run_away_dialog is not None:
            self.gde.traverse_dialog(self.message_dialog, self.run_away_dialog)

    def handle_death(self) -> None:
        self.game_state.handle_death()


def main() -> None:
    # Initialize pygame
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()

    # Setup the screen
    win_size_pixels = Point(1280, 960)
    tile_size_pixels = 48
    win_size_tiles = (win_size_pixels / tile_size_pixels).ceil()
    win_size_pixels = win_size_tiles * tile_size_pixels
    screen = pygame.display.set_mode(win_size_pixels, pygame.SRCALPHA | pygame.HWSURFACE)
    screen.fill(pygame.Color('pink'))
    GameDialog.static_init(win_size_tiles, tile_size_pixels)

    # Initialize GameInfo
    import os
    from GameInfo import GameInfo
    base_path = os.path.split(os.path.abspath(__file__))[0]
    game_xml_path = os.path.join(base_path, 'game.xml')
    game_info = GameInfo(base_path, game_xml_path, tile_size_pixels)
    for map in game_info.maps:
        if game_info.maps[map].encounter_image is not None:
            encounter_image = game_info.maps[map].encounter_image

    # Setup a mock game state
    from unittest import mock
    from unittest.mock import MagicMock
    from GameTypes import DialogReplacementVariables
    mock_game_state = mock.create_autospec(spec=GameStateInterface)
    mock_game_state.screen = screen
    mock_game_state.is_running = True
    mock_game_state.get_win_size_pixels = MagicMock(return_value=win_size_pixels)
    mock_game_state.get_dialog_replacement_variables = MagicMock(return_value=DialogReplacementVariables())

    # Create a series of hero party and monster party tuples for encounters
    from GameTypes import Direction
    combat_parties = []
    for i in range(1, 4):
        hero_party = HeroParty(HeroState(game_info.character_types['hero'], Point(), Direction.NORTH, 'Camden', 20000))
        monster_party = MonsterParty(cast(List[Union[MonsterInfo, SpecialMonster, MonsterState]],
                                          list(game_info.monsters.values())[0:i]))
        monster_party.add_monster(list(game_info.monsters.values())[0])
        combat_parties.append((hero_party, monster_party))
    for monster_name in ['Golem', 'Knight', 'Magiwyvern', 'Starwyvern', 'Red Dragon']:
        hero_party = HeroParty(HeroState(game_info.character_types['hero'], Point(), Direction.NORTH, 'Camden', 20000))
        hero_party.main_character.gain_item(game_info.items['Fairy Flute'])
        monster_party = MonsterParty([game_info.monsters[monster_name]])
        combat_parties.append((hero_party, monster_party))

    # Run a series of combat encounters
    CombatEncounter.static_init('06_-_Dragon_Warrior_-_NES_-_Fight.ogg')
    for (hero_party, monster_party) in combat_parties:
        mock_game_state.get_hero_party = MagicMock(return_value=hero_party)
        combat_encounter = CombatEncounter(game_info,
                                           mock_game_state,
                                           monster_party,
                                           encounter_image)
        combat_encounter.encounter_loop()
        clock.tick(1000)

    # Terminate pygame
    AudioPlayer().terminate()
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