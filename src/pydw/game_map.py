#!/usr/bin/env python

from typing import Any, Callable, Dict, List, Optional, Tuple

import abc
from heapq import heappush, heappop
import math
import random

import pygame
import pyscroll

from generic_utils.point import Point

from pygame_utils.audio_player import AudioPlayer

from pydw.game_state_interface import GameStateInterface
from pydw.game_types import CharacterType, Direction, EncounterBackground, MapDecoration, Tile
from pydw.hero_party import HeroParty
from pydw.hero_state import HeroState
from pydw.legacy_map_data import LegacyMapData
from pydw.padded_tiled_map_data import PaddedTiledMapData
from pydw.map_character_state import MapCharacterState
from pydw.npc_state import NpcState


class GameMapInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_tile_info(self, tile: Optional[Point] = None) -> Tile:
        pass

    @abc.abstractmethod
    def can_move_to_tile(self,
                         tile: Point,
                         enforce_npc_hp_penalty_limit: bool = False,
                         enforce_npc_dof_limit: bool = False,
                         is_npc: bool = False,
                         prev_tile: Optional[Point] = None) -> bool:
        pass

    def can_npc_move_to_tile(self,
                             tile: Point,
                             enforce_npc_hp_penalty_limit: bool = True,
                             enforce_npc_dof_limit: bool = True,
                             prev_tile: Optional[Point] = None) -> bool:
        return self.can_move_to_tile(tile, enforce_npc_hp_penalty_limit, enforce_npc_dof_limit, True, prev_tile)

    def compute_npc_path(self, start: Point, goal: Point, verbose: bool = False) -> Optional[List[Point]]:
        """Compute a path from start to goal for an NPC using A* search"""
        if verbose:
            print(f'in compute_npc_path; start={start}; goal={goal}', flush=True)
        def h(n: Point) -> float:
            return abs(goal.x - n.x) + abs(goal.y - n.y)
        open_set: List[Tuple[float, Point]] = []
        heappush(open_set, (h(start), start))
        came_from: Dict[Point, Point] = {}
        g_score: Dict[Point, float] = {start: 0.0}
        f_score: Dict[Point, float] = {start: h(start)}
        while 0 < len(open_set):
            queued_f_score, current = heappop(open_set)
            if queued_f_score != f_score[current]:
                if verbose:
                    print(f'\tin compute_npc_path; ignoring current={current}; open_set={open_set}', flush=True)
                continue
            if verbose:
                print(f'\tin compute_npc_path; current={current}; open_set={open_set}', flush=True)
            if current == goal:
                break

            for direction in Direction:
                neighbor = current + direction.get_vector()
                if verbose:
                    print(f'\t\tin compute_npc_path; neighbor={neighbor}', flush=True)
                if not self.can_npc_move_to_tile(neighbor, enforce_npc_dof_limit=False, prev_tile=current):
                    if verbose:
                        print(f'\t\t\tin compute_npc_path; cannot move to tile', flush=True)
                    continue
                neighbor_tile = self.get_tile_info(neighbor)
                tile_score = (1.0 if neighbor_tile.name == 'path' else 2.0) / neighbor_tile.movement_speed_factor
                tentative_g_score = g_score[current] + tile_score
                if verbose:
                    print(f'\t\t\tin compute_npc_path; tentative_g_score={tentative_g_score}', flush=True)
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    tentative_f_score = tentative_g_score + h(neighbor)
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_f_score
                    heappush(open_set, (tentative_f_score, neighbor))

        if goal in came_from:
            # Reconstruct the path
            reverse_path = []
            while goal != start:
                reverse_path.append(goal)
                goal = came_from[goal]
            return list(reversed(reverse_path))
        elif verbose:
            print(f'in compute_npc_path; goal is not in came_from={came_from}', flush=True)

        # No path exists
        return None


class MapSprite(pygame.sprite.Sprite):
    image: pygame.surface.Surface
    image_pad_tiles = Point()
    tile_size_pixels = 16
    image_px_step_size = 4

    def __init__(self) -> None:
        super().__init__()

    def get_rect_from_tile(self, tile: Point) -> pygame.rect.Rect:
        return self.image.get_rect().move((MapSprite.image_pad_tiles + tile) * MapSprite.tile_size_pixels)


