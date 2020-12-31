#!/usr/bin/env python

from typing import Dict, List, Optional

import pygame
import pyscroll

from AudioPlayer import AudioPlayer
from GameStateInterface import GameStateInterface
from GameTypes import CharacterType, Direction, Map, MapDecoration, NpcInfo, Phase, PointTransition, SpecialMonster, Tile
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

    def __init__(self) -> None:
        super().__init__()

    def get_rect_from_tile(self, tile: Point):
        return self.image.get_rect().move((MapSprite.image_pad_tiles + tile) * MapSprite.tile_size_pixels)


class MapDecorationSprite(MapSprite):
    def __init__(self, decoration: MapDecoration) -> None:
        super().__init__()
        self.image = decoration.type.image
        self.rect = self.get_rect_from_tile(decoration.point)

        # Modified the rect to center the decoration horizontally and to have the base of it aligned with the bottom
        # of its assigned tile.
        self.rect.x = int(self.rect.x + (MapSprite.tile_size_pixels - decoration.type.image.get_width()) / 2)
        self.rect.y = int(self.rect.y + MapSprite.tile_size_pixels - decoration.type.image.get_height())


class CharacterSprite(MapSprite):

    def __init__(self, character: MapCharacterState) -> None:
        super().__init__()
        self.character = character
        self.phase = Phase.A
        self.update_count = 0
        self.updates_per_phase_change = 20  # TODO: Make this a parameter of a character

        self.image = self.get_image()
        self.rect = self.get_rect()

    def get_image(self) -> pygame.Surface:
        return self.character.character_type.images[self.character.direction][self.phase]

    def get_rect(self):
        return self.get_rect_from_tile(self.character.curr_pos_dat_tile).move(self.character.curr_pos_offset_img_px)

    def update(self):
        self.update_count += 1
        if self.update_count % self.updates_per_phase_change == 0:
            if self.phase == Phase.A:
                self.phase = Phase.B
            else:
                self.phase = Phase.A

        self.image = self.get_image()
        self.rect = self.get_rect()


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
    def __init__(self, npc_info: NpcInfo) -> None:
        self.npc_info = npc_info
        super().__init__(NpcState(npc_info))

    def can_start_moving(self) -> bool:
        return self.npc_info.walking and \
               self.update_count % self.updates_per_phase_change == self.updates_per_phase_change - 1


