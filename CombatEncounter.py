#!/usr/bin/env python

from typing import Optional

import pygame

from AudioPlayer import AudioPlayer
from GameDialog import GameDialog
from GameDialogEvaluator import GameDialogEvaluator
from GameStateInterface import GameStateInterface
from GameTypes import DialogType
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
    def static_init(default_encounter_music: str):
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
            self.traverse_dialog(self.message_dialog, self.approach_dialog, depth=1)
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
        self.wait_for_acknowledgement(self.message_dialog)

        # Restore initial background image and key repeat settings
        self.game_state.screen.blit(self.background_image, (0, 0))
        pygame.key.set_repeat(orig_repeat1, orig_repeat2)

        # Call game_state.draw_map but manually flip the buffer for the case where this method is a mock
        self.game_state.draw_map(False)
        pygame.display.flip()

    def render_monsters(self) -> None:
        # Render the encounter background
        encounter_image_size_px = Point(self.encounter_image.get_size())
        encounter_image_dest_px = Point(
            (self.game_state.win_size_px.w - encounter_image_size_px.w) / 2,
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
                monster_image_dest_px = Point(monster_pos_x,
                                              encounter_image_dest_px.y + encounter_image_size_px.y
                                              - monster.monster_info.image.get_height()
                                              - self.game_state.get_tile_size_pixels())
                self.game_state.screen.blit(monster.monster_info.monster_info.image, monster_image_dest_px)
            monster_pos_x += CombatEncounter.MONSTER_SPACING_PIXELS + monster.monster_info.image.get_width()

    def get_turn_order(self) -> List[Union[HeroState,MonsterState]]:
        # TODO: In the future rework this method to better support parties with multiple members
        turn_order = []
        skip_hero_party = False
        if self.is_first_turn:
            self.is_first_turn = False
            skip_hero_party = self.monster_party.members[0].has_initiative(self.hero_party.main_character)
        if skip_hero_party:
            self.message_dialog.add_message('The ' + self.monster_party.members[0].get_name() + ' attacked before '
                                            + self.game_state.hero_party.main_character.get_name() + ' was ready.')
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

    def execute_monster_turn(self, monster: MonsterState) -> None:
        # TODO: Implement
        pass

    def execute_player_turn(self, hero: HeroState) -> None:
        # TODO: Implement
        pass

    def handle_victory(self) -> None:
        if 0 < self.monster_party.get_defeated_count():
            AudioPlayer().play_sound('17_-_Dragon_Warrior_-_NES_-_Enemy_Defeated.ogg')
            gp = self.monster_party.get_gp()
            xp = self.monster_party.get_xp()
            # TODO: Update text for multiple monster encounters
            self.message_dialog.add_message(
                'Thou has done well in defeating the ' + self.monster_party[0].get_name()
                + '. Thy experience increases by ' + str(xp) + '. Thy gold increases by ' + str(gp) + '.')
            self.hero_party.gp += gp
            for hero in self.hero_party.members:
                if hero.is_still_in_combat():
                    hero.xp += xp
                    if hero.level_up_check(self.game_state.get_levels()):
                        self.wait_for_acknowledgement(self.message_dialog)
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
            self.traverse_dialog(self.message_dialog, self.run_away_dialog)

    def handle_death(self) -> None:
        # TODO: Implement
        pass

        '''
        # Display status, command prompt dialog, and command menu
        is_start = True
        while self.game_state.is_running:
            GameDialog.create_encounter_status_dialog(self.game_state.pc).blit(self.game_state.screen, False)

            # The first time through, check to see if the monster runs away or takes the initiative
            skip_hero_attack = False
            if is_start:
                is_start = False

                # Check if the monster is going to run away.
                if monster.should_run_away(self.game_state.pc):
                    # TODO: Play sound?
                    monster.has_run_away = True
                    message_dialog.add_message('The ' + monster.get_name() + ' is running away.')
                    break

                # Check if the monster takes the initiative and attacks first
                if monster.has_initiative(self.game_state.pc):
                    message_dialog.add_message('The ' + monster.get_name() + ' attacked before '
                                               + self.game_state.pc.get_name() + ' was ready')
                    skip_hero_attack = True

            # Perform player character turn
            if not skip_hero_attack:

                message_dialog.add_message('')

                if self.game_state.pc.is_asleep:
                    # Check if player wakes up
                    if self.game_state.pc.is_still_asleep():
                        if self.game_state.pc.turns_asleep == 1:
                            message_dialog.add_message(self.game_state.pc.get_name() + ' is asleep.')
                        else:
                            message_dialog.add_message(self.game_state.pc.get_name() + ' is still asleep.')
                    else:
                        message_dialog.add_message(self.game_state.pc.get_name() + ' awakes.')

                while self.game_state.is_running and not self.game_state.pc.is_asleep:

                    message_dialog.add_encounter_prompt()
                    message_dialog.blit(self.game_state.screen, True)
                    menu_result = None
                    while self.game_state.is_running and menu_result is None:
                        menu_result = self.get_menu_result(message_dialog)
                    if not self.game_state.is_running:
                        break

                    # Process encounter menu selection
                    if menu_result == 'FIGHT':

                        message_dialog.add_message(self.game_state.pc.name + ' attacks!')

                        # Check for a critical strike
                        if self.game_state.pc.critical_hit_check(monster):
                            # TODO: Play sound?
                            message_dialog.add_message('Excellent move!')
                            damage = self.game_state.pc.calc_critical_hit_damage_to_monster(monster)
                        else:
                            damage = self.game_state.pc.calc_regular_hit_damage_to_monster(monster)

                        # Check for a monster dodge
                        if 0 == damage or monster.is_dodging_attack():
                            audio_player.play_sound('Dragon Warrior [Dragon Quest] SFX (9).wav')
                            message_dialog.add_message(
                                'The ' + monster.get_name() + ' dodges ' + self.game_state.pc.get_name() + "'s strike.")
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
                        if monster.is_blocking_escape(self.game_state.pc):
                            # TODO: Play sound?
                            message_dialog.add_message(
                                self.game_state.pc.get_name() + ' started to run away but was blocked in front.')
                        else:
                            audio_player.play_sound('runAway.wav')
                            message_dialog.add_message(self.game_state.pc.get_name() + ' started to run away.')

                            if run_away_dialog is not None:
                                self.traverse_dialog(message_dialog, run_away_dialog, depth=1)

                            self.game_state.pc.has_run_away = True
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
                            menu_result = self.get_menu_result(menu_dialog)
                            # print( 'menu_result =', menu_result, flush=True )
                            if menu_result is not None:
                                spell = self.game_state.game_info.spells[menu_result]
                                if self.game_state.pc.mp >= spell.mp:
                                    self.game_state.pc.mp -= spell.mp

                                    AudioPlayer().play_sound('castSpell.wav')
                                    SurfaceEffects.flickering(self.game_state.screen)

                                    spell_worked = True
                                    if self.game_state.pc.does_spell_work(spell, monster):
                                        if spell.max_hp_recover > 0:
                                            hp_recover = random.randint(spell.min_hp_recover, spell.max_hp_recover)
                                            self.game_state.pc.hp = min(self.game_state.pc.level.hp,
                                                                        self.game_state.pc.hp + hp_recover)
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
                                            self.game_state.pc.name + ' cast the spell of ' + spell.name.lower() + '.')
                                    else:
                                        message_dialog.add_message(
                                            self.game_state.pc.get_name() + ' cast the spell of ' + spell.name.lower()
                                            + ' but the spell did not work.')

                                    GameDialog.create_encounter_status_dialog(self.game_state.pc).blit(
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
                if not self.game_state.pc.is_still_in_combat() or not monster.is_alive():
                    break

                message_dialog.blit(self.game_state.screen, True)
                self.wait_for_acknowledgement(message_dialog)

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
            if monster.should_run_away(self.game_state.pc):
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
                if MonsterActionEnum.SLEEP == monster_action.type and self.game_state.pc.is_asleep:
                    continue
                if MonsterActionEnum.STOPSPELL == monster_action.type and self.game_state.pc.are_spells_blocked:
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
                if self.game_state.pc.armor is not None:
                    # TODO: Allow damage reduction from other sources
                    damage = round(damage * self.game_state.pc.armor.hurt_dmg_modifier)
                if not monster.does_spell_work(spell, self.game_state.pc):
                    message_dialog.add_message('But that spell hath been blocked.')
                    damage = 0
            elif chosen_monster_action == MonsterActionEnum.SLEEP:
                AudioPlayer().play_sound('castSpell.wav')
                SurfaceEffects.flickering(self.game_state.screen)
                message_dialog.add_message('The ' + monster.get_name() + ' chants the spell of sleep.')
                if monster.does_spell_work(self.game_state.game_info.spells['Sleep'], self.game_state.pc):
                    message_dialog.add_message('Thou art asleep.')
                    self.game_state.pc.is_asleep = True
                else:
                    message_dialog.add_message('But that spell hath been blocked.')
            elif chosen_monster_action == MonsterActionEnum.STOPSPELL:
                AudioPlayer().play_sound('castSpell.wav')
                SurfaceEffects.flickering(self.game_state.screen)
                message_dialog.add_message('The ' + monster.get_name() + ' chants the spell of stopspell.')
                if monster.does_spell_work(self.game_state.game_info.spells['Stopspell'], self.game_state.pc):
                    message_dialog.add_message(self.game_state.pc.name + "'s spells hath been blocked.")
                    self.game_state.pc.are_spells_blocked = True
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
                if self.game_state.pc.armor is not None:
                    # TODO: Allow damage reduction from other sources
                    damage = round(damage * self.game_state.pc.armor.fire_dmg_modifier)
            else:  # chosen_monster_action == MonsterActionEnum.ATTACK
                damage = self.game_state.pc.calc_hit_damage_from_monster(monster)
                if 0 == damage:
                    # TODO: Play sound?
                    message_dialog.add_message(
                        'The ' + monster.get_name() + ' attacks! ' + self.game_state.pc.name + ' dodges the strike.')
                else:
                    # TODO: Play different sound based on strength of attack
                    audio_player.play_sound('Dragon Warrior [Dragon Quest] SFX (5).wav')
                    message_dialog.add_message('The ' + monster.get_name() + ' attacks!')

            if damage != 0:
                message_dialog.add_message('Thy hit points reduced by ' + str(damage) + '.')
                self.game_state.pc.hp -= damage
                if self.game_state.pc.hp < 0:
                    self.game_state.pc.hp = 0
                for flickerTimes in range(10):
                    offset_pixels = Point(damage_flicker_pixels, damage_flicker_pixels)
                    self.game_state.screen.blit(orig_screen, (0, 0))
                    self.game_state.screen.blit(encounter_image, encounter_image_dest_pixels)
                    self.game_state.screen.blit(monster.monster_info.image, monster_image_dest_pixels)
                    GameDialog.create_encounter_status_dialog(self.game_state.pc).blit(self.game_state.screen, False,
                                                                                       offset_pixels)
                    message_dialog.blit(self.game_state.screen, True, offset_pixels)
                    pygame.time.Clock().tick(30)
                    self.game_state.screen.blit(orig_screen, (0, 0))
                    self.game_state.screen.blit(encounter_image, encounter_image_dest_pixels)
                    self.game_state.screen.blit(monster.monster_info.image, monster_image_dest_pixels)
                    GameDialog.create_encounter_status_dialog(self.game_state.pc).blit(self.game_state.screen, False)
                    message_dialog.blit(self.game_state.screen, True)
                    pygame.time.Clock().tick(30)

                # Check for player death
                if self.game_state.pc.hp <= 0:
                    break

        audio_player.stop_music()
        if self.game_state.pc.hp <= 0:
            self.check_for_player_death(message_dialog)
        elif monster.hp <= 0:
            audio_player.play_sound('17_-_Dragon_Warrior_-_NES_-_Enemy_Defeated.ogg')
            self.game_state.draw_map(False)
            self.game_state.screen.blit(encounter_image, encounter_image_dest_pixels)
            message_dialog.add_message(
                'Thou has done well in defeating the ' + monster.get_name() + '. Thy experience increases by ' + str(
                    monster.xp) + '. Thy gold increases by ' + str(monster.gp) + '.')
            self.game_state.pc.gp += monster.gp
            self.game_state.pc.xp += monster.xp
            GameDialog.create_exploring_status_dialog(self.game_state.pc).blit(self.game_state.screen, False)
            if self.game_state.pc.level_up_check(self.game_state.game_info.levels):
                self.wait_for_acknowledgement(message_dialog)
                audio_player.play_sound('18_-_Dragon_Warrior_-_NES_-_Level_Up.ogg')
                message_dialog.add_message(
                    '\nCourage and wit have served thee well. Thou hast been promoted to the next level.')
                GameDialog.create_exploring_status_dialog(self.game_state.pc).blit(self.game_state.screen, False)

            message_dialog.blit(self.game_state.screen, True)

            if victory_dialog is not None:
                self.traverse_dialog(message_dialog, victory_dialog)

        self.wait_for_acknowledgement(message_dialog)

        # Restore initial key repeat settings
        pygame.key.set_repeat(orig_repeat1, orig_repeat2)

        # Draw the map
        if self.game_state.pc.hp > 0:
            self.game_state.draw_map(True)
        '''


def main() -> None:
    # TODO: Add test
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