class MapDecorationSprite(MapSprite):
    def __init__(self, decoration: MapDecoration, removed: bool = False) -> None:
        super().__init__()
        self.decoration = decoration

        if self.decoration.type is None:
            raise AttributeError("All MapDecorationSprites require a MapDecoration with a type")

        if removed:
            if not self.remove_decoration():
                raise AttributeError("All removed MapDecorationSprites require a MapDecoration with a removed image")
        elif self.decoration.type.image is None:
            raise AttributeError("All MapDecorationSprites require a MapDecoration with an image")
        else:
            self.image = self.decoration.type.image

        self.rect = self.get_rect_from_tile(self.decoration.point)

        # Modified the rect to center the decoration horizontally and to have the base of it aligned with the bottom
        # of its assigned tile.
        self.rect.x = int(self.rect.x + (MapSprite.tile_size_pixels - self.image.get_width()) / 2)
        self.rect.y = int(self.rect.y + MapSprite.tile_size_pixels - self.image.get_height())

    def remove_decoration(self) -> bool:
        """
        :return: True if the map was successfully set to a removed image
        """
        if self.decoration.type is not None and self.decoration.type.removed_image is not None:
            self.image = self.decoration.type.removed_image
            return True
        return False


class CharacterSprite(MapSprite):
    character: MapCharacterState

    def __init__(self, character: MapCharacterState, game_map: GameMapInterface) -> None:
        super().__init__()
        self.character = character
        self.game_map = game_map
        self.phase = random.randint(0, self.character.character_type.num_phases-1)
        self.update_count = 0

        if self.character.character_type.num_phases == 2:
            # One step per phase change for characters with two phases
            self.updates_per_phase_change = self.character.character_type.ticks_per_step
            self.character_phase_progression = [0, 1]
        else:
            # One half step per phase change for characters with three phases
            self.updates_per_phase_change = self.character.character_type.ticks_per_step // 2
            self.character_phase_progression = [0, 1, 2, 1]

        self.image = CharacterSprite.get_image(self)
        self.rect = self.get_rect()

    def get_phase_image_index(self) -> int:
        return self.character_phase_progression[self.phase]

    def get_image(self) -> pygame.surface.Surface:
        return self.character.character_type.images[self.character.direction][self.get_phase_image_index()]

    def get_rect(self) -> pygame.rect.Rect:
        char_rect = self.image.get_rect()
        char_rect.midbottom = self.get_rect_from_tile(self.character.curr_pos_dat_tile).move(
            self.character.curr_pos_offset_img_px).midbottom
        return char_rect

    def get_character_movement_speed_factor(self) -> float:
        """Get the movement speed factor for the character"""
        return self.character.character_type.movement_speed_factor

    def get_nearest_tile_movement_speed_factor(self) -> float:
        """Get the movement speed factor for the tile nearest the character"""
        return self.get_nearest_tile_movement_speed_factor_for_character(self.character)

    def get_nearest_tile_movement_speed_factor_for_character(self, character: MapCharacterState) -> float:
        """Get the movement speed factor for the tile nearest an arbitrary character"""
        if character.curr_pos_offset_img_px.mag() < MapSprite.tile_size_pixels / 2:
            nearest_tile = character.curr_pos_dat_tile
        else:
            nearest_tile = character.dest_pos_dat_tile
        return self.game_map.get_tile_info(nearest_tile).movement_speed_factor

    def update(self, *args: Any, **kwargs: Any) -> None:
        # Move the character in steps to the destination tile
        if self.character.curr_pos_dat_tile != self.character.dest_pos_dat_tile:
            image_px_step_size = max(1, int(round(MapSprite.image_px_step_size *
                                                  self.get_character_movement_speed_factor() *
                                                  self.get_nearest_tile_movement_speed_factor())))

            direction_vector = self.character.direction.get_vector()
            self.character.curr_pos_offset_img_px += direction_vector * image_px_step_size
            if self.character.curr_pos_offset_img_px.mag() / MapSprite.tile_size_pixels >= direction_vector.mag():
                self.character.curr_pos_dat_tile = self.character.dest_pos_dat_tile
                self.character.curr_pos_offset_img_px = Point(0, 0)

        # Check for phase updates
        self.update_count += 1
        if self.update_count % self.updates_per_phase_change == 0:
            self.phase = (self.phase + 1) % len(self.character_phase_progression)

        # Update the image and rect
        self.image = self.get_image()
        self.rect = self.get_rect()

        super().update(args, kwargs)

    @staticmethod
    def get_tile_movement_steps() -> int:
        return int(math.ceil(MapSprite.tile_size_pixels / MapSprite.image_px_step_size))