class GameMap:
    def __init__(self,
                 game_state: GameStateInterface,
                 map_name: str,
                 map_decorations: Optional[List[MapDecoration]] = None) -> None:
        self.game_state = game_state
        self.map = self.game_state.get_game_info().maps[map_name]
        if map_decorations is None:
            self.map_decorations = self.map.map_decorations
        else:
            self.map_decorations = map_decorations
        self.npcs: List[NpcState] = self.map.npcs  # TODO: Not right as it doesn't take into account progress markers

        # Create the map data
        if self.map.tiled_filename is not None:
            self.map_data = PaddedTiledMapData(self.map.tiled_filename,
                                               self.game_state.get_image_pad_tiles())
        else:
            self.map_data = LegacyMapData(self.game_state.get_game_info(),
                                          self.map.name,
                                          self.game_state.get_image_pad_tiles())

        # Create renderer
        self.map_layer = pyscroll.orthographic.BufferedRenderer(self.map_data, self.game_state.screen.get_size())

        # 16 pixels tiles scaled 5x and 20 pixels decorations scaled 4x
        if isinstance(self.map_data, PaddedTiledMapData):
            self.map_layer.zoom = self.game_state.get_game_info().tile_size_pixels / self.map_data.tile_size[0]

        # pyscroll supports layered rendering.  our map has 3 'under' layers
        # layer 0:  under (water)
        # layer 1:  ground (land)
        # layer 2:  objects (cities, forests, etc.)
        # layer 3:  decorations (chests, doors, and other objects non-permanent objects not present in Tiled)
        # layer 4:  characters
        # layer 5:  over (roofs)
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=3)

        MapSprite.image_pad_tiles = self.game_state.get_image_pad_tiles()
        MapSprite.tile_size_pixels = self.game_state.get_game_info().tile_size_pixels
        HeroSprite.character_types = self.game_state.get_game_info().character_types

        # Add decorations to the group
        for decoration in self.map_decorations:
            if decoration.type is not None:
                self.group.add(MapDecorationSprite(decoration), layer=3)

        # Add characters to the group
        hero_party = self.game_state.get_hero_party()
        for hero in reversed(hero_party.members):
            self.group.add(HeroSprite(hero, hero_party))
        for npc in self.npcs:
            self.group.add(NpcSprite(npc))

    def size(self, with_padding=False) -> Point:
        # Doesn't include padding, just the size of data size of the map
        if with_padding:
            return Point(self.map_data.map_size)
        else:
            return Point(self.map_data.map_size) - 2 * self.game_state.get_image_pad_tiles()

    def update(self):
        # TODO: Move logic for moving an NPC here
        self.group.update()

    def draw(self, surface: Optional[pygame.Surface] = None):
        if surface is None:
            surface = self.game_state.screen

        # Center the map on the PC
        self.group.center((self.game_state.get_image_pad_tiles() +
                           self.game_state.get_hero_party().get_curr_pos_dat_tile()) *
                           self.map_data.tile_size + self.game_state.get_hero_party().get_curr_pos_offset_img_px())

        # Detect if the hero is eclipsed by the over layer(s), if so, do not render those layers
        # TODO: Implement this

        # tell the map_layer (BufferedRenderer) to draw to the surface
        # the draw function requires a rect to draw to.
        self.group.draw(surface)

    def get_tile_info(self, tile: Optional[Point]) -> Tile:
        if tile is None:
            tile = self.game_state.get_hero_party().main_character.curr_pos_dat_tile

        if isinstance(self.map_data, PaddedTiledMapData):
            tile_name = None
            for l in self.map_data.visible_tile_layers:
                tile_properties = self.map_data.tmx.get_tile_properties(tile.x, tile.y, l)
                if 'type' in tile_properties:
                    tile_name = tile_properties['type']
            if tile_name is not None and tile_name in self.game_state.get_game_info().tiles:
                return self.game_state.get_game_info().tiles[tile_name]
        else:
            return self.game_state.get_game_info().tiles[
                self.game_state.get_game_info().tile_symbols[
                    self.game_state.get_game_info().maps[self.map_state.name].dat[int(tile.y)][int(tile.x)]]]

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

    '''
    # Find point transitions for either the specified point or the current position of the player character.
    # If auto is true, only look for automatic point transitions
    def get_point_transition(self, tile: Optional[Point] = None,
                             filter_to_automatic_transitions=False) -> Optional[PointTransition]:
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for point_transition in self.game_info.maps[self.map_state.name].point_transitions:
            if point_transition.src_point == tile and self.check_progress_markers(
                    point_transition.progress_marker, point_transition.inverse_progress_marker):
                if filter_to_automatic_transitions:
                    if point_transition.is_automatic is None and not self.is_light_restricted():
                        # By default, make transitions manual in dark places
                        return point_transition
                    elif point_transition.is_automatic:
                        return point_transition
                else:
                    return point_transition
        return None

    def get_decorations(self, tile: Optional[Point] = None) -> List[MapDecoration]:
        decorations = []
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for decoration in self.map_decorations:
            if decoration.point == tile and self.check_progress_markers(
                    decoration.progress_marker, decoration.inverse_progress_marker):
                decorations.append(decoration)
        return decorations

    def get_special_monster(self, tile: Optional[Point] = None) -> Optional[SpecialMonster]:
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for special_monster in self.game_info.maps[self.map_state.name].special_monsters:
            if special_monster.point == tile and self.check_progress_markers(
                    special_monster.progress_marker, special_monster.inverse_progress_marker):
                print('Found monster at point: ', tile, flush=True)
                return special_monster
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
        if (0 <= tile.x < self.game_info.maps[self.map_state.name].size.w
                and 0 <= tile.y < self.game_info.maps[self.map_state.name].size.h
                and self.get_tile_info(tile).walkable):
            movement_allowed = True

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
                for hero in self.hero_party.members:
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

    def get_tile_monsters(self, tile: Optional[Point] = None) -> List[str]:
        if tile is None:
            tile = self.hero_party.get_curr_pos_dat_tile()
        for mz in self.game_info.maps[self.map_state.name].monster_zones:
            if mz.x <= tile.x <= mz.x + mz.w and mz.y <= tile.y <= mz.y + mz.h:
                # print('in monsterZone of set ' + mz.setName + ':', self.gameInfo.monsterSets[mz.setName], flush=True)
                return self.game_info.monster_sets[mz.name]
        return []

    def is_interior(self, pos_dat_tile: Point) -> bool:
        overlay_dat = self.game_info.maps[self.map_state.name].overlay_dat
        return (overlay_dat is not None
                and overlay_dat[int(pos_dat_tile.y)][int(pos_dat_tile.x)] in self.game_info.tile_symbols)

    def is_exterior(self, pos_dat_tile: Point) -> bool:
        return not self.is_interior(pos_dat_tile)

    def is_facing_door(self) -> bool:
        door_open_dest_dat_tile = self.hero_party.get_curr_pos_dat_tile() \
                                  + self.hero_party.get_direction().get_vector()
        for decoration in self.map_decorations:
            if (door_open_dest_dat_tile == decoration.point
                    and decoration.type is not None
                    and decoration.type.remove_with_key):
                return True
        return False

    def open_door(self) -> None:
        door_open_dest_dat_tile = self.hero_party.get_curr_pos_dat_tile() \
                                  + self.hero_party.get_direction().get_vector()
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
            if self.map_state.name not in self.removed_decorations_by_map:
                self.removed_decorations_by_map[self.map_state.name] = []
            self.removed_decorations_by_map[self.map_state.name].append(decoration)
            self.map_state = self.game_info.get_map_image_info(self.map_state.name,
                                                               self.image_pad_tiles,
                                                               self.map_decorations)

            # Get exterior and interior map images
            self.update_images()

            # Draw the map to the screen
            self.draw_map()

    def set_clipping_for_light_diameter(self) -> None:
        # TODO: Rework for parties
        if self.is_light_restricted() and self.hero_party.light_diameter is not None:
            self.screen.set_clip(
                self.get_tile_region_screen_rect(
                    self.hero_party.get_curr_pos_dat_tile(),
                    self.hero_party.light_diameter / 2,
                    self.hero_party.get_curr_pos_offset_img_px()))
        else:
            self.set_clipping_for_window()

    def set_clipping_for_window(self) -> None:
        self.screen.set_clip(pygame.Rect(0,
                                         0,
                                         self.win_size_pixels.x,
                                         self.win_size_pixels.y))
    '''


class MapViewer:
    def __init__(self) -> None:
        self.is_running = True

        # Initialize pygame
        pygame.init()
        self.audio_player = AudioPlayer()
        self.clock = pygame.time.Clock()

        # Setup to draw maps
        self.tile_size_pixels = 80  # 4*20 and 5*16
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
            self.screen = pygame.display.set_mode(self.win_size_pixels.getAsIntTuple(),
                                                  pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.HWSURFACE)
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
        self.hero_party.set_pos(game_map.size() // 2, Direction.SOUTH)

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
                    else:
                        move_direction = Direction.get_direction(event.key)
                elif event.type == pygame.QUIT:
                    self.is_running = False

                if move_direction is not None:
                    self.hero_party.members[0].direction = move_direction
                    dest_tile = self.hero_party.members[0].curr_pos_dat_tile + move_direction.get_vector()
                    dest_tile_x = min(max(0, dest_tile.x), game_map.size().w - 1)
                    dest_tile_y = min(max(0, dest_tile.y), game_map.size().h - 1)
                    self.hero_party.members[0].curr_pos_dat_tile = (dest_tile_x, dest_tile_y)

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