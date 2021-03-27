#!/usr/bin/env python

from typing import Dict, List, Optional

import math
import pygame
import pyscroll
import random

from AudioPlayer import AudioPlayer
from GameStateInterface import GameStateInterface
from GameTypes import CharacterType, Direction, MapDecoration, NpcInfo, Tile
from HeroParty import HeroParty
from HeroState import HeroState
from LegacyMapData import LegacyMapData
from PaddedTiledMapData import PaddedTiledMapData
from Point import Point
from MapCharacterState import MapCharacterState
from NpcState import NpcState


class MapSprite(pygame.sprite.Sprite):
    image_pad_tiles = Point()
    tile_size_pixels = 16
    image_px_step_size = 4

    def __init__(self) -> None:
        super().__init__()

    def get_rect_from_tile(self, tile: Point):
        return self.image.get_rect().move((MapSprite.image_pad_tiles + tile) * MapSprite.tile_size_pixels)


class MapDecorationSprite(MapSprite):
    def __init__(self, decoration: MapDecoration) -> None:
        super().__init__()
        self.decoration = decoration
        self.image = self.decoration.type.image
        self.rect = self.get_rect_from_tile(self.decoration.point)

        # Modified the rect to center the decoration horizontally and to have the base of it aligned with the bottom
        # of its assigned tile.
        self.rect.x = int(self.rect.x + (MapSprite.tile_size_pixels - self.image.get_width()) / 2)
        self.rect.y = int(self.rect.y + MapSprite.tile_size_pixels - self.image.get_height())


class CharacterSprite(MapSprite):

    def __init__(self, character: MapCharacterState) -> None:
        super().__init__()
        self.character = character
        self.phase = 0
        self.update_count = 0
        self.updates_per_phase_change = 20  # TODO: Make this a parameter of a character

        self.image = self.get_image()
        self.rect = self.get_rect()

    def get_image(self) -> pygame.Surface:
        return self.character.character_type.images[self.character.direction][self.phase]

    def get_rect(self):
        char_rect = self.image.get_rect()
        char_rect.midbottom = self.get_rect_from_tile(self.character.curr_pos_dat_tile).move(
            self.character.curr_pos_offset_img_px).midbottom
        return char_rect

    def update(self, game_map):
        # Move the character in steps to the destination tile
        if self.character.curr_pos_dat_tile != self.character.dest_pos_dat_tile:
            direction_vector = self.character.direction.get_vector()
            self.character.curr_pos_offset_img_px += direction_vector * MapSprite.image_px_step_size
            if self.character.curr_pos_offset_img_px.mag() / MapSprite.tile_size_pixels >= direction_vector.mag():
                self.character.curr_pos_dat_tile = self.character.dest_pos_dat_tile
                self.character.curr_pos_offset_img_px = Point(0, 0)

        # Check for phase updates
        self.update_count += 1
        if self.update_count % self.updates_per_phase_change == 0:
            self.phase = (self.phase + 1) % self.character.character_type.num_phases

        # Update the image and rect
        self.image = self.get_image()
        self.rect = self.get_rect()

    @staticmethod
    def get_tile_movement_steps() -> int:
        return int(math.ceil(MapSprite.tile_size_pixels / MapSprite.image_px_step_size))


class HeroSprite(CharacterSprite):
    character_types: Dict[str, CharacterType] = {}

    def __init__(self, hero: HeroState, hero_party: HeroParty) -> None:
        self.hero_party = hero_party
        super().__init__(hero)

    def get_image(self) -> pygame.Surface:
        if self.character.hp <= 0:
            character_images = HeroSprite.character_types['ghost'].images
        elif self.character.character_type.name == 'hero':
            # TODO: Configurable way to handle the PC image mappings
            if self.character == self.hero_party.main_character and self.hero_party.has_item('PM_Carrying_Princess'):
                character_images = HeroSprite.character_types['hero_carrying_princess'].images
            elif self.character.weapon is not None and self.character.shield is not None:
                character_images = HeroSprite.character_types['hero_sword_and_shield'].images
            elif self.character.weapon is not None:
                character_images = HeroSprite.character_types['hero_sword'].images
            elif self.character.shield is not None:
                character_images = HeroSprite.character_types['hero_shield'].images
            else:
                character_images = HeroSprite.character_types['hero'].images
        else:
            character_images = self.character.character_type.images
        return character_images[self.character.direction][self.phase]


