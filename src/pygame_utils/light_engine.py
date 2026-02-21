"""Module defining the Light class.

Adapted from LIGHT in
https://github.com/LuckeyDuckey/Pygame_Lighting_Engine/blob/main/Dungeon_Example_Project/Light_Engine.py
with my updates from
https://github.com/justinbeetle/Pygame_Lighting_Engine/blob/main/Dungeon_Example_Project/Light_Engine.py.
"""

import logging
import math
import random
from typing import Optional

import numpy as np
import pygame

from generic_utils.point import Point
from pygame_utils.rect_utils import rect_intersection

logger = logging.getLogger(__name__)


class Light:
    """Light class to apply dynamic lighting from point or direction light sources onto a surface based
    on the provided list of rectangles casting shadows."""

    def __init__(
        self,
        radius_px: int,
        color: pygame.Color,
        intensity: float = 1.0,
        is_point: bool = False,
        angle_deg: float = 0.0,
        angle_width_deg: float = 360.0,
        flicker: bool = False,
    ) -> None:
        """
        :param radius_px: The radius of the light in pixels
        :param color: Color of the light
        :param intensity: Intensity of the light [0.0, 1.0]
        :param is_point: If the light is a point (directional) light source
        :param angle_deg: For a point light, the direction of the light's beam in degrees [0.0, 360.0]
        :param angle_width_deg: For a point light, the width of the lights's bean in degrees [0.0, 360.0]
        """
        self.size_px = radius_px * 2
        self.radius_px = radius_px
        self.render_surface = pygame.Surface((self.size_px, self.size_px))
        self.color = color
        self.intensity = intensity
        self.is_point = is_point
        self.angle = angle_deg
        self.angle_width_deg = angle_width_deg
        self.beam_line: Optional[tuple[int, int, int, int]] = None
        if self.is_point:
            self.beam_line = (
                self.radius_px,
                self.radius_px,
                int(self.radius_px + self.radius_px * math.cos(math.radians(self.angle))),
                int(self.radius_px - self.radius_px * math.sin(math.radians(self.angle))),
            )
        self.pixel_shader_surfs = [self.pixel_shader()]
        if flicker:
            flicker_increment_px = int(self.radius_px / 16)
            self.pixel_shader_surfs.extend(
                [self.pixel_shader(flicker_increment_px), self.pixel_shader(2 * flicker_increment_px)]
            )
        self.render_surface.set_colorkey((0, 0, 0))
        self.is_debugging = False

    def pixel_shader(self, radius_offset_px: int = 0) -> pygame.surface.Surface:
        """Return a surface with the full light map (no shadows) for this light source."""

        final_array = np.full(
            (self.size_px, self.size_px, 3), (self.color.r, self.color.g, self.color.b), dtype=np.float64
        )

        # Grid -----
        x, y = np.meshgrid(np.arange(self.size_px), np.arange(self.size_px))
        x = x.astype(np.float64)
        y = y.astype(np.float64)
        # -----

        # Radial -----
        distance = np.sqrt((x - self.radius_px) ** 2 + (y - self.radius_px) ** 2)
        radial_falloff = (self.radius_px + radius_offset_px - distance) / (self.radius_px + radius_offset_px)
        radial_falloff[radial_falloff <= 0] = 0
        # -----

        # Angular -----
        if self.is_point:
            point_angle = (180 / np.pi) * -np.arctan2((self.radius_px - x), (self.radius_px - y)) + 180
            diff_angle = np.abs(((self.angle - point_angle) + 180) % 360 - 180)
            angular_falloff = ((self.angle_width_deg / 2) - diff_angle) / self.angle_width_deg
            angular_falloff[angular_falloff <= 0] = 0
            final_intensity = radial_falloff * angular_falloff * self.intensity
        else:
            final_intensity = radial_falloff * self.intensity
        # -----

        final_array *= final_intensity[..., np.newaxis]

        return pygame.surfarray.make_surface(final_array.astype(np.uint8))

    def get_projection_to_edge(self, pt: Point) -> Point:
        """Get the center point of self.render_surface projected to the edge of the surface through pt."""
        dx = pt.x - self.radius_px
        dy = pt.y - self.radius_px

        if dx == 0:
            return Point(pt.x, (0 if dy <= 0 else self.size_px))

        if dy == 0:
            return Point((0 if dx <= 0 else self.size_px), pt.y)

        def calc_intersection(d1: float, d2: float, is_y_intersection: bool) -> Point:
            gradient = d1 / d2
            intercept = self.radius_px - (self.radius_px * gradient)
            line = 0 if d2 <= 0 else self.size_px
            if is_y_intersection:
                return Point(line, (gradient * line) + intercept)
            return Point((gradient * line) + intercept, line)

        y_intersection = calc_intersection(dy, dx, True)
        if y_intersection.y >= 0 and y_intersection.y <= self.size_px:
            return y_intersection

        return calc_intersection(dx, dy, False)

    def get_shadow_polygon_points(self, rect: pygame.Rect) -> Optional[list[Point]]:
        """Get a 3-tuple of points defining the points on the rectangle
        :param rect: Shadow tile rect in the coordinate frame of self.render_surface

        Upper      Upper      Upper
        Left       Center     Right
                 __________
                |          |
        Center  |  Center  |  Center
        Left    |  Center  |  Right
                |__________|

        Lower      Lower      Lower
        Left       Center     Right
        """

        def finalize_points(outer_pt1: Point, outer_pt2: Point, middle_pt: Optional[Point] = None) -> list[Point]:
            projected_pt1 = self.get_projection_to_edge(outer_pt1)
            projected_pt2 = self.get_projection_to_edge(outer_pt2)

            # Determine points between projected_pt1 and projected_pt2
            projected_pt1_to_projected_pt2_pts: list[Point] = []
            if abs(projected_pt1.x - projected_pt2.x) == self.size_px:
                if self.radius_px < projected_pt1.y:
                    # Upper center case where projections hit opposite sides
                    # logger.debug("Upper center opposite sides")
                    projected_pt1_to_projected_pt2_pts = [
                        Point(self.size_px, self.size_px),
                        Point(0, self.size_px),
                    ]
                else:
                    # Lower center case where projections hit opposite sides
                    # logger.debug("Lower center opposite sides")
                    projected_pt1_to_projected_pt2_pts = [Point(0, 0), Point(self.size_px, 0)]

            elif abs(projected_pt1.y - projected_pt2.y) == self.size_px:
                if self.radius_px < projected_pt1.x:
                    # Center right case where projections hit opposite sides
                    # logger.debug("Center right opposite sides")
                    projected_pt1_to_projected_pt2_pts = [
                        Point(self.size_px, 0),
                        Point(self.size_px, self.size_px),
                    ]
                else:
                    # Center left case where projections hit opposite sides
                    # logger.debug("Center left opposite sides")
                    projected_pt1_to_projected_pt2_pts = [Point(0, 0), Point(0, self.size_px)]
            elif projected_pt1.x not in (0, self.size_px):
                projected_pt1_to_projected_pt2_pts = [Point(projected_pt2.x, projected_pt1.y)]
            else:
                projected_pt1_to_projected_pt2_pts = [Point(projected_pt1.x, projected_pt2.y)]

            return (
                [outer_pt1, projected_pt1]
                + projected_pt1_to_projected_pt2_pts
                + [projected_pt2, outer_pt2, middle_pt if middle_pt else outer_pt1]
            )

        if rect.left <= self.radius_px <= rect.right:
            if self.radius_px < rect.top:
                # Upper center case - light above the shadow tile casting a shadow down
                # logger.debug("Upper center")
                return finalize_points(Point(rect.right, rect.top), Point(rect.left, rect.top))

            if self.radius_px > rect.bottom:
                # Lower center case - light below the shadow tile casting a shadow up
                # logger.debug("Lower center")
                return finalize_points(Point(rect.left, rect.bottom), Point(rect.right, rect.bottom))

            # Center center case - inside the shadow tile
            # logger.debug("Center center")
            return None

        if rect.top <= self.radius_px <= rect.bottom:
            if self.radius_px < rect.left:
                # Center left case - light left of the shadow tile casting a shadow right
                # logger.debug("Center left")
                return finalize_points(Point(rect.left, rect.top), Point(rect.left, rect.bottom))

            # Center right case - light right of the shadow tile casting a shadow left
            # logger.debug("Center right")
            return finalize_points(Point(rect.right, rect.top), Point(rect.right, rect.bottom))

        if self.radius_px > rect.right and self.radius_px < rect.top:
            # Upper right case - light above and right of the shadow tile casting a shadow to the lower left
            # logger.debug("Upper right")
            return finalize_points(
                Point(rect.left, rect.top), Point(rect.right, rect.bottom), Point(rect.right, rect.top)
            )

        if self.radius_px < rect.left and self.radius_px < rect.top:
            # Upper left case - light above and left of the shadow tile casting a shadow to the lower right
            # logger.debug("Upper left")
            return finalize_points(
                Point(rect.right, rect.top), Point(rect.left, rect.bottom), Point(rect.left, rect.top)
            )

        if self.radius_px < rect.left and self.radius_px > rect.bottom:
            # Lower left case - light below and left of the shadow tile casting a shadow to the upper right
            # logger.debug("Lower left")
            return finalize_points(
                Point(rect.left, rect.top), Point(rect.right, rect.bottom), Point(rect.left, rect.bottom)
            )

        # Lower right case - light below and right of the shadow tile casting a shadow to the upper left
        # logger.debug("Lower right")
        return finalize_points(
            Point(rect.right, rect.top), Point(rect.left, rect.bottom), Point(rect.right, rect.bottom)
        )

    def filter_shadow_rects(self, shadow_rects: list[pygame.Rect], pos_px: Point) -> list[pygame.Rect]:
        """Filter the shadow_rects to those that collide with this light source.."""
        light_rect = pygame.Rect(pos_px.x - self.radius_px, pos_px.y - self.radius_px, self.size_px, self.size_px)
        filtered = []
        for shadow_rect in shadow_rects:
            if (shadow_rect.height == 0 or shadow_rect.width == 0) and light_rect.clipline(
                shadow_rect.left, shadow_rect.top, shadow_rect.right, shadow_rect.bottom
            ):
                filtered.append(shadow_rect)
            elif light_rect.colliderect(shadow_rect):
                filtered.append(shadow_rect)
        return filtered

    def check_cast(self, pixel_shader_surf: pygame.surface.Surface, shadow_tile_rect: pygame.Rect) -> bool:
        """If the rect is fully in shadow, return True indicating this shadow tile can be ignored."""
        if self.is_point:
            if self.beam_line is not None and shadow_tile_rect.clipline(self.beam_line):
                # Center of beam collides with this rectangle.
                return True
            for point in [
                (shadow_tile_rect.right, shadow_tile_rect.top),
                (shadow_tile_rect.left, shadow_tile_rect.top),
                (shadow_tile_rect.left, shadow_tile_rect.bottom),
                (shadow_tile_rect.right, shadow_tile_rect.bottom),
            ]:
                # Center of beam doesn't touch the tile but its light may still hit it depending on
                # beam width.  Check if any of the coorner coordinates are lit by the beam.
                try:
                    if pixel_shader_surf.get_at(point) != pygame.Color(0, 0, 0, 255):
                        return True
                except IndexError:
                    pass
            return False
        return True

    def add_light(
        self,
        light_surface: pygame.surface.Surface,
        pos_px: Point,
        shadow_rects: Optional[list[pygame.Rect]] = None,
        forward_facing_wall_rects: Optional[list[pygame.Rect]] = None,
        wall_top_rects: Optional[list[pygame.Rect]] = None,
        wall_top_shift: int = 0,
        surface: Optional[pygame.surface.Surface] = None,
    ) -> None:
        """Add the light from this light source onto the provided light_surface at pixel coordinates
        pos_px in the coordinate frame of light_surface.
        :param light_surface: Surface for the light map for the scene
        :param pos_px: The light position in screen pixel coordinates.
        :param shadow_rects: Rectangles casting shadows, in screen pixel coordinates
        :param forward_facing_rects: Tuples of forward facing rectangles, for which there should shadows
        should not propagate in the x-dimension, and an optional rect for the top where shadow movement
        in the x-dimension should resume.
        """
        if shadow_rects is None:
            shadow_rects = []
        if forward_facing_wall_rects is None:
            forward_facing_wall_rects = []
        if wall_top_rects is None:
            wall_top_rects = []

        pixel_shader_surf = random.choice(self.pixel_shader_surfs)

        self.render_surface.fill((255, 255, 255))

        dx = pos_px.x - self.radius_px
        dy = pos_px.y - self.radius_px

        # Draw the shadows on the ground
        filtered_shadow_rects = self.filter_shadow_rects(shadow_rects, pos_px)
        for idx, screen_rect in enumerate(filtered_shadow_rects):
            # Shift the rect to be in the coordinate system of self.render_surface
            shadow_tile_rect = screen_rect.move(-dx, -dy)

            if self.check_cast(pixel_shader_surf, shadow_tile_rect):
                polygon_pts = self.get_shadow_polygon_points(shadow_tile_rect)
                if polygon_pts is None:
                    # Light is inside the shadow tile
                    logger.error("Light is inside a shadow tile")
                    return
                pygame.draw.polygon(self.render_surface, (0, 0, 0), polygon_pts)

                if self.is_debugging and surface:
                    pygame.draw.polygon(surface, (255, 0, 0), [p + (dx, dy) for p in polygon_pts])

        # Shift the shadows for the top of wall tiles
        render_surface_rect = pygame.Rect((0, 0), self.render_surface.get_size())
        for idx, screen_rect in enumerate(wall_top_rects):
            # Shift the rects to be in the coordinate system of self.render_surface
            dest_rect = rect_intersection(screen_rect.move(-dx, -dy), render_surface_rect)
            if dest_rect is None:
                if self.is_debugging and surface:
                    surface.fill((0, 128, 128), screen_rect)
                    surface.blit(
                        pygame.font.Font(pygame.font.get_default_font(), 16).render(
                            f"{idx}", False, pygame.Color("black")
                        ),
                        screen_rect.topleft,
                    )
                continue
            source_rect = rect_intersection(dest_rect.move(0, wall_top_shift), render_surface_rect)
            if source_rect is None:
                self.render_surface.fill((0, 0, 0), dest_rect)
                continue

            if self.is_debugging and surface:
                surface.fill((128, 128, 0), screen_rect)
                surface.blit(
                    pygame.font.Font(pygame.font.get_default_font(), 16).render(
                        f"{idx}", False, pygame.Color("black")
                    ),
                    screen_rect.topleft,
                )

            # BUG: For some reason blitting will NOT reliably work here.  Ensuring the source and destination rectangles
            #      do not overlap and copying the source subsurface, which should provide a new surfaces avoiding
            #      potential issues with source and destination overlaps, all have issues.  Using a scale no-op here as
            #      a workaround.
            source_subsurface = self.render_surface.subsurface(source_rect)
            dest_subsurface = self.render_surface.subsurface(dest_rect.topleft, source_rect.size)
            pygame.transform.scale(source_subsurface, source_rect.size, dest_subsurface)

            if dest_rect.size != source_rect.size:
                self.render_surface.fill(
                    (0, 0, 0), pygame.Rect(dest_rect.x, dest_rect.y + source_rect.height, dest_rect.w, dest_rect.h - source_rect.height)
                )

        # Apply shadows up forward facing walls
        for idx, screen_rect in enumerate(forward_facing_wall_rects):
            if self.is_debugging and surface:
                surface.fill((128, 0, 128), screen_rect)
                surface.blit(
                    pygame.font.Font(pygame.font.get_default_font(), 16).render(
                        f"{idx}", False, pygame.Color("black")
                    ),
                    screen_rect.topleft,
                )

            # Shift the rects to be in the coordinate system of self.render_surface
            dest_rect = rect_intersection(screen_rect.move(-dx, -dy), render_surface_rect)
            if dest_rect is None:
                continue
            source_rect = rect_intersection(pygame.Rect(dest_rect.x, dest_rect.y + dest_rect.h, dest_rect.w, 1), render_surface_rect)
            if source_rect is None:
                self.render_surface.fill((0, 0, 0), dest_rect)
                continue

            source_subsurface = self.render_surface.subsurface(source_rect)
            dest_subsurface = self.render_surface.subsurface(dest_rect)
            pygame.transform.scale(source_subsurface, dest_rect.size, dest_subsurface)

        # Draw the shadow rects for debugging
        if self.is_debugging and surface:
            for idx, screen_rect in enumerate(filtered_shadow_rects):
                if screen_rect.w > 0 and screen_rect.h > 0:
                    pygame.draw.rect(surface, (0, 0, 255), screen_rect, width=5)
                else:
                    pygame.draw.line(surface, (0, 0, 255), screen_rect.topleft, screen_rect.bottomright, width=5)
                surface.blit(
                    pygame.font.Font(pygame.font.get_default_font(), 16).render(
                        f"{idx}", False, pygame.Color("blue")
                    ),
                    screen_rect.move(5, 0).center,
                )

        self.render_surface.blit(pixel_shader_surf, special_flags=pygame.BLEND_RGBA_MIN)

        light_surface.blit(self.render_surface, (dx, dy), special_flags=pygame.BLEND_RGBA_ADD)


def set_ambient_light(
    light_surface: pygame.surface.Surface, color: Optional[pygame.Color] = None, intensity: int = 50
) -> None:
    """Set ambient light of the specified color and intensity
    :param color: Defaults to white
    :param intensity: [0, 255]
    """
    light_surface.fill((0, 0, 0))
    if color is None:
        color = pygame.Color("white")
    ambient_light = pygame.Surface(light_surface.get_size()).convert_alpha()
    ambient_light.fill((color.r, color.g, color.b, intensity))
    light_surface.blit(ambient_light)