class HeroSprite(CharacterSprite):
    character: HeroState
    character_types: Dict[str, CharacterType] = {}

    def __init__(self, hero: HeroState, hero_party: HeroParty, game_map: GameMapInterface) -> None:
        self.hero_party = hero_party
        super().__init__(hero, game_map)

    def get_character_movement_speed_factor(self) -> float:
        """Get the movement speed factor for the slowest member of the hero party"""
        slowest_movement_speed_factor = self.hero_party.members[0].character_type.movement_speed_factor
        for member in self.hero_party.members[1:]:
            slowest_movement_speed_factor = min(slowest_movement_speed_factor,
                                                member.character_type.movement_speed_factor)
        return slowest_movement_speed_factor

    def get_nearest_tile_movement_speed_factor(self) -> float:
        """Get the movement speed factor for the tile nearest the lead member of the hero party"""
        return self.get_nearest_tile_movement_speed_factor_for_character(self.hero_party.members[0])

    def get_image(self) -> pygame.surface.Surface:
        if self.character.hp <= 0:
            character_images = HeroSprite.character_types['ghost'].images
        elif self.character.character_type.name == 'hero':
            # TODO: Configurable way to handle the PC image mappings
            if self.character.weapon is not None and self.character.shield is not None:
                character_images = HeroSprite.character_types['hero_sword_and_shield'].images
            elif self.character.weapon is not None:
                character_images = HeroSprite.character_types['hero_sword'].images
            elif self.character.shield is not None:
                character_images = HeroSprite.character_types['hero_shield'].images
            else:
                character_images = HeroSprite.character_types['hero'].images
        else:
            character_images = self.character.character_type.images
        return character_images[self.character.direction][self.get_phase_image_index() %
                                                          len(character_images[self.character.direction])]


class NpcSprite(CharacterSprite):
    character: NpcState

    def __init__(self, character: NpcState, game_map: GameMapInterface) -> None:
        super().__init__(character, game_map)
        self.updates_between_npc_moves = character.character_type.ticks_between_npc_moves

        # Vary the movement rate across the NPCs
        move_delta = random.randint(-6, 6)
        self.updates_between_npc_moves += move_delta
        self.updates_per_phase_change += move_delta // 2
        self.update_count = random.randint(0, max(0, self.updates_between_npc_moves-1))
        self.destination_waypoint: Optional[Point] = None
        self.no_path_count = 0

        # Increase updates_per_phase_change for characters which are not moving so they step less frequently
        if not self.character.npc_info.walking:
            self.updates_per_phase_change *= 5

    def update(self, *args: Any, **kwargs: Any) -> None:
        if self.character.npc_info.walking:
            # Start moving NPC by setting a destination tile
            if (self.update_count % self.updates_between_npc_moves) == self.updates_between_npc_moves - 1:

                # Determine where to move instead of blindly moving forward
                if 0 < len(self.character.npc_info.waypoints):
                    # Choose a new waypoint if we don't have one or are already at it
                    new_waypoint = False
                    if self.destination_waypoint is None or \
                            self.character.curr_pos_dat_tile == self.destination_waypoint:
                        # Randomly choose a waypoint
                        self.destination_waypoint = random.choice(self.character.npc_info.waypoints)
                        new_waypoint = True
                        print(f'NPC moving to waypoint {self.destination_waypoint}', flush=True)

                    # Determine path to waypoint
                    path = self.game_map.compute_npc_path(self.character.curr_pos_dat_tile, self.destination_waypoint)
                    if new_waypoint:
                        print(f'NPC path to waypoint={path} from {self.character.curr_pos_dat_tile}', flush=True)
                    if path is not None and 0 < len(path):
                        self.character.dest_pos_dat_tile = path[0]
                        self.character.direction = Direction.get_direction(self.character.dest_pos_dat_tile -
                                                                           self.character.curr_pos_dat_tile)
                        self.no_path_count = 0
                    else:
                        self.no_path_count += 1
                        if self.no_path_count > 3:
                            self.destination_waypoint is None
                else:
                    # Randomly choose a directions
                    self.character.direction = random.choice(list(Direction))
                    dest_tile = self.character.curr_pos_dat_tile + self.character.direction.get_vector()
                    if self.game_map.can_npc_move_to_tile(dest_tile, prev_tile=self.character.curr_pos_dat_tile):
                        self.character.dest_pos_dat_tile = dest_tile

        super().update(args, kwargs)


