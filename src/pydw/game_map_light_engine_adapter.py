"""Module defining the GameMapLightEngineAdapter class."""

import logging
import math
from typing import Optional

import pygame
import pyscroll

from generic_utils.point import Point
from pydw.game_map_interface import GameMapInterface
from pydw.game_state_interface import GameStateInterface
from pygame_utils.light_engine import Light

logger = logging.getLogger(__name__)


class GameMapLightEngineAdapter:
    """Logic for setting up the shadow rects for light_engine.Light based on the GameMap state in
    order to use dynamic lighting."""

    def __init__(
        self,
        game_state: GameStateInterface,
        game_map: GameMapInterface,
        map_layer: pyscroll.orthographic.BufferedRenderer,
    ) -> None:
        self.game_state = game_state
        self.game_map = game_map
        self.map_layer = map_layer
        self.image_pad_tiles = self.game_state.get_image_pad_tiles()
        self.tile_size_pixels = self.game_state.get_game_info().tile_size_pixels
        self.is_debugging = False

    def translate_point_world_to_screen(self, pt: Point) -> Point:
        """Translate a point from world to screen coordinates."""
        return Point(self.map_layer.translate_point(pt))

    def translate_rect_world_to_screen(self, rect: pygame.Rect) -> pygame.Rect:
        """Translate a rectangle from world to screen coordinates."""
        return pygame.Rect(self.map_layer.translate_rect(rect))

    def apply_dynamic_lighting(self, surface: pygame.surface.Surface) -> None:
        """Apply dynamic lighting onto the provided surface based on the current game state.
        The dynamic lighting is applied onto an already rendered map (in screen coordinates)
        so when determining where to apply shadows based on the map the coordinates need to
        be translated from world to screen coordinates."""
        light_diameter_tiles = self.game_state.get_hero_party().light_diameter
        if light_diameter_tiles is None:
            return

        # Apply ambient light
        light_surface = pygame.Surface(surface.get_size())
        ambient_light = pygame.Surface(light_surface.get_size()).convert_alpha()
        ambient_light.fill((255, 255, 255, 50))
        light_surface.blit(ambient_light)

        # Add point lights
        def add_point_light(
            light_position_tiles: Point,
            light_radius_px: int,
            color: Optional[pygame.Color] = None,
            intensity: float = 1.0,
        ) -> None:
            """Add a point light in the specified position casting light of the specified radius,
            color, and intensity.  The real work in doing this is determining where shadows should
            be cast, which is a factor of the location of wall tiles relative to the light.  In
            maintaining the lighting feel of Dragon Warrior, we want the light to propagate into the
            lower half of upper wall tiles, the upper half of lower wall tiles, and the entirety of
            left and right wall tiles.

                Upper      Upper      Upper
                Left       Center     Right
                        __________
                        |          |
                Center  |  Center  |  Center
                Left    |  Center  |  Right
                        |__________|

                Lower      Lower      Lower
                Left       Center     Right

            The algorithm used here to identify the shadow rentangles operates on each of the
            diagnals (upper left, lower left, upper right, and lower right).  For each diagnal,
            it iterates though the tiles in the quaderant of the diagnal from the light source
            out in two passes.  In the first pass, where wall tiles are present it determines if
            the wall tile is visible.  In the second, operating only on the visible wall tiles,
            it ands recntangles to the list shadow_rects for the sides away from the light source
            that are not adjacent to another visible wall.
            """
            if color is None:
                color = pygame.Color("white")
            # Calculate light posisition in screen pixels.
            light_map_pos_px = (self.image_pad_tiles + light_position_tiles) * self.tile_size_pixels
            light_screen_pos_px = self.translate_point_world_to_screen(light_map_pos_px)

            light_radius_tiles = light_radius_px / self.tile_size_pixels
            min_x = math.floor(max(0, light_position_tiles.x - light_radius_tiles))
            max_x = math.ceil(min(light_position_tiles.x + light_radius_tiles, self.game_map.size().x - 1))
            min_y = math.floor(max(0, light_position_tiles.y - light_radius_tiles))
            max_y = math.ceil(min(light_position_tiles.y + light_radius_tiles, self.game_map.size().y - 1))

            # Iterate through tiles to get a list of tile rects which should cast shadows.
            shadow_rects = []
            wall_tiles: list[list[bool]] = [
                [self.game_map.get_tile_info(Point(x, y)).name in ["walls"] for y in range(min_y, max_y + 1)]
                for x in range(min_x, max_x + 1)
            ]
            tile_rect = pygame.Rect(
                self.image_pad_tiles * self.tile_size_pixels,
                (self.tile_size_pixels, self.tile_size_pixels),
            )
            wall_tile_rects: list[pygame.Rect] = []

            def is_wall(tile: Point) -> bool:
                try:
                    x, y = tile.get_as_int_tuple()
                    return wall_tiles[x - min_x][y - min_y]
                except IndexError:
                    return False

            def unset_wall(tile: Point) -> None:
                try:
                    x, y = tile.get_as_int_tuple()
                    wall_tiles[x - min_x][y - min_y] = False
                except IndexError:
                    logger.exception(
                        "Enccounter index error for tile %s where min_x=%s; max_x=%s; min_y=%s; \
max_y=%s; len(wall_tiles)=%s; len(wall_tiles[0])=%s",
                        tile,
                        min_x,
                        max_x,
                        min_y,
                        max_y,
                        len(wall_tiles),
                        len(wall_tiles[0]),
                    )

            def is_visible(
                tile: Point,
                check_ul: bool = True,
                check_ur: bool = True,
                check_lr: bool = True,
                check_ll: bool = True,
            ) -> bool:
                """Determine whether or not a wall tile is visible from the light source
                by building a list of lines from the light source to the coorners of the
                tile and checking whether any of the lines do not collide with any of the
                rectangles of the visible wall tiles (wall_tile_rects).  Where a wall tile
                is visible, add its rectange to wall_tile_rects.  Where a wall tile is
                not visible, remove it from wall_tiles."""
                light_x, light_y = light_screen_pos_px.get_as_int_tuple()
                this_tile_rect = self.translate_rect_world_to_screen(tile_rect.move(tile * self.tile_size_pixels))
                lines: list[tuple[int, int, int, int]] = []
                if check_ul:
                    lines.append((light_x, light_y, this_tile_rect.left, this_tile_rect.top))
                if check_ur:
                    lines.append((light_x, light_y, this_tile_rect.right, this_tile_rect.top))
                if check_lr:
                    lines.append((light_x, light_y, this_tile_rect.right, this_tile_rect.bottom))
                if check_ll:
                    lines.append((light_x, light_y, this_tile_rect.left, this_tile_rect.bottom))
                visible = False
                for line in lines:
                    this_line_visible = True
                    for rect in wall_tile_rects:
                        clipped_line = rect.clipline(line)
                        # If the line doesn't colide with the rect or it colisdes only at a single point, then it is visible
                        if clipped_line and clipped_line[0] != clipped_line[1]:
                            this_line_visible = False
                            break
                    if this_line_visible:
                        visible = True
                        break
                if visible:
                    wall_tile_rects.append(this_tile_rect)
                    if self.is_debugging:
                        surface.fill((255, 0, 0, 40), this_tile_rect)
                else:
                    if self.is_debugging:
                        surface.fill((0, 255, 0, 40), this_tile_rect)
                    unset_wall(tile)
                return visible

            light_x = int(light_position_tiles.x)
            light_y = int(light_position_tiles.y)
            max_left_x = light_x
            min_right_x = max_left_x
            max_upper_y = light_y
            min_lower_y = max_upper_y
            left_line_rects = [pygame.Rect(self.image_pad_tiles * self.tile_size_pixels, (0, self.tile_size_pixels))]
            right_line_rects = [left_line_rects[0].move(self.tile_size_pixels, 0)]
            top_line_rects = [pygame.Rect(self.image_pad_tiles * self.tile_size_pixels, (self.tile_size_pixels, 0))]
            bottom_line_rects = [
                top_line_rects[0].move(0, self.tile_size_pixels / 2),
                pygame.Rect(
                    (self.image_pad_tiles + Point(0, 0.5)) * self.tile_size_pixels, (0, self.tile_size_pixels / 2)
                ),
                pygame.Rect(
                    (self.image_pad_tiles + Point(1, 0.5)) * self.tile_size_pixels, (0, self.tile_size_pixels / 2)
                ),
            ]

            def add_shadow(tile_pos: Point, rects: list[pygame.Rect]) -> None:
                for rect in rects:
                    shadow_rects.append(
                        self.translate_rect_world_to_screen(rect.move(tile_pos * self.tile_size_pixels))
                    )

            def add_shadow_left(tile_pos: Point) -> None:
                add_shadow(tile_pos, left_line_rects)

            def add_shadow_right(tile_pos: Point) -> None:
                add_shadow(tile_pos, right_line_rects)

            def add_shadow_top(tile_pos: Point) -> None:
                add_shadow(tile_pos, top_line_rects)

            def add_shadow_bottom(tile_pos: Point) -> None:
                add_shadow(tile_pos, bottom_line_rects)

            # Handle upper left diagnal
            wall_tile_rects = []
            for x in range(max_left_x, min_x - 1, -1):
                for y in range(max_upper_y, min_y - 1, -1):
                    tile = Point(x, y)
                    if is_wall(tile):
                        is_visible(tile, check_ul=False, check_ur=True, check_lr=True, check_ll=True)
            for x in range(max_left_x, min_x - 1, -1):
                for y in range(max_upper_y, min_y - 1, -1):
                    tile = Point(x, y)
                    if is_wall(tile):
                        if not is_wall(tile.get_upper()):
                            add_shadow_top(tile)
                        if not is_wall(tile.get_left()):
                            add_shadow_left(tile)

            # Handle lower left diagnal
            wall_tile_rects = []
            for x in range(max_left_x, min_x - 1, -1):
                for y in range(min_lower_y, max_y + 1):
                    tile = Point(x, y)
                    if is_wall(tile):
                        is_visible(tile, check_ul=True, check_ur=True, check_lr=True, check_ll=False)
            for x in range(max_left_x, min_x - 1, -1):
                for y in range(min_lower_y, max_y + 1):
                    tile = Point(x, y)
                    if is_wall(tile):
                        if not is_wall(tile.get_lower()):
                            add_shadow_bottom(tile)
                        if not is_wall(tile.get_left()):
                            add_shadow_left(tile)

            # Handle upper right diagnal
            wall_tile_rects = []
            for x in range(min_right_x, max_x + 1):
                for y in range(max_upper_y, min_y - 1, -1):
                    tile = Point(x, y)
                    if is_wall(tile):
                        is_visible(tile, check_ul=True, check_ur=False, check_lr=True, check_ll=True)
            for x in range(min_right_x, max_x + 1):
                for y in range(max_upper_y, min_y - 1, -1):
                    tile = Point(x, y)
                    if is_wall(tile):
                        if not is_wall(tile.get_upper()):
                            add_shadow_top(tile)
                        if not is_wall(tile.get_right()):
                            add_shadow_right(tile)

            # Handle lower right diagnal
            wall_tile_rects = []
            for x in range(min_right_x, max_x + 1):
                for y in range(min_lower_y, max_y + 1):
                    tile = Point(x, y)
                    if is_wall(tile):
                        is_visible(tile, check_ul=True, check_ur=True, check_lr=False, check_ll=True)
            for x in range(min_right_x, max_x + 1):
                for y in range(min_lower_y, max_y + 1):
                    tile = Point(x, y)
                    if is_wall(tile):
                        if not is_wall(tile.get_lower()):
                            add_shadow_bottom(tile)
                        if not is_wall(tile.get_right()):
                            add_shadow_right(tile)

            light = Light(light_radius_px, color, intensity)
            light.add_light(light_surface, shadow_rects, light_screen_pos_px)

        # Add player character light
        add_point_light(
            self.game_state.get_hero_party().get_curr_pos_dat_tile()
            + self.game_state.get_hero_party().get_curr_pos_offset_img_px() / self.tile_size_pixels
            + Point(0.5, 0.5),
            int(light_diameter_tiles * self.tile_size_pixels / 2),
            intensity=0.4,
        )

        if self.is_debugging:
            pc_x, pc_y = self.translate_point_world_to_screen(
                (self.image_pad_tiles + self.game_state.get_hero_party().get_curr_pos_dat_tile())
                * self.tile_size_pixels
            ).get_as_int_tuple()
            surface.fill((0, 0, 255, 40), (pc_x, pc_y, self.tile_size_pixels, self.tile_size_pixels))

        # Apply light map to surface
        surface.blit(light_surface, special_flags=pygame.BLEND_RGBA_MULT)
