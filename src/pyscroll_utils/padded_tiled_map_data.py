#!/usr/bin/env python

"""
Variant of pyscroll.data.TileMapData.
ScrollTest was copied and modified from pyscroll/apps/demo.py.

Source copied and modified from https://github.com/bitcraft/pyscroll
"""
import logging
import xml.etree.ElementTree as ET
from typing import Any, Callable, Iterator, Optional, cast

import pygame
import pyscroll
import pytmx

from generic_utils.point import Point
from pygame_utils import surface_effects
from pyscroll_utils.scroll_test import ScrollTest

logger = logging.getLogger(__name__)


class PaddedTiledMapData(pyscroll.data.PyscrollDataAdapter):  # type: ignore
    """For data loaded from pytmx

    Use of this class requires a recent version of pytmx.
    """

    TILED_MAP_MONSTER_SET_LAYER_NAME_PREFIX = "Monster Set "

    def __init__(
        self,
        tmx_filename: str,
        image_pad_tiles: Point = Point(0, 0),
        desired_tile_size: Optional[int] = None,
    ):
        super().__init__()
        self.desired_tile_size = desired_tile_size

        # Lighting mode state - applied in modify_images
        self.saturation_factor = 1.0  # no-op
        self.blue_factor = 0.0  # no-op
        self.darken_factor = 0.0  # no-op

        # Load the map
        self.tmx = self.load_pytmx_without_image_layers(tmx_filename)
        # Modify the images for the needs of this implementation
        self.modify_images()

        self.image_pad_tiles = image_pad_tiles.ceil()
        self.overlay_layer_offset = 0
        self._base_tile_layers = self.calc_base_tile_layers()
        self._overlay_tile_layers = self.calc_overlay_tile_layers()
        self._all_tile_layers = self._base_tile_layers + self._overlay_tile_layers
        self.layers_to_render = self.all_tile_layers
        self.object_group_to_bound_rendering: Optional[int] = None

        decoration_layer = None
        character_layer = None
        for idx, l in enumerate(self.tmx.layers):
            if "decoration" == l.name:
                decoration_layer = idx
            elif "character" == l.name:
                character_layer = idx
        if decoration_layer is None:
            self.overlay_layer_offset += 1
            decoration_layer = self.base_tile_layers[-1] + self.overlay_layer_offset
        if character_layer is None:
            self.overlay_layer_offset += 1
            character_layer = self.base_tile_layers[-1] + self.overlay_layer_offset
        self._decoration_layer = decoration_layer
        self._character_layer = character_layer

        """print('self.tmx', self.tmx, flush=True)
        print('self.tmx.tilewidth', self.tmx.tilewidth, flush=True)
        print('self.tmx.tileheight', self.tmx.tileheight, flush=True)
        #print('self.tmx.__dict__', self.tmx.__dict__, flush=True)
        for idx, l in enumerate(self.tmx.layers):
            print('layer', idx, '=', l, flush=True)
            print('type(l) =', type(l), flush=True)
            #print('l.__dict__ =', l.__dict__, flush=True)
            if isinstance(l, list):
                for obj in l:
                    print('   obj.x', obj.x / self.tmx.tilewidth, flush=True)
                    print('   obj.y', obj.y / self.tmx.tileheight, flush=True)
                    print('   obj.width', obj.width / self.tmx.tilewidth, flush=True)
                    print('   obj.height', obj.height / self.tmx.tileheight, flush=True)
                    #print('   obj', obj, flush=True)
                    print('   type(obj) =', type(obj), flush=True)
                    #print('   obj.__dict__', obj.__dict__, flush=True)
        for idx, l in enumerate(self.all_tile_layers):
            print('all_tile_layers: layer', idx, '=', l, flush=True)
        for idx, l in enumerate(self.base_tile_layers):
            print('base_tile_layers: layer', idx, '=', l, flush=True)
        for idx, l in enumerate(self.overlay_tile_layers):
            print('overlay_tile_layers: layer', idx, '=', l, flush=True)
        print('decoration layer', self.decoration_layer, flush=True)
        print('character layer', self.character_layer, flush=True)"""

    @staticmethod
    def load_pytmx_without_image_layers(tmx_filename: str) -> pytmx.TiledMap:
        """Load the TiledMap while stripping invisible image layers.  These image layers are only
        being used to compare the Tiled map to a template image while creating the map in Tiled.
        The template images are not being controlled and pytmx errors out upon failing to load an
        image, making this neccessary.

        If removing the image layers wasn't neccessary, loading a Tiled map would instead be as
        simple as follows:  pytmx.util_pygame.load_pygame(tmx_filename)
        """
        # Remove invisible image layers from the XML ElementTree
        xml_root = ET.parse(tmx_filename).getroot()
        for image_layer_element in xml_root.findall(".//imagelayer"):
            if "visible" in image_layer_element.attrib and not pytmx.convert_to_bool(
                image_layer_element.attrib["visible"]
            ):
                xml_root.remove(image_layer_element)
            else:
                logger.warning("Retaining visible image layer in Tiled map.")

        # Load map into pytmx manually from the modified ElementTree
        tmx = pytmx.TiledMap(image_loader=pytmx.util_pygame.pygame_image_loader)
        tmx.filename = tmx_filename
        tmx.parse_xml(xml_root)
        return tmx

    def set_lighting_mode(self, saturation_factor: float, blue_factor: float, darken_factor: float) -> bool:
        """Set factors used in the alter_lighting for day/night lighting changes.  Return a boolean
        indicating if the lighting mode was changed."""
        was_changed = (
            self.saturation_factor != saturation_factor
            or self.blue_factor != blue_factor
            or self.darken_factor != darken_factor
        )
        self.saturation_factor = saturation_factor
        self.blue_factor = blue_factor
        self.darken_factor = darken_factor
        return was_changed

    def modify_images(self) -> None:
        """Modify the images for the usage in PaddedTiledMapData"""
        # Determine desired amount of pre-zoom
        self.pre_zoom = 1.0
        if self.desired_tile_size is not None:
            self.pre_zoom = self.desired_tile_size / self.tmx.tilewidth

        # Pre-zoom tile images
        if self.pre_zoom != 1.0:
            images: list[Optional[pygame.surface.Surface]] = []
            for i in self.tmx.images:
                if i is not None:
                    images.append(
                        pygame.transform.scale(
                            surface_effects.alter_lighting(
                                i, self.saturation_factor, self.blue_factor, self.darken_factor
                            ),
                            self.tile_size,
                        )
                    )
                else:
                    images.append(None)
            self.tmx.images = images

        # FUTURE: Remove this after updating to a new pyscroll version with the fix.
        # Manually clearing _animated_tile as this is otherwise missed in reload_animations.
        # Fix in PR https://github.com/bitcraft/pyscroll/pull/73.
        self._animated_tile.clear()

        self.reload_animations()

        # Add an image of black as the last image
        black_tile = self.tmx.images[-1].copy()
        black_tile.fill("black")
        self.tmx.images.append(black_tile)

    def reload_data(self) -> None:
        """Reload the tiles"""
        self.tmx = self.load_pytmx_without_image_layers(self.tmx.filename)
        self.modify_images()

    def set_pc_character_tile(self, pos_dat_tile: Point) -> bool:
        """
        :param pos_dat_tile: Tile position of player character
        :return: If a redraw of the map is needed for the new PC position
        """
        object_group_to_bound_rendering_orig = self.object_group_to_bound_rendering
        self.object_group_to_bound_rendering = self.get_overlapping_overlay_mask_layer_index(pos_dat_tile)
        if self.object_group_to_bound_rendering is not None:
            self.set_tile_layers_to_render(self.base_tile_layers)
        else:
            self.set_tile_layers_to_render(self.all_tile_layers)
        return object_group_to_bound_rendering_orig != self.object_group_to_bound_rendering

    def is_interior(self, pos_dat_tile: Point) -> bool:
        return self.get_overlapping_overlay_mask_layer_index(pos_dat_tile) is not None

    def is_exterior(self, pos_dat_tile: Point) -> bool:
        return not self.is_interior(pos_dat_tile)

    def get_monster_set_name(self, pos_dat_tile: Point) -> Optional[str]:
        layer_name = self.get_overlapping_monster_set_layer_name(pos_dat_tile)
        if layer_name:
            return layer_name[len(PaddedTiledMapData.TILED_MAP_MONSTER_SET_LAYER_NAME_PREFIX) :]
        return None

    def get_overlapping_overlay_mask_layer_index(self, pos_dat_tile: Point) -> Optional[int]:
        def layer_filter(layer: pytmx.pytmx.TiledObjectGroup) -> bool:
            return "is_overlay" in layer.properties and layer.properties["is_overlay"]

        object_group_info = self.get_overlapping_object_group_info(pos_dat_tile, layer_filter)
        if object_group_info:
            return object_group_info[0]
        return None

    def get_overlapping_monster_set_layer_name(self, pos_dat_tile: Point) -> Optional[str]:
        # TODO: Change this to be property driven
        def layer_filter(layer: pytmx.pytmx.TiledObjectGroup) -> bool:
            return isinstance(layer.name, str) and layer.name.startswith(
                PaddedTiledMapData.TILED_MAP_MONSTER_SET_LAYER_NAME_PREFIX
            )

        object_group_info = self.get_overlapping_object_group_info(pos_dat_tile, layer_filter)
        if object_group_info:
            return object_group_info[1]
        return None

    def get_overlapping_object_group_info(
        self,
        pos_dat_tile: Point,
        layer_filter: Optional[Callable[[pytmx.pytmx.TiledObjectGroup], bool]] = None,
    ) -> Optional[tuple[int, Optional[str]]]:
        # Iterate through TiledOjbectGroup layers looking for any layer which the PC collides with tile
        for idx, layer in enumerate(self.tmx.layers):
            if not isinstance(layer, pytmx.pytmx.TiledObjectGroup):
                continue
            for obj in layer:
                if layer_filter and not layer_filter(layer):
                    # If a layer filter was specified, skip layers which do not conform to the filter
                    continue
                rect = pygame.Rect(
                    obj.x / self.tmx.tilewidth,
                    obj.y / self.tmx.tileheight,
                    obj.width / self.tmx.tilewidth,
                    obj.height / self.tmx.tileheight,
                )
                if rect.collidepoint(pos_dat_tile.get_as_int_tuple()):
                    return idx, layer.name
        return None

    def set_tile_layers_to_render(self, layers_to_render: list[int]) -> None:
        if self.layers_to_render != layers_to_render:
            self.layers_to_render = layers_to_render

    def decrement_layers_to_render(self) -> None:
        if len(self.layers_to_render) > 1:
            self.layers_to_render = self.layers_to_render[:-1]

    def increment_layers_to_render(self) -> None:
        layer_added = False
        new_layers = []
        for layer_idx in self.all_tile_layers:
            if layer_idx in self.layers_to_render:
                new_layers.append(layer_idx)
            elif not layer_added:
                new_layers.append(layer_idx)
                layer_added = True
        self.layers_to_render = new_layers

    @property
    def all_tile_layers(self) -> list[int]:
        return self._all_tile_layers

    def calc_all_tile_layers(self) -> list[int]:
        return self.calc_base_tile_layers() + self.calc_overlay_tile_layers()

    @property
    def base_tile_layers(self) -> list[int]:
        return self._base_tile_layers

    def calc_base_tile_layers(self) -> list[int]:
        tile_layers = []
        for layer_idx, layer in enumerate(self.tmx.layers):
            # Skip non-tile layers
            if not isinstance(layer, pytmx.pytmx.TiledTileLayer):
                continue

            # Assume base layers are the default
            if layer.visible and ("is_overlay" not in layer.properties or not layer.properties["is_overlay"]):
                tile_layers.append(layer_idx)
        return tile_layers

    @property
    def decoration_layer(self) -> int:
        return self._decoration_layer

    @property
    def character_layer(self) -> int:
        return self._character_layer

    @property
    def cloud_layer(self) -> int:
        return max(len(self._all_tile_layers), max(self._decoration_layer, self._character_layer) + 1)

    @property
    def overlay_tile_layers(self) -> list[int]:
        return self._overlay_tile_layers

    def calc_overlay_tile_layers(self) -> list[int]:
        tile_layers = []
        for layer_idx, layer in enumerate(self.tmx.layers):
            # Skip non-tile layers
            if not isinstance(layer, pytmx.pytmx.TiledTileLayer):
                continue

            # Assume base layers are the default
            if layer.visible and "is_overlay" in layer.properties and layer.properties["is_overlay"]:
                tile_layers.append(layer_idx + self.overlay_layer_offset)
        return tile_layers

    def get_animations(self) -> Iterator[tuple[int, Any]]:
        for gid, d in self.tmx.tile_properties.items():
            try:
                frames = d["frames"]
            except KeyError:
                continue

            if frames:
                yield gid, frames

    def convert_surfaces(self, parent: pygame.surface.Surface, alpha: bool = False) -> None:
        """Convert all images in the data to match the parent

        :param parent: pygame.surface.Surface
        :param alpha: preserve alpha channel or not
        """
        images = []
        for image in self.tmx.images:
            try:
                if alpha:
                    images.append(image.convert_alpha(parent))
                else:
                    images.append(image.convert(parent))
            except AttributeError:
                images.append(None)
        self.tmx.images = images

    @property
    def tile_size(self) -> tuple[int, int]:
        """This is the pixel size of tiles to be rendered"""
        if self.pre_zoom == 1.0:
            return self.tmx.tilewidth, self.tmx.tileheight
        return int(self.pre_zoom * self.tmx.tilewidth), int(self.pre_zoom * self.tmx.tileheight)

    @property
    def map_size(self) -> tuple[int, int]:
        """This is the size of the map in tiles"""
        # This size INCLUDES the padding
        return (
            self.tmx.width + 2 * self.image_pad_tiles[0],
            self.tmx.height + 2 * self.image_pad_tiles[1],
        )

    @property
    def visible_tile_layers(self) -> list[int]:
        """This must return layer numbers, not objects"""
        return self.layers_to_render

    @property
    def visible_object_layers(self) -> Iterator[pytmx.TiledObjectGroup]:
        """This must return layer objects

        This is not required for custom data formats.

        :return: Sequence of pytmx object layers/groups
        """
        return (layer for layer in self.tmx.visible_layers if isinstance(layer, pytmx.TiledObjectGroup))

    def get_tile_properties(self, x: int, y: int, l: int) -> Optional[dict[str, str]]:
        layer_idx = l
        if layer_idx not in self.base_tile_layers:
            layer_idx -= self.overlay_layer_offset
        if not isinstance(self.tmx.layers[layer_idx], pytmx.pytmx.TiledTileLayer):
            return None
        x = min(max(0, x), self.tmx.width - 1)
        y = min(max(0, y), self.tmx.height - 1)
        return cast(Optional[dict[str, str]], self.tmx.get_tile_properties(x, y, layer_idx))

    def _get_tile_image(
        self,
        x: int,
        y: int,
        l: int,
        image_indexing: bool = True,
        limit_to_visible: bool = True,
    ) -> Optional[pygame.surface.Surface]:
        layer_idx = l
        if layer_idx not in self.visible_tile_layers and limit_to_visible:
            return None
        if layer_idx not in self.base_tile_layers:
            layer_idx -= self.overlay_layer_offset
        if not isinstance(self.tmx.layers[layer_idx], pytmx.pytmx.TiledTileLayer):
            return None
        if image_indexing:
            # With image_indexing, coord (0,0) is where the pad starts.
            # Without image_indexing, coord (0,0) is where the Tiled map starts.
            x = min(max(0, x - self.image_pad_tiles.x), self.tmx.width - 1)
            y = min(max(0, y - self.image_pad_tiles.y), self.tmx.height - 1)
        if self.object_group_to_bound_rendering is not None:
            render_tile = False
            for obj in self.tmx.layers[self.object_group_to_bound_rendering]:
                rect = pygame.Rect(
                    obj.x / self.tmx.tilewidth,
                    obj.y / self.tmx.tileheight,
                    obj.width / self.tmx.tilewidth,
                    obj.height / self.tmx.tileheight,
                )
                rect.inflate_ip(2, 2)
                if rect.collidepoint(x, y):
                    render_tile = True
                    break
            if not render_tile:
                return cast(Optional[pygame.surface.Surface], self.tmx.images[-1])
        try:
            return cast(
                Optional[pygame.surface.Surface],
                self.tmx.get_tile_image(x, y, layer_idx),
            )
        except ValueError:
            return None

    def _get_tile_image_by_id(self, id: int) -> Optional[pygame.surface.Surface]:
        """Return Image by a custom ID

        Used for animations.  Not required for static maps.
        """
        return cast(Optional[pygame.surface.Surface], self.tmx.images[id])

    def get_tile_images_by_rect(self, rect: pygame.Rect) -> Iterator[tuple[int, int, int, pygame.surface.Surface]]:
        """Speed up data access

        More efficient because data is accessed and cached locally
        """

        x1, y1, x2, y2 = pyscroll.common.rect_to_bb(rect)
        images = self.tmx.images
        layers = self.tmx.layers
        at = self._animated_tile
        tracked_gids = self._tracked_gids
        anim_map = self._animation_map
        track = bool(self._animation_queue)

        for layer_idx in self.visible_tile_layers:
            if layer_idx not in self.base_tile_layers:
                layer_idx -= self.overlay_layer_offset

            if not isinstance(layers[layer_idx], pytmx.pytmx.TiledTileLayer):
                continue

            for y in range(y1, y2 + 1):
                row = layers[layer_idx].data[min(max(0, y - self.image_pad_tiles[1]), self.tmx.height - 1)]

                for x in range(x1, x2 + 1):
                    gid = row[min(max(0, x - self.image_pad_tiles[0]), self.tmx.width - 1)]
                    if not gid:
                        continue

                    if self.object_group_to_bound_rendering is not None:
                        render_tile = False
                        for obj in self.tmx.layers[self.object_group_to_bound_rendering]:
                            rect = pygame.Rect(
                                obj.x / self.tmx.tilewidth,
                                obj.y / self.tmx.tileheight,
                                obj.width / self.tmx.tilewidth,
                                obj.height / self.tmx.tileheight,
                            )
                            rect.inflate_ip(2, 2)
                            if rect.collidepoint(x - self.image_pad_tiles[0], y - self.image_pad_tiles[1]):
                                render_tile = True
                                break
                        if not render_tile:
                            yield x, y, layer_idx, images[-1]
                            continue

                    if track and gid in tracked_gids:
                        anim_map[gid].positions.add((x, y, layer_idx))

                    try:
                        # animated, so return the correct frame
                        yield x, y, layer_idx, at[(x, y, layer_idx)]

                    except KeyError:
                        # not animated, so return surface from data, if any
                        yield x, y, layer_idx, images[gid]


if __name__ == "__main__":
    import os
    import sys

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    pygame.display.set_caption("pyscroll Test")

    base_path = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = os.path.join("data", "maps", "tiled", "alefgard.tmx")
    filename = os.path.join(base_path, filename)

    try:
        ScrollTest(screen, PaddedTiledMapData(filename, Point(100, 100))).run()
    except Exception as e:
        import traceback

        print(
            traceback.format_exception(None, e, e.__traceback__),  # <- type(e) by docs, but ignored
            file=sys.stderr,
            flush=True,
        )
        traceback.print_exc()

    pygame.quit()
