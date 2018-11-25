#!/usr/bin/env python

from typing import List, Optional, Union

import pygame
import random

from AudioPlayer import AudioPlayer
from CombatCharacterState import CombatCharacterState
from GameDialog import GameDialog
from GameDialogEvaluator import GameDialogEvaluator
import GameEvents
from GameStateInterface import GameStateInterface
from GameTypes import ActionCategoryTypeEnum, DialogType, MonsterActionEnum
from HeroParty import HeroParty
from HeroState import HeroState
from MonsterParty import MonsterParty
from MonsterState import MonsterState
from Point import Point
import SurfaceEffects


class CombatEncounter:
    MONSTER_SPACING_PIXELS = 20
    DAMAGE_FLICKER_PIXELS = 4
    default_encounter_music = ''

    @staticmethod
    def static_init(default_encounter_music: str) -> None:
        CombatEncounter.default_encounter_music = default_encounter_music

    def __init__(self,
                 game_state: GameStateInterface,
                 monster_party: MonsterParty,
                 encounter_image: pygame.Surface,
                 message_dialog: Optional[GameDialog] = None,
                 approach_dialog: Optional[DialogType] = None,
                 victory_dialog: Optional[DialogType] = None,
                 run_away_dialog: Optional[DialogType] = None,
                 encounter_music: Optional[str] = None) -> None:
        self.is_first_turn = True
        self.game_state = game_state
        self.gde = GameDialogEvaluator(game_state)
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
        for monster in self.monster_party.members:
            if monster.is_still_in_combat():
                if monster.should_run_away(self.hero_party.main_character):
                    monster.has_run_away = True
                    self.message_dialog.add_message('The ' + monster.get_name() + ' is running away.')

        # Iterate through turns in the encounter until the encounter ends
        while self.still_in_encounter():
            for combatant in self.get_turn_order():
                if combatant.is_still_in_combat():
                    if isinstance(combatant, MonsterState):
                        self.execute_monster_turn(combatant)
                    elif isinstance(combatant, HeroState):
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

    def render_monsters(self, damage_image_monsters: List[MonsterState] = []) -> None:
        # Render the encounter background
        encounter_image_size_px = Point(self.encounter_image.get_size())
        encounter_image_dest_px = Point(
            (self.game_state.get_win_size_pixels().w - encounter_image_size_px.w) / 2,
            self.message_dialog.pos_tile.y * self.game_state.get_tile_size_pixels()
            - encounter_image_size_px.h + CombatEncounter.DAMAGE_FLICKER_PIXELS)
        self.game_state.screen.blit(self.encounter_image, encounter_image_dest_px)

        # Render the monsters  CombatEncounter.MONSTER_SPACING_PIXELS
        monster_width_px = CombatEncounter.MONSTER_SPACING_PIXELS * (len(self.monster_party.members) - 1)
        for monster in self.monster_party.members:
            monster_width_px += monster.monster_info.image.get_width()
        monster_pos_x = self.game_state.get_win_size_pixels().x - monster_width_px / 2
        for monster in self.monster_party.members:
            if monster.is_still_in_combat():
                if monster in damage_image_monsters:
                    monster_image = monster.monster_info.dmg_image
                else:
                    monster_image = monster.monster_info.image
                monster_image_dest_px = Point(monster_pos_x,
                                              encounter_image_dest_px.y + encounter_image_size_px.y
                                              - monster.monster_info.image.get_height()
                                              - self.game_state.get_tile_size_pixels())
                self.game_state.screen.blit(monster_image, monster_image_dest_px)
            monster_pos_x += CombatEncounter.MONSTER_SPACING_PIXELS + monster.monster_info.image.get_width()

    def get_turn_order(self) -> List[Union[HeroState, MonsterState]]:
        # TODO: In the future rework this method to better support parties with multiple members
        turn_order: List[Union[HeroState, MonsterState]] = []
        skip_hero_party = False
        if self.is_first_turn:
            self.is_first_turn = False
            skip_hero_party = self.monster_party.members[0].has_initiative(self.hero_party.main_character)
        if skip_hero_party:
            self.message_dialog.add_message('The ' + self.monster_party.members[0].get_name() + ' attacked before '
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
            self.message_dialog.add_message('The ' + monster.get_name() + ' is running away.')
            return

        # Determine the target for the monster action (if needed)
        target = random.choice(self.hero_party.get_still_in_combat_members())

        # Determine the monster action
        # TODO: Could move this into the MonsterState class
        chosen_monster_action = MonsterActionEnum.ATTACK
        for monster_action in monster.monster_info.monster_actions:
            monster_health_ratio = monster.hp / monster.max_hp
            if monster_health_ratio > monster_action.health_ratio_threshold:
                continue
            if MonsterActionEnum.SLEEP == monster_action.type and target.is_asleep:
                continue
            if MonsterActionEnum.STOPSPELL == monster_action.type and target.are_spells_blocked:
                continue
            if random.uniform(0, 1) < monster_action.probability:
                chosen_monster_action = monster_action.type
                break

        # Perform the monster action
        damage = 0
        if chosen_monster_action.is_spell():
            spell = chosen_monster_action.get_spell(self.game_state.get_spells())
            if spell is not None:
                AudioPlayer().play_sound('castSpell.wav')
                SurfaceEffects.flickering(self.game_state.screen)
                self.message_dialog.add_message('The ' + monster.get_name() + ' chants the spell of '
                                                + chosen_monster_action.name.lower() + '.')
                if not monster.does_spell_work(spell, target):
                    if monster.are_spells_blocked:
                        self.message_dialog.add_message('But that spell hath been blocked.')
                    else:
                        self.message_dialog.add_message('But that spell did not work.')
                elif chosen_monster_action.is_heal_spell():
                    self.message_dialog.add_message('The ' + monster.get_name() + ' hath recovered.')
                    monster.hp = monster.max_hp
                elif chosen_monster_action.is_hurt_spell():
                    spell = chosen_monster_action.get_spell(self.game_state.get_spells())
                    damage = CombatCharacterState.calc_damage(spell.min_damage_by_monster,
                                                              spell.max_damage_by_monster,
                                                              target,
                                                              ActionCategoryTypeEnum.MAGICAL)
                elif MonsterActionEnum.SLEEP == chosen_monster_action:
                    # TODO: Should this apply to all hero's or only a single one?
                    self.message_dialog.add_message('Thou art asleep.')
                    target.is_asleep = True
                elif MonsterActionEnum.STOPSPELL == chosen_monster_action:
                    # TODO: Should this apply to all hero's or only a single one?
                    self.message_dialog.add_message(target.get_name() + "'s spells hath been blocked.")
                    target.are_spells_blocked = True
                else:
                    print('ERROR: Failed to perform action for spell', chosen_monster_action.name, flush=True)
            else:
                print('ERROR: Failed to find spell for', chosen_monster_action.name, flush=True)
                chosen_monster_action = MonsterActionEnum.ATTACK

        if chosen_monster_action.is_fire_attack():
            AudioPlayer().play_sound('fireBreathingAttack.wav')
            self.message_dialog.add_message('The ' + monster.get_name() + ' is breathing fire.')
            if chosen_monster_action == MonsterActionEnum.BREATH_FIRE:
                min_damage = 16
                max_damage = 23
            else:
                min_damage = 65
                max_damage = 72
            damage = CombatCharacterState.calc_damage(min_damage,
                                                      max_damage,
                                                      target,
                                                      ActionCategoryTypeEnum.FIRE)
        elif MonsterActionEnum.ATTACK == chosen_monster_action:
            damage = monster.get_attack_damage(target)[0]
            if 0 == damage:
                # TODO: Play sound?
                self.message_dialog.add_message(
                    'The ' + monster.get_name() + ' attacks! ' + target.get_name() + ' dodges the strike.')
            else:
                # TODO: Play different sound based on strength of attack
                AudioPlayer().play_sound('Dragon Warrior [Dragon Quest] SFX (5).wav')
                self.message_dialog.add_message('The ' + monster.get_name() + ' attacks!')

        if 0 < damage:
            self.message_dialog.add_message('Thy hit points reduced by ' + str(damage) + '.')
            target.hp -= damage
            if target.hp < 0:
                target.hp = 0
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

    def execute_player_turn(self, hero: HeroState) -> None:
        self.message_dialog.add_message('')

        # Check if the hero wakes up
        self.check_wake_up(hero)
        if hero.is_asleep:
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

            # Process encounter menu selection
            if menu_result == 'FIGHT':
                # Determine the target
                # TODO: Allow user to select the monster
                target = random.choice(self.monster_party.get_still_in_combat_members())

                self.message_dialog.add_message(hero.get_name() + ' attacks!')

                # Check for damage and a critical strike
                (damage, is_critical_hit) = hero.get_attack_damage(target)
                if 0 == damage:
                    # TODO: Play sound?
                    self.message_dialog.add_message('A miss! No damage hath been scored!')
                else:
                    if is_critical_hit:
                        # TODO: Play sound?
                        self.message_dialog.add_message('Excellent move!')

                    # Check for a monster dodge
                    if target.is_dodging_attack():
                        AudioPlayer().play_sound('Dragon Warrior [Dragon Quest] SFX (9).wav')
                        self.message_dialog.add_message(
                            'The ' + target.get_name() + ' dodges ' + hero.get_name() + "'s strike.")
                    else:
                        # TODO: Play different sound based on damage of attack
                        AudioPlayer().play_sound('Dragon Warrior [Dragon Quest] SFX (5).wav')
                        self.message_dialog.add_message(
                            'The ' + target.get_name() + "'s hit points reduced by " + str(damage) + '.')
                        target.hp -= damage
                        for flickerTimes in range(10):
                            self.render_monsters([target])
                            pygame.display.flip()
                            pygame.time.Clock().tick(30)

                            self.render_monsters()
                            pygame.display.flip()
                            pygame.time.Clock().tick(30)

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
                    break

            elif menu_result == 'SPELL':
                available_spell_names = self.game_state.get_available_spell_names()
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
                        spell = self.game_state.get_spells()[menu_result]
                        if hero.mp >= spell.mp:
                            hero.mp -= spell.mp

                            AudioPlayer().play_sound('castSpell.wav')
                            SurfaceEffects.flickering(self.game_state.screen)

                            # Determine the target
                            # TODO: Allow user to select the monster
                            target = random.choice(self.monster_party.get_still_in_combat_members())

                            spell_worked = True
                            if hero.does_spell_work(spell, target):
                                if spell.max_hp_recover > 0:
                                    hp_recover = random.randint(spell.min_hp_recover, spell.max_hp_recover)
                                    hero.hp = min(hero.max_hp, hero.hp + hp_recover)
                                elif spell.max_damage_by_hero > 0:
                                    damage = random.randint(spell.min_damage_by_hero,
                                                            spell.max_damage_by_hero)
                                    self.message_dialog.add_message('The ' + target.get_name()
                                                               + "'s hit points reduced by "
                                                               + str(damage) + '.')
                                    target.hp -= damage
                                elif 'SLEEP' == spell.name.upper():
                                    target.is_asleep = True
                                elif 'STOPSPELL' == spell.name.upper():
                                    target.are_spells_blocked = True
                                else:
                                    spell_worked = False
                            else:
                                spell_worked = False

                            if spell_worked:
                                self.message_dialog.add_message(
                                    hero.get_name() + ' cast the spell of ' + spell.name.lower() + '.')
                            else:
                                self.message_dialog.add_message(
                                    hero.get_name() + ' cast the spell of ' + spell.name.lower()
                                    + ' but the spell did not work.')

                            GameDialog.create_encounter_status_dialog(self.hero_party).blit(
                                self.game_state.screen, False)

                        else:
                            self.message_dialog.add_message('Thou dost not have enough magic to cast the spell.')
                            continue
                    menu_dialog.erase(self.game_state.screen, self.background_image, True)
            elif menu_result == 'ITEM':
                print('Items are not implemented', flush=True)
                continue
            else:
                continue

            # If here the turn was successfully completed
            break

        # Check for ran away death or monster death
        if self.still_in_encounter():
            self.message_dialog.blit(self.game_state.screen, True)
            self.gde.wait_for_acknowledgement(self.message_dialog)

    def handle_victory(self) -> None:
        if 0 < self.monster_party.get_defeated_count():
            AudioPlayer().play_sound('17_-_Dragon_Warrior_-_NES_-_Enemy_Defeated.ogg')
            gp = self.monster_party.get_gp()
            xp = self.monster_party.get_xp()
            # TODO: Update text for multiple monster encounters
            self.message_dialog.add_message(
                'Thou has done well in defeating the ' + self.monster_party.members[0].get_name()
                + '. Thy experience increases by ' + str(xp) + '. Thy gold increases by ' + str(gp) + '.')
            self.hero_party.gp += gp
            for hero in self.hero_party.members:
                if hero.is_still_in_combat():
                    hero.xp += xp
                    if hero.level_up_check(self.game_state.get_levels('')):
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
        # TODO: Implement
        pass


def main() -> None:
    from unittest.mock import MagicMock
    mock_game_state = mock.create_autospec(spec=GameStateInterface)

    # Initialize pygame
    pygame.init()
    pygame.font.init()

    # Setup the screen
    win_size_pixels = Point(1280, 960)
    tile_size_pixels = 48
    win_size_tiles = (win_size_pixels / tile_size_pixels).ceil()
    win_size_pixels = win_size_tiles * tile_size_pixels
    screen = pygame.display.set_mode(win_size_pixels, pygame.SRCALPHA | pygame.HWSURFACE)
    clock = pygame.time.Clock()
    pygame.key.set_repeat()

    # Test out game dialog
    GameDialog.init(win_size_tiles, tile_size_pixels)
    level = Level(1, '1', 0, 20, 20, 15, 0)
    hero_party = HeroParty(HeroState('hero', Point(5, 6), Direction.SOUTH, 'CAMDEN', level))


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
