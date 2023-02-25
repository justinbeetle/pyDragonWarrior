#!/usr/bin/env python

from typing import Optional

import os
import pygame

from generic_utils.point import Point

from pygame_utils.audio_player import AudioPlayer
import pygame_utils.game_events as GameEvents

from pydw.game_map import GameMap
from pydw.game_state_interface import GameStateInterface
from pydw.game_types import Direction
from pydw.hero_party import HeroParty
from pydw.hero_state import HeroState


class GameMapViewer:
    def __init__(self, base_path: str) -> None:
        self.is_running = True

        # Initialize pygame
        pygame.init()
        self.audio_player = AudioPlayer()
        self.clock = pygame.time.Clock()

        # Setup to draw maps
        self.tile_size_pixels = 32
        desired_win_size_pixels = Point(2560, 1340)
        if desired_win_size_pixels is None:
            self.screen: pygame.surface.Surface = pygame.display.set_mode(
                (0, 0), pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA
            )
            self.win_size_pixels: Point = Point(self.screen.get_size())
            self.win_size_tiles: Point = self.win_size_pixels // self.tile_size_pixels
        else:
            self.win_size_tiles = desired_win_size_pixels // self.tile_size_pixels
            self.win_size_pixels = self.win_size_tiles * self.tile_size_pixels
            self.screen = pygame.display.set_mode(
                self.win_size_pixels.get_as_int_tuple(), pygame.SRCALPHA
            )
        self.image_pad_tiles = self.win_size_tiles // 2 * 4

        # Initialize GameInfo
        game_xml_path = os.path.join(base_path, "game.xml")
        from pydw.game_info import GameInfo

        self.game_info = GameInfo(
            base_path, game_xml_path, self.tile_size_pixels, self.win_size_pixels
        )

        # Initialize the hero party
        self.hero_party = HeroParty(
            HeroState(
                self.game_info.character_types["hero"],
                Point(),
                Direction.NORTH,
                "Camden",
                20000,
            )
        )

        # Setup a mock game state
        from unittest import mock
        from unittest.mock import MagicMock

        self.mock_game_state = mock.create_autospec(spec=GameStateInterface)
        self.mock_game_state.screen = self.screen
        self.mock_game_state.is_running = self.is_running
        self.mock_game_state.get_game_info = MagicMock(return_value=self.game_info)
        self.mock_game_state.get_image_pad_tiles = MagicMock(
            return_value=self.image_pad_tiles
        )
        self.mock_game_state.get_hero_party = MagicMock(return_value=self.hero_party)
        self.mock_game_state.check_progress_markers = MagicMock(return_value=True)

    def __del__(self) -> None:
        # Terminate pygame
        self.audio_player.terminate()
        pygame.quit()

    def view_map(self, map_name: str) -> None:
        if not self.is_running:
            return

        self.audio_player.play_music(self.game_info.maps[map_name].music)
        game_map = GameMap(self.mock_game_state, map_name)

        # Center hero party in map
        self.hero_party.light_diameter = self.game_info.maps[map_name].light_diameter
        self.hero_party.set_pos(Point(-1, -1), Direction.SOUTH)
        game_map.bounds_check_pc_position()

        done_with_map = False
        god_mode = False

        while self.is_running and not done_with_map:
            for event in GameEvents.get_events(True):
                move_direction: Optional[Direction] = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                    elif event.key == pygame.K_RETURN:
                        done_with_map = True
                    elif event.key == pygame.K_EQUALS:
                        if self.hero_party.light_diameter is not None:
                            self.hero_party.light_diameter += 1
                    elif event.key == pygame.K_MINUS:
                        if self.hero_party.light_diameter is not None:
                            self.hero_party.light_diameter = max(
                                1, self.hero_party.light_diameter - 1
                            )
                    elif event.key == pygame.K_e:
                        if game_map.is_facing_locked_item():
                            print("Opened door", flush=True)
                            game_map.open_locked_item()
                        else:
                            for decoration in game_map.get_decorations():
                                if (
                                    decoration.type is not None
                                    and decoration.type.remove_with_search
                                ):
                                    print("Removing decoration", decoration, flush=True)
                                    game_map.remove_decoration(decoration)
                                else:
                                    print(
                                        "Not removing decoration",
                                        decoration,
                                        flush=True,
                                    )
                    elif event.key == pygame.K_b:
                        game_map.dump_encounter_backgrounds()
                    elif event.key == pygame.K_g:
                        god_mode = not god_mode
                    else:
                        move_direction = Direction.get_optional_direction(event.key)
                elif event.type == pygame.QUIT:
                    self.is_running = False

                if move_direction is not None:
                    if (
                        self.hero_party.members[0].curr_pos_dat_tile
                        != self.hero_party.members[0].dest_pos_dat_tile
                    ):
                        print(
                            "Ignoring move as another move is already in progress",
                            flush=True,
                        )
                        continue
                    if move_direction != self.hero_party.members[0].direction:
                        self.hero_party.members[0].direction = move_direction
                    else:
                        dest_tile = (
                            self.hero_party.members[0].curr_pos_dat_tile
                            + move_direction.get_vector()
                        )
                        if god_mode or game_map.can_move_to_tile(dest_tile):
                            self.hero_party.members[0].dest_pos_dat_tile = dest_tile
                            tile_name = game_map.get_tile_info().name
                            encounter_background = game_map.get_encounter_background(
                                dest_tile
                            )
                            print(
                                f"Moved to {dest_tile} of type {tile_name} and background {encounter_background}",
                                flush=True,
                            )

            updated = False
            while (
                not updated
                or self.hero_party.members[0].curr_pos_dat_tile
                != self.hero_party.members[0].dest_pos_dat_tile
            ):
                updated = True
                game_map.update()
                game_map.draw()
                pygame.display.flip()
                self.clock.tick(30)


def main() -> None:
    # Iterate through and render the different maps
    viewer = GameMapViewer(
        os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    )
    for map_name in viewer.game_info.maps:
        viewer.view_map(map_name)


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
