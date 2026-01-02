#!/usr/bin/env python

import logging
from typing import NamedTuple, Optional, Union

import numpy as np
import pygame

logger = logging.getLogger(__name__)


class Point(NamedTuple):
    x: int
    y: int


class FloatPoint(NamedTuple):
    x: float
    y: float


class Light:
    def __init__(
        self,
        radius_px: int,
        color: pygame.Color,
        intensity: float = 1.0,
        is_point: bool = False,
        angle_deg: float = 0.0,
        angle_width_deg: float = 360.0,
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
        self.angle = angle_deg
        self.angle_width_deg = angle_width_deg
        self.is_point = is_point
        self.pixel_shader_surf = self.pixel_shader()
        self.render_surface.set_colorkey((0, 0, 0))

    def pixel_shader(self) -> pygame.surface.Surface:
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
        radial_falloff = (self.radius_px - distance) * (1 / self.radius_px)
        radial_falloff[radial_falloff <= 0] = 0
        # -----

        # Angular -----
        if self.is_point:
            point_angle = (180 / np.pi) * -np.arctan2((self.radius_px - x), (self.radius_px - y)) + 180
            diff_angle = np.abs(((self.angle - point_angle) + 180) % 360 - 180)
            angular_falloff = ((self.angle_width_deg / 2) - diff_angle) * (1 / self.angle_width_deg)
            angular_falloff[angular_falloff <= 0] = 0
        else:
            angular_falloff = 1
        # -----

        final_intensity = radial_falloff * angular_falloff * self.intensity
        final_array *= final_intensity[..., np.newaxis]

        return pygame.surfarray.make_surface(final_array.astype(np.uint8))

    def get_projection_to_edge(self, pt: Point) -> Union[FloatPoint, Point]:
        """Get the center point of self.render_surface projected to the edge of the surface through pt."""
        dx = pt.x - self.radius_px
        dy = pt.y - self.radius_px

        if dx == 0:
            return Point(pt.x, (0 if dy <= 0 else self.size_px))

        if dy == 0:
            return Point((0 if dx <= 0 else self.size_px), pt.y)

        def calc_intersection(d1: int, d2: int, is_y_intercept: bool) -> FloatPoint:
            gradient = d1 / d2
            intercept = self.radius_px - (self.radius_px * gradient)
            line = 0 if d2 <= 0 else self.size_px
            if is_y_intercept:
                return FloatPoint(line, (gradient * line) + intercept)
            return FloatPoint((gradient * line) + intercept, line)

        y_intersection = calc_intersection(dy, dx, True)
        if y_intersection.y >= 0 and y_intersection.y <= self.size_px:
            return y_intersection

        return calc_intersection(dx, dy, False)

    def get_shadow_polygon_points(self, rect: pygame.Rect) -> Optional[list[Union[FloatPoint, Point]]]:
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

        def finalize_points(
            outer_pt1: Point, outer_pt2: Point, middle_pt: Optional[Point] = None
        ) -> list[Union[FloatPoint, Point]]:
            projected_pt1 = self.get_projection_to_edge(outer_pt1)
            projected_pt2 = self.get_projection_to_edge(outer_pt2)

            # Determine points between projected_pt1 and projected_pt2
            projected_pt1_to_projected_pt2_pts: list[Union[FloatPoint, Point]] = []
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
            elif projected_pt1.x != self.size_px and projected_pt1.x != 0:
                projected_pt1_to_projected_pt2_pts = [FloatPoint(projected_pt2.x, projected_pt1.y)]
            else:
                projected_pt1_to_projected_pt2_pts = [FloatPoint(projected_pt1.x, projected_pt2.y)]

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

    def filter_shadow_rects(self, shadow_rects: list[pygame.Rect], x_px: int, y_px: int) -> list[pygame.Rect]:
        """Filter the shadow_rects to those that collide with this light source.."""
        light_rect = pygame.Rect(x_px - self.radius_px, y_px - self.radius_px, self.size_px, self.size_px)
        filtered = []
        for shadow_rect in shadow_rects:
            if shadow_rect.height == 0 and light_rect.clipline(
                shadow_rect.left, shadow_rect.top, shadow_rect.right, shadow_rect.bottom
            ):
                filtered.append(shadow_rect)
            elif light_rect.colliderect(shadow_rect):
                filtered.append(shadow_rect)
        return filtered

    def check_cast(self, shadow_tile_rect: pygame.Rect) -> bool:
        """If the rect is fully in shadow, return True indicating this shadow tile can be ignored."""
        if False and self.is_point:
            # Disabled as this logic will miss a narrow bean going through a tile but not hitting its corners!!!
            for point in [
                (shadow_tile_rect.right, shadow_tile_rect.top),
                (shadow_tile_rect.left, shadow_tile_rect.top),
                (shadow_tile_rect.left, shadow_tile_rect.bottom),
                (shadow_tile_rect.right, shadow_tile_rect.bottom),
            ]:
                try:
                    c = self.pixel_shader_surf.get_at(point)
                    logger.debug(f"point={point}; c={c}; c!=(0, 0, 0, 255)={c!=(0, 0, 0, 255)}")
                    if self.pixel_shader_surf.get_at(point) != (0, 0, 0, 255):
                        return True
                except IndexError:
                    pass
            return False
        return True

    def add_light(
        self, light_surface: pygame.surface.Surface, shadow_rects: list[pygame.Rect], x_px: int, y_px: int
    ) -> None:
        """Add the light from this light source onto the provided light_surface at pixel coordinates
        x_px, y_px in the coordinate frame of light_surface."""

        self.render_surface.fill((0, 0, 0))
        self.render_surface.blit(self.pixel_shader_surf)

        dx = x_px - self.radius_px
        dy = y_px - self.radius_px

        for shadow_tile_rect in self.filter_shadow_rects(shadow_rects, x_px, y_px):
            # Shift the rect to be in the coordinate system of self.render_surface
            shadow_tile_rect = shadow_tile_rect.move(-dx, -dy)

            if self.check_cast(shadow_tile_rect):
                polygon_pts = self.get_shadow_polygon_points(shadow_tile_rect)
                if polygon_pts is None:
                    # Light is inside the shadow tile
                    logger.error("Light is inside a shadow tile")
                    return
                pygame.draw.polygon(self.render_surface, (0, 0, 0), polygon_pts)
                # pygame.draw.aalines(self.render_surface, (0, 0, 0), True, polygon_pts)

        # pygame.draw.circle(self.render_surface, (255, 255, 255), (self.radius_px, self.radius_px), 2)

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
