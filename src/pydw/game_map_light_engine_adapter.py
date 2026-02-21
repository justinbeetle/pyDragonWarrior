"""Module defining the GameMapLightEngineAdapter class."""

import logging
import math
from copy import deepcopy
from typing import Optional

import pygame
import pyscroll

from generic_utils.point import Point
from pydw.game_map_interface import GameMapInterface
from pydw.game_state_interface import GameStateInterface
from pygame_utils.light_engine import Light
from pygame_utils.rect_utils import rect_collideline

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

        # Indicates that with the tileset the bottom of a wall tile is split in half with the bottom
        # halve depicting a vertical face of the wall and the top halve depicting a horizontal cross
        # section of the top of the wall.
        self.bottom_wall_tiles_split_in_middle = True

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

        def add_point_lights(
            light_position_tiles: Point,
            light_radius_px: int,
            ambient_light: Optional[Light],
            light: Optional[Light],
        ) -> None:
            """Optionally add both an ambient and non-ambient point light sources at the specified
            position and radius using the color and intensity settings of the provided lights.  The
            real work in doing this is determining where shadows should be cast for the non-ambient
            light, which is a factor of the location of wall tiles relative to the light.  In
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
            # Calculate light posisition in screen pixels.
            light_map_pos_px = (self.image_pad_tiles + light_position_tiles) * self.tile_size_pixels
            light_screen_pos_px = self.translate_point_world_to_screen(light_map_pos_px)

            if ambient_light:
                ambient_light.add_light(light_surface, light_screen_pos_px)

            if light is None:
                return

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
            visible_wall_tiles = deepcopy(wall_tiles)
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

            def is_visible_wall(tile: Point) -> bool:
                try:
                    x, y = tile.get_as_int_tuple()
                    return visible_wall_tiles[x - min_x][y - min_y]
                except IndexError:
                    return False

            def unset_visible_wall(tile: Point) -> None:
                try:
                    x, y = tile.get_as_int_tuple()
                    visible_wall_tiles[x - min_x][y - min_y] = False
                except IndexError:
                    logger.exception(
                        "Enccounter index error for tile %s where min_x=%s; max_x=%s; min_y=%s; \
max_y=%s; len(visible_wall_tiles)=%s; len(visible_wall_tiles[0])=%s",
                        tile,
                        min_x,
                        max_x,
                        min_y,
                        max_y,
                        len(visible_wall_tiles),
                        len(visible_wall_tiles[0]),
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
                        if rect_collideline(rect, line):
                            this_line_visible = False
                            break
                    if this_line_visible:
                        visible = True
                        break
                if visible:
                    wall_tile_rects.append(this_tile_rect)
                    if self.is_debugging:
                        surface.fill((0, 255, 0), this_tile_rect)
                        surface.blit(
                            pygame.font.Font(pygame.font.get_default_font(), 16).render(
                                f"{tile.x}, {tile.y}", False, pygame.Color("black")
                            ),
                            this_tile_rect.topleft,
                        )
                else:
                    if self.is_debugging:
                        surface.fill((255, 0, 0), this_tile_rect)
                        surface.blit(
                            pygame.font.Font(pygame.font.get_default_font(), 16).render(
                                f"{tile.x}, {tile.y}", False, pygame.Color("black")
                            ),
                            this_tile_rect.topleft,
                        )
                    #unset_visible_wall(tile)
                return visible

            light_x = int(light_position_tiles.x)
            light_y = int(light_position_tiles.y)
            max_left_x = min_right_x = light_x
            max_upper_y = min_lower_y = light_y
            left_line_rects = [pygame.Rect(self.image_pad_tiles * self.tile_size_pixels, (0, self.tile_size_pixels))]
            lower_left_line_rects = [pygame.Rect((self.image_pad_tiles + Point(0, 0.25)) * self.tile_size_pixels, (0, 3 * self.tile_size_pixels // 4))]
            right_line_rects = [left_line_rects[0].move(self.tile_size_pixels, 0)]
            lower_right_line_rects = [lower_left_line_rects[0].move(self.tile_size_pixels, 0)]
            top_line_rects = [pygame.Rect((self.image_pad_tiles + Point(0, 0.25)) * self.tile_size_pixels, (self.tile_size_pixels, 0))]
            bottom_line_rects = [pygame.Rect((self.image_pad_tiles + Point(0, 1.0)) * self.tile_size_pixels, (self.tile_size_pixels, 0))]
            top_of_tile_rect = pygame.Rect(self.image_pad_tiles * self.tile_size_pixels, (self.tile_size_pixels, self.tile_size_pixels // 2))
            bottom_of_tile_rect = top_of_tile_rect.move(0, self.tile_size_pixels // 2)

            def add_shadow(tile_pos: Point, rects: list[pygame.Rect]) -> None:
                for rect in rects:
                    shadow_rects.append(
                        self.translate_rect_world_to_screen(rect.move(tile_pos * self.tile_size_pixels))
                    )

            def add_shadow_left(tile_pos: Point) -> None:
                if is_wall(tile.get_upper()):
                    add_shadow(tile_pos, left_line_rects)
                else:
                    add_shadow(tile_pos, lower_left_line_rects)

            def add_shadow_right(tile_pos: Point) -> None:
                if is_wall(tile.get_upper()):
                    add_shadow(tile_pos, right_line_rects)
                else:
                    add_shadow(tile_pos, lower_right_line_rects)

            def add_shadow_top(tile_pos: Point) -> None:
                add_shadow(tile_pos, top_line_rects)

            def add_shadow_bottom(tile_pos: Point) -> None:
                add_shadow(tile_pos, bottom_line_rects)

            # Handle upper
            added_wall = False
            for y in range(max_upper_y, min_y - 1, -1):
                tile = Point(light_x, y)
                if added_wall:
                    unset_visible_wall(tile)
                elif is_wall(tile):
                    add_shadow_top(tile)
                    added_wall = True

            # Handle lower
            added_wall = False
            for y in range(min_lower_y, max_y + 1):
                tile = Point(light_x, y)
                if added_wall:
                    unset_visible_wall(tile)
                elif is_wall(tile):
                    add_shadow_bottom(tile)
                    added_wall = True

            # Handle left
            added_wall = False
            for x in range(max_left_x, min_x - 1, -1):
                tile = Point(x, light_y)
                if added_wall:
                    unset_visible_wall(tile)
                elif is_wall(tile):
                    add_shadow_left(tile)
                    added_wall = True

            # Handle right
            added_wall = False
            for x in range(min_right_x, max_x + 1):
                tile = Point(x, light_y)
                if added_wall:
                    unset_visible_wall(tile)
                elif is_wall(tile):
                    add_shadow_right(tile)
                    added_wall = True

            # Handle upper left diagnal
            wall_tile_rects = []
            for x in range(max_left_x, min_x - 1, -1):
                for y in range(max_upper_y, min_y - 1, -1):
                    tile = Point(x, y)
                    if is_visible_wall(tile):
                        is_visible(tile, check_ul=False, check_ur=True, check_lr=True, check_ll=True)
            for x in range(max_left_x, min_x - 1, -1):
                for y in range(max_upper_y, min_y - 1, -1):
                    tile = Point(x, y)
                    if is_visible_wall(tile):
                        if not is_wall(tile.get_upper()) or is_wall(tile.get_right()):
                            add_shadow_top(tile)
                        if not is_wall(tile.get_left()) or is_wall(tile.get_lower()):
                            add_shadow_left(tile)

            # Handle lower left diagnal
            wall_tile_rects = []
            for x in range(max_left_x, min_x - 1, -1):
                for y in range(min_lower_y, max_y + 1):
                    tile = Point(x, y)
                    if is_visible_wall(tile):
                        is_visible(tile, check_ul=True, check_ur=True, check_lr=True, check_ll=False)
            for x in range(max_left_x, min_x - 1, -1):
                for y in range(min_lower_y, max_y + 1):
                    tile = Point(x, y)
                    if is_visible_wall(tile):
                        if not is_wall(tile.get_lower()) or is_wall(tile.get_right()):
                            add_shadow_bottom(tile)
                        if not is_wall(tile.get_left()) or is_wall(tile.get_upper()):
                            add_shadow_left(tile)

            # Handle upper right diagnal
            wall_tile_rects = []
            for x in range(min_right_x, max_x + 1):
                for y in range(max_upper_y, min_y - 1, -1):
                    tile = Point(x, y)
                    if is_visible_wall(tile):
                        is_visible(tile, check_ul=True, check_ur=False, check_lr=True, check_ll=True)
            for x in range(min_right_x, max_x + 1):
                for y in range(max_upper_y, min_y - 1, -1):
                    tile = Point(x, y)
                    if is_visible_wall(tile):
                        if not is_wall(tile.get_upper()) or is_wall(tile.get_left()):
                            add_shadow_top(tile)
                        if not is_wall(tile.get_right()) or is_wall(tile.get_lower()):
                            add_shadow_right(tile)

            # Handle lower right diagnal
            wall_tile_rects = []
            for x in range(min_right_x, max_x + 1):
                for y in range(min_lower_y, max_y + 1):
                    tile = Point(x, y)
                    if is_visible_wall(tile):
                        is_visible(tile, check_ul=True, check_ur=True, check_lr=False, check_ll=True)
            for x in range(min_right_x, max_x + 1):
                for y in range(min_lower_y, max_y + 1):
                    tile = Point(x, y)
                    if is_visible_wall(tile):
                        if not is_wall(tile.get_lower()) or is_wall(tile.get_left()):
                            add_shadow_bottom(tile)
                        if not is_wall(tile.get_right()) or is_wall(tile.get_upper()):
                            add_shadow_right(tile)

            # Find visible forward facing walls and tops of walls
            forward_facing_rects = []
            wall_top_rects = []
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    tile = Point(x, y)
                    if is_wall(tile):
                        if is_wall(tile.get_lower()):
                            wall_top_rects.append(
                                self.translate_rect_world_to_screen(tile_rect.move(tile * self.tile_size_pixels))
                            )
                        else:
                            wall_top_rects.append(
                                self.translate_rect_world_to_screen(top_of_tile_rect.move(tile * self.tile_size_pixels))
                            )
                            forward_facing_rects.append(
                                self.translate_rect_world_to_screen(bottom_of_tile_rect.move(tile * self.tile_size_pixels))
                            )

            light.add_light(
                light_surface,
                light_screen_pos_px,
                shadow_rects,
                forward_facing_rects,
                wall_top_rects,
                self.tile_size_pixels // 2,
                surface,
            )

            if self.is_debugging:
                pygame.draw.circle(surface, (255, 255, 255), light_screen_pos_px, 4)

        # Check for the no-op case of a fully lit map
        for hero in self.game_state.get_hero_party().members:
            if hero.light_diameter_tiles is None:
                return

        # Create a surface to act as a light map
        light_surface = pygame.Surface(surface.get_size())
        map_wide_ambient_itensity = 0.0
        if self.is_debugging:
            map_wide_ambient_itensity = 0.25
        if map_wide_ambient_itensity:
            ambient_light = pygame.Surface(light_surface.get_size()).convert_alpha()
            ambient_light.fill((255, 255, 255, int(map_wide_ambient_itensity * 255)))
            light_surface.blit(ambient_light)

        # Add point lights to the light map
        # Where the debugging graphics are being applied, ensure they are only applied for
        # a single (currently using the first) light.
        orig_is_debugging = self.is_debugging
        for hero in self.game_state.get_hero_party().members:
            if hero.light_diameter_tiles is None:
                # This case doesn't exist (see return above) and is only here to appease mypy
                continue

            # In calculating the radius, increasing it by a 4/pi factor (about 1.27) to account for the
            # decrease in visible area in changing from lighting a square to the circle inscribed in the
            # square.  This change restores the maximum area of visibility as this is the ratio of the
            # area of a square to its inscribed circle based on a unit circle (area pi units squared)
            # versus the square inscribing a unit circle (area=4 units squared).
            light_radius_px = int(hero.light_diameter_tiles * self.tile_size_pixels / 2 * 4 / math.pi)

            # Check for no-op case - no light output for this character
            if 0 == light_radius_px:
                continue

            if hero.ambient_light_color:
                ambient_color = pygame.Color(
                    hero.ambient_light_color[0], hero.ambient_light_color[1], hero.ambient_light_color[2], 255
                )
                ambient_intensity = hero.ambient_light_color[3] / 255
            else:
                ambient_color = pygame.Color("White")
                ambient_intensity = 0.45
            if hero.light_color:
                light_color = pygame.Color(hero.light_color[0], hero.light_color[1], hero.light_color[2], 255)
                light_intensity = hero.light_color[3] / 255
            else:
                light_color = pygame.Color("White")
                light_intensity = 0.2
            if ambient_intensity > 0:
                if (
                    hero.ambient_light is None
                    or hero.ambient_light.radius_px != light_radius_px
                    or hero.ambient_light.intensity != ambient_intensity
                    or hero.ambient_light.color != ambient_color
                ):
                    hero.ambient_light = Light(light_radius_px, ambient_color, ambient_intensity, flicker=False)
            else:
                hero.ambient_light = None
            if light_intensity > 0:
                if (
                    hero.light is None
                    or hero.light.radius_px != light_radius_px
                    or hero.light.intensity != light_intensity
                    or hero.light.color != light_color
                ):
                    hero.light = Light(light_radius_px, light_color, light_intensity, flicker=True)
            else:
                hero.light = None

            # When self.bottom_wall_tiles_split_in_middle is True, only apply jitter in the x-dimension.
            # That is because the y-coordinate is used to determine whether or not to shade the bottom
            # of wall tiles with the same y-coordinate, leading to possible cases of unsightly
            # oscillations between shading and not shading the bottom on a wall tile.
            jitter = Point(
                hero.light_position_jitter_tiles.x,
                0.0 if self.bottom_wall_tiles_split_in_middle else hero.light_position_jitter_tiles.y,
            )
            light_pos_dat_tile = (
                hero.curr_pos_dat_tile
                + hero.curr_pos_offset_img_px / self.tile_size_pixels
                + Point(0.5, 0.5)
                + hero.direction.get_vector() * 0.15
                + jitter
            )
            add_point_lights(light_pos_dat_tile, light_radius_px, hero.ambient_light, hero.light)

            # Only add the debugging visualizations for the first member of the hero party with lights
            self.is_debugging = False
        self.is_debugging = orig_is_debugging

        # Apply light map to surface
        surface.blit(light_surface, special_flags=pygame.BLEND_RGBA_MULT)