class NpcSprite(CharacterSprite):
    def __init__(self, character: NpcState) -> None:
        self.updates_per_npc_move = 60  # TODO: Make this a parameter of a character
        super().__init__(character)

    def update(self, game_map):
        if self.character.npc_info.walking:
            # Start moving NPC by setting a destination tile
            if (self.update_count % self.updates_per_npc_move) == self.updates_per_npc_move - 1:
                # TODO: Determine where to move instead of blindly moving forward
                self.character.direction = random.choice(list(Direction))
                dest_tile = self.character.curr_pos_dat_tile + self.character.direction.get_vector()
                if game_map.can_move_to_tile(dest_tile, True, True, True, self.character.curr_pos_dat_tile):
                    self.character.dest_pos_dat_tile = dest_tile

        super().update(game_map)


class GameMap:
    def __init__(self,
                 game_state: GameStateInterface,
                 map_name: str,
                 map_decorations: Optional[List[MapDecoration]] = None,
                 npcs: Optional[List[NpcState]] = None) -> None:
        self.game_state = game_state
        print('map_name =', map_name)
        self.map = self.game_state.get_game_info().maps[map_name]

        # Set the decorations
        if map_decorations is None:
            self.map_decorations = self.map.map_decorations
        else:
            self.map_decorations = map_decorations

        # Set the NPCs
        self.npcs: List[NpcState] = npcs
        if self.npcs is None:
            for npc in self.map.npcs:
                self.npcs.append(NpcState(npc))

        # Create the map data
        if self.map.tiled_filename is not None:
            self.map_data = PaddedTiledMapData(self.map.tiled_filename,
                                               self.game_state.get_image_pad_tiles(),
                                               desired_tile_size=self.game_state.get_game_info().tile_size_pixels)
        else:
            self.map_data = LegacyMapData(self.game_state.get_game_info(),
                                          self.map.name,
                                          self.game_state.get_image_pad_tiles())

        # Create renderer
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, self.game_state.screen.get_size())

        # Create the pyscroll group to support character and decoration sprites
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=self.map_data.decoration_layer)

        MapSprite.image_pad_tiles = self.game_state.get_image_pad_tiles()
        MapSprite.tile_size_pixels = self.game_state.get_game_info().tile_size_pixels
        MapSprite.image_px_step_size = self.game_state.get_game_info().image_px_step_size
        HeroSprite.character_types = self.game_state.get_game_info().character_types

        # Add decorations to the group
        for decoration in self.map_decorations:
            if decoration.type is not None:
                self.group.add(MapDecorationSprite(decoration), layer=self.map_data.decoration_layer)

        # Add characters to the group
        hero_party = self.game_state.get_hero_party()
        for hero in reversed(hero_party.members):
            self.group.add(HeroSprite(hero, hero_party), layer=self.map_data.character_layer)
        for npc in self.npcs:
            self.group.add(NpcSprite(npc), layer=self.map_data.character_layer)

    def size(self, with_padding=False) -> Point:
        # Doesn't include padding, just the size of data size of the map
        if with_padding:
            return Point(self.map_data.map_size)
        else:
            return Point(self.map_data.map_size) - 2 * self.game_state.get_image_pad_tiles()

    def update(self):
        self.group.update(self)

    def draw(self, surface: Optional[pygame.Surface] = None):
        if surface is None:
            surface = self.game_state.screen

        # Center the map on the PC
        self.group.center((self.game_state.get_image_pad_tiles() + Point(0.5, 0.5) +
                           self.game_state.get_hero_party().get_curr_pos_dat_tile()) *
                           self.map_data.tile_size + self.game_state.get_hero_party().get_curr_pos_offset_img_px())

        # Detect if the hero is eclipsed by the over layer(s).  If so, do not render those layers.
        if self.is_interior():
            layers_to_render = self.map_data.base_tile_layers
        else:
            layers_to_render = self.map_data.all_tile_layers
        if layers_to_render != self.map_data.visible_tile_layers:
            self.map_data.set_tile_layers_to_render(layers_to_render)
            self.map_layer.redraw_tiles(self.map_layer._buffer)

        # tell the map_layer (BufferedRenderer) to draw to the surface
        # the draw function requires a rect to draw to.
        self.group.draw(surface)

        if self.game_state.get_hero_party().light_diameter is not None:
            light_radius_px = self.game_state.get_hero_party().light_diameter \
                                * self.game_state.get_game_info().tile_size_pixels / 2

            # Left
            surface.fill(pygame.Color('black'), pygame.Rect(0,
                                                            0,
                                                            surface.get_width() / 2 - light_radius_px,
                                                            surface.get_height()))

            # Right
            surface.fill(pygame.Color('black'), pygame.Rect(surface.get_width() / 2 + light_radius_px,
                                                            0,
                                                            surface.get_width() / 2 - light_radius_px,
                                                            surface.get_height()))

            # Top
            surface.fill(pygame.Color('black'), pygame.Rect(0,
                                                            0,
                                                            surface.get_width(),
                                                            surface.get_height() / 2 - light_radius_px))

            # Bottom
            surface.fill(pygame.Color('black'), pygame.Rect(0,
                                                            surface.get_height() / 2 + light_radius_px,
                                                            surface.get_width(),
                                                            surface.get_height() / 2 - light_radius_px))

    def get_tile_info(self, tile: Optional[Point] = None) -> Tile:
        if tile is None:
            tile = self.game_state.get_hero_party().main_character.curr_pos_dat_tile

        if isinstance(self.map_data, PaddedTiledMapData):
            tile_name = None
            for l in self.map_data.visible_tile_layers:
                tile_properties = self.map_data.tmx.get_tile_properties(tile.x, tile.y, l)
                if tile_properties is not None and 'type' in tile_properties and len(tile_properties['type']) > 0:
                    tile_name = tile_properties['type']
            if tile_name is not None and tile_name in self.game_state.get_game_info().tiles:
                return self.game_state.get_game_info().tiles[tile_name]
        else:
            return self.game_state.get_game_info().tiles[
                self.game_state.get_game_info().tile_symbols[
                    self.map.dat[int(tile.y)][int(tile.x)]]]

        # Return a default, walkable tile as a default
        return Tile('DEFAULT TILE',
                    '?',
                    [],
                    True,
                    False,
                    0,
                    0,
                    1.0,
                    1.0)

    def get_decorations(self, tile: Optional[Point] = None) -> List[MapDecoration]:
        decorations = []
        if tile is None:
            tile = self.game_state.get_hero_party().get_curr_pos_dat_tile()
        for decoration in self.map_decorations:
            if decoration.point == tile and self.game_state.check_progress_markers(
                    decoration.progress_marker, decoration.inverse_progress_marker):
                decorations.append(decoration)
        return decorations

    def get_npc_to_talk_to(self) -> Optional[NpcInfo]:
        talk_dest_dat_tile = self.game_state.hero_party.members[0].curr_pos_dat_tile \
                             + self.game_state.hero_party.members[0].direction.get_vector()
        talk_dest_tile_type = self.game_state.get_tile_info(talk_dest_dat_tile)
        if talk_dest_tile_type.can_talk_over:
            talk_dest_dat_tile = talk_dest_dat_tile \
                                 + self.game_state.hero_party.members[0].direction.get_vector()

        for sprite in self.group:
            if not isinstance(sprite, NpcSprite):
                continue
            npc_info = sprite.character.npc_info
            if (npc_info is not None and
                    (talk_dest_dat_tile == sprite.character.curr_pos_dat_tile or
                     talk_dest_dat_tile == sprite.character.dest_pos_dat_tile)):
                # NPC should turn to face you if they have something to say
                if npc_info.dialog is not None:
                    sprite.character.curr_pos_dat_tile = sprite.character.dest_pos_dat_tile = talk_dest_dat_tile
                    sprite.character.curr_pos_offset_img_px = Point(0, 0)
                    sprite.character.direction = self.game_state.hero_party.members[0].direction.get_opposite()
                    sprite.update_count = 0
                    sprite.update(self)

                    # Stationary characters should resume looking in the default direction after talking to the player.
                    if not npc_info.walking:
                        sprite.character.direction = npc_info.direction

                return npc_info

        return None

    def get_tile_degrees_of_freedom(self,
                                    tile: Point,
                                    enforce_npc_hp_penalty_limit: bool,
                                    prev_tile: Optional[Point]) -> int:
        degrees_of_freedom = 0
        for x in [tile.x - 1, tile.x + 1]:
            if self.can_move_to_tile(Point(x, tile.y), enforce_npc_hp_penalty_limit, False, True, prev_tile):
                degrees_of_freedom += 1
        for y in [tile.y - 1, tile.y + 1]:
            if self.can_move_to_tile(Point(tile.x, y), enforce_npc_hp_penalty_limit, False, True, prev_tile):
                degrees_of_freedom += 1
        # print('DOF for tile', tile, 'is', degrees_of_freedom, flush=True)
        return degrees_of_freedom

    def can_move_to_tile(self,
                         tile: Point,
                         enforce_npc_hp_penalty_limit: bool = False,
                         enforce_npc_dof_limit: bool = False,
                         is_npc: bool = False,
                         prev_tile: Optional[Point] = None) -> bool:
        movement_allowed = False

        # Check if native tile allows movement
        if 0 <= tile.x < self.size().w and 0 <= tile.y < self.size().h:
            movement_allowed = self.get_tile_info(tile).walkable or \
                not self.get_tile_info(self.game_state.get_hero_party().get_curr_pos_dat_tile()).walkable

        # Check if a decoration prevents movement to the tile that otherwise allowed movement
        if movement_allowed:
            for decoration in self.map_decorations:
                if decoration.type is not None and not decoration.type.walkable and decoration.overlaps(tile):
                    movement_allowed = False
                    # print('Movement not allowed: decoration not walkable', decoration, flush=True)
                    break
        # Check if a decoration allows movement to a tile to which movement was otherwise prevented
        if not movement_allowed:
            for decoration in self.map_decorations:
                if decoration.type is not None and decoration.type.walkable and decoration.overlaps(tile):
                    movement_allowed = True
                    # print('Movement allowed: decoration walkable', decoration, flush=True)
                    break

        if movement_allowed:
            if movement_allowed and enforce_npc_hp_penalty_limit and self.get_tile_info(tile).hp_penalty != 0:
                movement_allowed = False
                # print('Movement not allowed: NPC HP penalty limited', flush=True)
            if movement_allowed and enforce_npc_hp_penalty_limit and prev_tile is not None and self.is_interior(
                    tile) != self.is_interior(prev_tile):
                movement_allowed = False
                # print('Movement not allowed: NPC cannot move between interior and exterior tiles', flush=True)
            if (movement_allowed
                    and enforce_npc_dof_limit
                    and self.get_tile_degrees_of_freedom(tile, enforce_npc_hp_penalty_limit, prev_tile) < 2):
                movement_allowed = False
                # print('Movement not allowed: NPC degree-of-freedom limit not met', flush=True)
            if movement_allowed and is_npc:
                for hero in self.game_state.get_hero_party().members:
                    if tile == hero.curr_pos_dat_tile or tile == hero.dest_pos_dat_tile:
                        movement_allowed = False
                        # print('Movement not allowed: PC in the way', flush=True)
                        break
            if movement_allowed:
                for npc in self.npcs:
                    if tile == npc.curr_pos_dat_tile or tile == npc.dest_pos_dat_tile:
                        movement_allowed = False
                        # print('Movement not allowed: NPC in the way', flush=True)
                        break
        # else:
        #   print('Movement not allowed: tile not walkable', flush=True)

        return movement_allowed

    def bounds_check_pc_position(self) -> None:
        # Bounds checking to ensure a valid hero/center position
        curr_pos_dat_tile = self.game_state.get_hero_party().get_curr_pos_dat_tile()
        if (curr_pos_dat_tile is None
                or curr_pos_dat_tile.x < 1
                or curr_pos_dat_tile.y < 1
                or curr_pos_dat_tile.x > self.size().w - 1
                or curr_pos_dat_tile.y > self.size().h - 1):
            print('ERROR: Invalid hero position, defaulting to middle tile', flush=True)
            self.game_state.get_hero_party().set_pos(Point(self.size().w // 2,
                                                           self.size().h // 2),
                                                     Direction.SOUTH)

    def is_interior(self, pos_dat_tile: Optional[Point] = None) -> bool:
        if pos_dat_tile is None:
            pos_dat_tile = self.game_state.get_hero_party().get_curr_pos_dat_tile()
        for l in self.map_data.overlay_tile_layers:
            if self.map_data._get_tile_image(pos_dat_tile.x, pos_dat_tile.y, l,
                                             image_indexing=False, limit_to_visible=False) is not None:
                return True
        return False

    def is_exterior(self, pos_dat_tile: Optional[Point] = None) -> bool:
        return not self.is_interior(pos_dat_tile)

    def is_facing_door(self) -> bool:
        door_open_dest_dat_tile = self.game_state.get_hero_party().get_curr_pos_dat_tile() \
                                  + self.game_state.get_hero_party().get_direction().get_vector()
        for decoration in self.map_decorations:
            if (door_open_dest_dat_tile == decoration.point
                    and decoration.type is not None
                    and decoration.type.remove_with_key):
                return True
        return False

    def open_door(self) -> None:
        door_open_dest_dat_tile = self.game_state.get_hero_party().get_curr_pos_dat_tile() \
                                  + self.game_state.get_hero_party().get_direction().get_vector()
        for decoration in self.map_decorations:
            if (door_open_dest_dat_tile == decoration.point
                    and decoration.type is not None
                    and decoration.type.remove_with_key):
                if decoration.type.remove_sound is not None:
                    AudioPlayer().play_sound(decoration.type.remove_sound)
                self.remove_decoration(decoration)

    def remove_decoration(self, decoration: MapDecoration) -> None:
        # Remove the decoration from the map (if present)
        if decoration in self.map_decorations:
            self.map_decorations.remove(decoration)

            for sprite in self.group.remove_sprites_of_layer(self.map_data.decoration_layer):
                if sprite.decoration != decoration:
                    self.group.add(sprite, layer=self.map_data.decoration_layer)


class MapViewer:
    def __init__(self) -> None:
        self.is_running = True

        # Initialize pygame
        pygame.init()
        self.audio_player = AudioPlayer()
        self.clock = pygame.time.Clock()

        # Setup to draw maps
        self.tile_size_pixels = 60
        desired_win_size_pixels = Point(2560, 1340)
        if desired_win_size_pixels is None:
            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA)
            self.win_size_pixels = Point(self.screen.get_size())
            self.win_size_tiles = (self.win_size_pixels / self.tile_size_pixels).floor()
        else:
            self.win_size_tiles = (desired_win_size_pixels / self.tile_size_pixels).floor()
            self.win_size_pixels = self.win_size_tiles * self.tile_size_pixels
            self.screen = pygame.display.set_mode(self.win_size_pixels.getAsIntTuple(), pygame.SRCALPHA)
        self.image_pad_tiles = self.win_size_tiles // 2 * 4

        # Initialize GameInfo
        import os
        base_path = os.path.split(os.path.abspath(__file__))[0]
        game_xml_path = os.path.join(base_path, 'game.xml')
        from GameInfo import GameInfo
        self.game_info = GameInfo(base_path, game_xml_path, self.tile_size_pixels)

        # Initialize the hero party
        self.hero_party = HeroParty(
            HeroState(self.game_info.character_types['hero'], Point(), Direction.NORTH, 'Camden', 20000))

        # Setup a mock game state
        from unittest import mock
        from unittest.mock import MagicMock
        self.mock_game_state = mock.create_autospec(spec=GameStateInterface)
        self.mock_game_state.screen = self.screen
        self.mock_game_state.is_running = self.is_running
        self.mock_game_state.get_game_info = MagicMock(return_value=self.game_info)
        self.mock_game_state.get_image_pad_tiles = MagicMock(return_value=self.image_pad_tiles)
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

        import GameEvents
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
                            self.hero_party.light_diameter = max(1, self.hero_party.light_diameter-1)
                    elif event.key == pygame.K_e:
                        if game_map.is_facing_door():
                            print('Opened door', flush=True)
                            game_map.open_door()
                        else:
                            for decoration in game_map.get_decorations():
                                if decoration.type is not None and decoration.type.remove_with_search:
                                    print('Removing decoration', decoration, flush=True)
                                    game_map.remove_decoration(decoration)
                                else:
                                    print('Not removing decoration', decoration, flush=True)

                    else:
                        move_direction = Direction.get_direction(event.key)
                elif event.type == pygame.QUIT:
                    self.is_running = False

                if move_direction is not None:
                    if self.hero_party.members[0].curr_pos_dat_tile != self.hero_party.members[0].dest_pos_dat_tile:
                        print('Ignoring move as another move is already in progress', flush=True)
                        continue
                    if move_direction != self.hero_party.members[0].direction:
                        self.hero_party.members[0].direction = move_direction
                    else:
                        dest_tile = self.hero_party.members[0].curr_pos_dat_tile + move_direction.get_vector()
                        if game_map.can_move_to_tile(dest_tile):
                            self.hero_party.members[0].dest_pos_dat_tile = dest_tile
                            print('moved to tile of type', game_map.get_tile_info().name, flush=True)

            updated = False
            while not updated or \
                    self.hero_party.members[0].curr_pos_dat_tile != self.hero_party.members[0].dest_pos_dat_tile:
                updated = True
                game_map.update()
                game_map.draw()
                pygame.display.flip()
                self.clock.tick(30)


def main() -> None:
    # Iterate through and render the different maps
    viewer = MapViewer()
    for map_name in viewer.game_info.maps:
        viewer.view_map(map_name)


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