class GameMap(GameMapInterface):
    def __init__(self,
                 game_state: GameStateInterface,
                 map_name: str,
                 map_decorations: Optional[List[MapDecoration]] = None,
                 removed_map_decorations: Optional[List[MapDecoration]] = None,
                 npcs: Optional[List[NpcState]] = None) -> None:
        self.game_state = game_state
        self.map = self.game_state.get_game_info().maps[map_name]

        # Set the decorations
        if map_decorations is None:
            self.map_decorations = self.map.map_decorations
        else:
            self.map_decorations = map_decorations
        self.removed_map_decorations: List[MapDecoration] = []
        if removed_map_decorations is not None:
            self.removed_map_decorations = removed_map_decorations

        # Set the NPCs
        if npcs is not None:
            self.npcs = npcs
        else:
            self.npcs = []
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
        for decoration in self.removed_map_decorations:
            if decoration.type is not None and decoration.type.removed_image is not None:
                self.group.add(MapDecorationSprite(decoration, removed=True), layer=self.map_data.decoration_layer)

        # Add characters to the group
        hero_party = self.game_state.get_hero_party()
        for hero in reversed(hero_party.members):
            self.group.add(HeroSprite(hero, hero_party, self), layer=self.map_data.character_layer)
        for npc_info in self.npcs:
            self.group.add(NpcSprite(npc_info, self), layer=self.map_data.character_layer)

    def size(self, with_padding: bool = False) -> Point:
        # Doesn't include padding, just the size of data size of the map
        if with_padding:
            return Point(self.map_data.map_size)
        else:
            return Point(self.map_data.map_size) - 2 * self.game_state.get_image_pad_tiles()

    def update(self) -> None:
        self.group.update()

    def draw(self, surface: Optional[pygame.surface.Surface] = None) -> None:
        if surface is None:
            surface = self.game_state.screen
            if surface is None:
                return

        # Center the map on the PC
        self.group.center((self.game_state.get_image_pad_tiles() + Point(0.5, 0.5) +
                           self.game_state.get_hero_party().get_curr_pos_dat_tile()) *
                          self.map_data.tile_size + self.game_state.get_hero_party().get_curr_pos_offset_img_px())

        # Detect if the hero is eclipsed by the over layer(s).  If so, do not render those layers.
        if self.map_data.set_pc_character_tile(self.game_state.get_hero_party().get_curr_pos_dat_tile()):
            self.map_layer.redraw_tiles(self.map_layer._buffer)

        # tell the map_layer (BufferedRenderer) to draw to the surface
        # the draw function requires a rect to draw to.
        self.group.draw(surface)

        light_diameter = self.game_state.get_hero_party().light_diameter
        if light_diameter is not None:
            light_radius_px = light_diameter * self.game_state.get_game_info().tile_size_pixels / 2

            # Left
            surface.fill('black', pygame.Rect(0,
                                              0,
                                              surface.get_width() / 2 - light_radius_px,
                                              surface.get_height()))

            # Right
            surface.fill('black', pygame.Rect(surface.get_width() / 2 + light_radius_px,
                                              0,
                                              surface.get_width() / 2 - light_radius_px,
                                              surface.get_height()))

            # Top
            surface.fill('black', pygame.Rect(0,
                                              0,
                                              surface.get_width(),
                                              surface.get_height() / 2 - light_radius_px))

            # Bottom
            surface.fill('black', pygame.Rect(0,
                                              surface.get_height() / 2 + light_radius_px,
                                              surface.get_width(),
                                              surface.get_height() / 2 - light_radius_px))

    def draw_character_sprites(self) -> None:
        map_center_offset = self.group._map_layer.get_center_offset()
        for sprite in self.group.get_sprites_from_layer(self.map_data.character_layer):
            self.game_state.screen.blit(sprite.get_image(), sprite.get_rect().move(map_center_offset))
        pygame.display.flip()

    def get_tile_info(self, tile: Optional[Point] = None, use_second: bool = False) -> Tile:
        if tile is None:
            tile = self.game_state.get_hero_party().main_character.curr_pos_dat_tile

        if isinstance(self.map_data, PaddedTiledMapData):
            tile_name = None
            tile_x, tile_y = tile.get_as_int_tuple()
            for layer_idx in reversed(self.map_data.base_tile_layers):
                tile_properties = self.map_data.get_tile_properties(tile_x, tile_y, layer_idx)
                if tile_properties is not None and 'type' in tile_properties and \
                        tile_properties['type'] is not None and len(tile_properties['type']) > 0:
                    tile_name = tile_properties['type']
                    if use_second:
                        use_second = False
                    else:
                        break
            if tile_name is not None and tile_name in self.game_state.get_game_info().tiles:
                return self.game_state.get_game_info().tiles[tile_name]
        else:
            try:
                return self.game_state.get_game_info().tiles[
                    self.game_state.get_game_info().tile_symbols[
                        self.map.dat[int(tile.y)][int(tile.x)]]]
            except IndexError:
                pass

        return Tile.default_tile()

    def get_decorations(
            self,
            tile: Optional[Point] = None,
            decoration_filter: Optional[Callable[[MapDecoration], bool]] = None,
            stop_after_first: bool = False) -> List[MapDecoration]:
        decorations = []
        if tile is None:
            tile = self.game_state.get_hero_party().get_curr_pos_dat_tile()
        for decoration in self.map_decorations:
            if decoration.point == tile and self.game_state.check_progress_markers(
                    decoration.progress_marker, decoration.inverse_progress_marker):
                if decoration_filter is None or decoration_filter(decoration):
                    decorations.append(decoration)
                    if stop_after_first:
                        break
        return decorations

    def get_decoration_for_interaction(
            self,
            pos_dat_tile: Optional[Point] = None,
            decoration_filter: Optional[Callable[[MapDecoration], bool]] = None) -> Optional[MapDecoration]:
        decoration = None

        if pos_dat_tile is None:
            # First look under the hero party
            decoration = self.get_decoration_for_interaction(
                self.game_state.get_hero_party().get_curr_pos_dat_tile(), decoration_filter)

            # Then look in front the hero party
            if decoration is None:
                decoration = self.get_decoration_for_interaction(
                    self.game_state.get_hero_party().get_curr_pos_dat_tile()
                    + self.game_state.get_hero_party().get_direction().get_vector(), decoration_filter)
        else:
            # Look at the specified tile position
            decorations = self.get_decorations(pos_dat_tile, decoration_filter, stop_after_first=True)
            if 0 < len(decorations):
                decoration = decorations[0]

        return decoration

    def get_npc_to_talk_to(self) -> Optional[NpcState]:
        def get_npc_sprite_at_tile(pos_dat_tile: Point) -> Optional[NpcState]:
            for sprite in self.group:
                if isinstance(sprite, NpcSprite):
                    npc_state = sprite.character
                    npc_info = npc_state.npc_info
                else:
                    continue

                if (npc_info is not None and
                        (pos_dat_tile == sprite.character.curr_pos_dat_tile or
                         pos_dat_tile == sprite.character.dest_pos_dat_tile)):
                    # NPC should turn to face you if they have something to say
                    if npc_info.dialog is not None:
                        sprite.character.curr_pos_dat_tile = sprite.character.dest_pos_dat_tile = pos_dat_tile
                        sprite.character.curr_pos_offset_img_px = Point(0, 0)
                        sprite.character.direction = self.game_state.get_hero_party().members[0].direction.get_opposite()
                        sprite.update_count = 0
                        sprite.update()

                        # Stationary characters should resume looking in the default direction after talking to the player.
                        if not npc_info.walking:
                            sprite.character.direction = npc_info.direction

                    return npc_state
            return None

        talk_dest_dat_tile = self.game_state.get_hero_party().members[0].curr_pos_dat_tile \
                             + self.game_state.get_hero_party().members[0].direction.get_vector()
        npc_to_talk_to = get_npc_sprite_at_tile(talk_dest_dat_tile)
        if npc_to_talk_to is None:
            talk_dest_tile_type = self.game_state.get_tile_info(talk_dest_dat_tile)
            can_talk_over = talk_dest_tile_type.can_talk_over

            # Check if a decoration prevents talking over a tile that otherwise allowed talking
            if can_talk_over:
                for decoration in self.map_decorations:
                    if decoration.type is not None and decoration.type.can_talk_over is False \
                            and decoration.overlaps(talk_dest_dat_tile):
                        can_talk_over = False
                        # print('Talking over not allowed: decoration', decoration, flush=True)
                        break
            # Check if a decoration allows talking over a tile to where talking was otherwise prevented
            if not can_talk_over:
                for decoration in self.map_decorations:
                    if decoration.type is not None and decoration.type.can_talk_over is True \
                            and decoration.overlaps(talk_dest_dat_tile):
                        can_talk_over = True
                        # print('Talking over allowed: decoration', decoration, flush=True)
                        break

            if can_talk_over:
                talk_dest_dat_tile = talk_dest_dat_tile \
                                     + self.game_state.get_hero_party().members[0].direction.get_vector()
                npc_to_talk_to = get_npc_sprite_at_tile(talk_dest_dat_tile)

        return npc_to_talk_to

    def get_npc_by_name(self, name: str) -> Optional[MapCharacterState]:
        for sprite in self.group:
            if isinstance(sprite, NpcSprite):
                npc_state = sprite.character
                if name == npc_state.npc_info.name:
                    return npc_state

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
            movement_allowed = self.get_tile_info(tile).walkable
            # print('Tile info =', self.get_tile_info(tile), self.get_tile_info(tile), flush=True)

        # Check if a decoration prevents movement to the tile that otherwise allowed movement
        if movement_allowed:
            for decoration in self.map_decorations:
                if decoration.type is not None and decoration.type.walkable is False and decoration.overlaps(tile):
                    movement_allowed = False
                    # print('Movement not allowed: decoration not walkable', decoration, flush=True)
                    break
        # Check if a decoration allows movement to a tile to which movement was otherwise prevented
        if not movement_allowed:
            for decoration in self.map_decorations:
                if decoration.type is not None and decoration.type.walkable is True and decoration.overlaps(tile):
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
        #     print('Movement not allowed: tile not walkable', flush=True)

        # If the PC is stuck somewhere it shouldn't be able to go, allow it to escape
        if not movement_allowed and not is_npc and tile != self.game_state.get_hero_party().get_curr_pos_dat_tile():
            movement_allowed = not self.can_move_to_tile(self.game_state.get_hero_party().get_curr_pos_dat_tile())

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
        return self.map_data.is_interior(pos_dat_tile)

    def is_exterior(self, pos_dat_tile: Optional[Point] = None) -> bool:
        return not self.is_interior(pos_dat_tile)

    def get_tile_monsters(self, pos_dat_tile: Point) -> List[str]:
        monster_set_name = self.map_data.get_monster_set_name(pos_dat_tile)
        if monster_set_name in self.game_state.get_game_info().monster_sets:
            return self.game_state.get_game_info().monster_sets[monster_set_name]
        return []

    def get_locked_map_decoration(self, pos_dat_tile: Optional[Point] = None) -> Optional[MapDecoration]:
        def is_locked(decoration: MapDecoration) -> bool:
            return decoration.type is not None and decoration.type.remove_with_key
        return self.get_decoration_for_interaction(pos_dat_tile, is_locked)

    def get_openable_map_decoration(self, pos_dat_tile: Optional[Point] = None) -> Optional[MapDecoration]:
        def is_openable(decoration: MapDecoration) -> bool:
            return decoration.type is not None and (decoration.type.remove_with_key or decoration.type.remove_with_open)
        return self.get_decoration_for_interaction(pos_dat_tile, is_openable)

    def is_facing_locked_item(self) -> bool:
        return self.get_locked_map_decoration() is not None

    def is_facing_openable_item(self) -> bool:
        return self.get_openable_map_decoration() is not None

    def open_locked_item(self) -> Optional[MapDecoration]:
        locked_map_decoration = self.get_locked_map_decoration()

        if locked_map_decoration is not None:
            if locked_map_decoration.type is not None and locked_map_decoration.type.remove_sound is not None:
                AudioPlayer().play_sound(locked_map_decoration.type.remove_sound)
            self.remove_decoration(locked_map_decoration)

        return locked_map_decoration

    def remove_decoration(self, decoration: MapDecoration) -> Optional[MapDecoration]:
        # Remove the decoration from the map (if present)
        if decoration in self.map_decorations and decoration.type is not None:
            self.map_decorations.remove(decoration)

            for sprite in self.group.remove_sprites_of_layer(self.map_data.decoration_layer):
                if sprite.decoration != decoration:
                    self.group.add(sprite, layer=self.map_data.decoration_layer)
                elif isinstance(sprite, MapDecorationSprite) and sprite.remove_decoration():
                    self.removed_map_decorations.append(decoration)
                    self.group.add(sprite, layer=self.map_data.decoration_layer)

            return decoration
        return None

    @staticmethod
    def get_surrounding_points(point: Point, distance: int, include_point: bool = True) -> List[Point]:
        points = []
        point_x, point_y = point.get_as_int_tuple()
        for x in range(point_x - distance, point_x + distance + 1):
            for y in range(point_y - distance, point_y + distance + 1):
                if not include_point and x == point_x and y == point_y:
                    continue
                points.append(Point(x, y))
        return points

    @staticmethod
    def get_adjacent_points(point: Point, include_point: bool = True) -> List[Point]:
        points = [Point(point.x - 1, point.y),
                  Point(point.x + 1, point.y),
                  Point(point.x, point.y - 1),
                  Point(point.x, point.y + 1)]
        if include_point:
            points.append(point)
        return points

    def get_tile_type_count(self, tiles: List[Point], tile_types: List[str]) -> int:
        tile_count = 0
        for tile in tiles:
            if self.get_tile_info(tile).name in tile_types:
                tile_count += 1
        return tile_count

    def get_tile_type_counts(self, tiles: List[Point], tile_types: List[str]) -> Dict[str, int]:
        tile_counts = {tile_type: 0 for tile_type in tile_types}
        for tile in tiles:
            tile_info = self.get_tile_info(tile)
            if tile_info.name in tile_counts:
                tile_counts[tile_info.name] += 1
        return tile_counts

    def get_surrounding_tile_type_count(self, tile: Point, distance: int, tile_types: List[str]) -> int:
        return self.get_tile_type_count(self.get_surrounding_points(tile, distance), tile_types)

    def get_surrounding_tile_type_counts(self, tile: Point, distance: int, tile_types: List[str]) -> Dict[str, int]:
        return self.get_tile_type_counts(self.get_surrounding_points(tile, distance), tile_types)

    def get_adjacent_tile_type_count(self, tile: Point, tile_types: List[str]) -> int:
        return self.get_tile_type_count(self.get_adjacent_points(tile), tile_types)

    def get_adjacent_tile_type_counts(self, tile: Point, tile_types: List[str]) -> Dict[str, int]:
        return self.get_tile_type_counts(self.get_adjacent_points(tile), tile_types)

    def get_encounter_background_name(self, tile: Optional[Point] = None,
                                      backgrounds: Optional[List[str]] = None) -> str:
        # Handle the background for dark maps
        if self.game_state.get_hero_party().light_diameter is not None:
            return 'darkness'

        # Determine the base tile
        if tile is None:
            tile = self.game_state.get_hero_party().get_curr_pos_dat_tile()
        tile_info = self.get_tile_info(tile)
        tile_name = tile_info.name.replace('_walkable', '')

        # Handle gates, which we should be able to see through to the local terrain
        background_prefix = ''
        if 'gate' == tile_name:
            background_prefix = 'gate:'
            tile_info = self.get_tile_info(tile, use_second=True)
            tile_name = tile_info.name.replace('_walkable', '')

        if tile_name in ['hill', 'cliff']:
            tile_name = 'plain'

        # Handle background for forested tiles, taking into account if we are deep in the forest or on the perimeter.
        forested_tiles = ['deciduous_forest', 'pine_forest', 'jungle']
        if tile_name in forested_tiles:
            adjacent_tiles_of_same_type = self.get_surrounding_tile_type_count(tile, 1, [tile_name]) - 1
            if adjacent_tiles_of_same_type >= 7:
                return background_prefix + tile_name + '_dark'
            elif adjacent_tiles_of_same_type >= 2:
                return background_prefix + tile_name
            else:
                return background_prefix + tile_name + '_light'

        # Handle shore backgrounds
        shore_tiles = ['shore', 'shore_walkable', 'shore_cliff', 'shore_cliff_walkable', 'beach', 'beach_walkable']
        shore_tile_name_to_tile_name_map = {'shore': 'plain', 'shore_cliff': 'plain', 'beach': 'desert'}
        shore_counts = self.get_adjacent_tile_type_counts(tile, shore_tiles)
        for tile_type, count in shore_counts.items():
            if count > 0:
                shore_tile_name = tile_type.replace('_walkable', '')
                if shore_tile_name in shore_tile_name_to_tile_name_map and tile_name == \
                        shore_tile_name_to_tile_name_map[shore_tile_name]:
                    return background_prefix + shore_tile_name

        # Handle backgrounds on some other tile types, taking into account surrounding vegetation and elevation.
        if tile_name in ['plain', 'desert']:
            # Factor in vegetation
            vegetation_suffix = ''
            vegetation_counts = self.get_surrounding_tile_type_counts(tile, 1, forested_tiles)
            vegetation = None
            vegetation_count = 0
            for tile_type, count in vegetation_counts.items():
                if count > vegetation_count:
                    vegetation, vegetation_count = tile_type, count
            if vegetation is not None:
                vegetation_suffix = '_' + vegetation

            # Factor in elevation
            elevation_suffix = ''
            elevation = None
            if self.get_surrounding_tile_type_count(tile, 3, ['volcano']) > 0:
                elevation = 'volcano'
            else:
                mountain_count = self.get_surrounding_tile_type_count(tile, 1, ['mountain'])
                if mountain_count > 0:
                    elevation = 'close_mountain'
                else:
                    mountain_count = self.get_surrounding_tile_type_count(tile, 3, ['mountain'])
                    if mountain_count > 15:
                        elevation = 'distant_mountain'  # 'big_distant_mountain'
                    elif mountain_count > 5:
                        elevation = 'distant_mountain'  # 'small_distant_mountain'
                    else:
                        cliff_count = self.get_surrounding_tile_type_count(tile, 1, ['cliff', 'cliff_walkable'])
                        if cliff_count > 1:
                            elevation = 'cliff'
                        elif elevation != 'hill':
                            hill_count = self.get_surrounding_tile_type_count(tile, 1, ['hill'])
                            if hill_count > 1:
                                elevation = 'hill'
            if elevation is not None:
                elevation_suffix = '_' + elevation

            background = tile_name + vegetation_suffix + elevation_suffix
            if backgrounds is not None:
                if background in backgrounds:
                    return background_prefix + background
                # print(f'WARN: No encounter background for {background} at {tile}', flush=True)

                background = tile_name + vegetation_suffix
                if background in backgrounds:
                    return background_prefix + background

                background = tile_name + elevation_suffix
                if background in backgrounds:
                    return background_prefix + background

        # For all other tiles, just use the tile name
        if tile_name == 'DEFAULT TILE':
            print('WARN: default tile at', tile, flush=True)

        return tile_name

    def get_encounter_background(self, tile: Optional[Point] = None) -> Optional[EncounterBackground]:
        if tile is None:
            tile = self.game_state.get_hero_party().get_curr_pos_dat_tile()
        backgrounds = self.game_state.get_game_info().encounter_backgrounds
        encounter_background_name = self.get_encounter_background_name(tile, list(backgrounds.keys()))
        if encounter_background_name in backgrounds:
            return backgrounds[encounter_background_name]
        if encounter_background_name.startswith('gate:'):
            non_gate_background_name = encounter_background_name.replace('gate:', '')
            if 'gate' in backgrounds and non_gate_background_name in backgrounds:
                gate_background = backgrounds['gate']
                background_without_gate = backgrounds[non_gate_background_name]

                # Combine the two backgrounds
                # Scale the background_without_gate image to the dimension and size of the gate_background image
                original_width = background_without_gate.image.get_width()
                original_height = background_without_gate.image.get_height()
                target_width = gate_background.image.get_width()
                target_height = gate_background.image.get_height()
                actual_height_to_width_ratio = original_width / original_height
                target_height_to_width_ratio = target_width / target_height
                if actual_height_to_width_ratio != target_height_to_width_ratio:
                    if actual_height_to_width_ratio < target_height_to_width_ratio:
                        subsurface_height = original_width / target_height_to_width_ratio
                        subsurface_rect = pygame.Rect(0,
                                                      (original_height - subsurface_height) // 2,
                                                      original_width,
                                                      subsurface_height)
                    else:
                        subsurface_width = original_height * target_height_to_width_ratio
                        subsurface_rect = pygame.Rect((original_width - subsurface_width) // 2,
                                                      0,
                                                      subsurface_width,
                                                      original_height)
                    background_image_without_gate = background_without_gate.image.subsurface(subsurface_rect)
                else:
                    background_image_without_gate = background_without_gate.image
                combined_image = pygame.transform.smoothscale(background_image_without_gate,
                                                              (target_width, target_height))
                combined_image.blit(gate_background.image, (0, 0))
                return EncounterBackground(encounter_background_name,
                                           combined_image,
                                           gate_background.image_path,
                                           gate_background.artist,
                                           gate_background.artist_url,
                                           gate_background.image_url)

        print(f'WARN: No encounter background for {encounter_background_name} at {tile}', flush=True)
        return None

    def dump_encounter_backgrounds(self) -> None:
        encounter_background_counts = {}
        map_size_x, map_size_y = self.size().get_as_int_tuple()
        for x in range(map_size_x):
            for y in range(map_size_y):
                tile = Point(x, y)
                tile_info = self.get_tile_info(tile)
                if tile_info.walkable and tile_info.spawn_rate > 0:
                    encounter_background = self.get_encounter_background(tile)
                    if encounter_background not in encounter_background_counts:
                        encounter_background_counts[encounter_background] = 1
                    else:
                        encounter_background_counts[encounter_background] += 1
        for k, v in sorted(encounter_background_counts.items(), key=lambda item: item[1], reverse=True):
            print(k, v, flush=True)
