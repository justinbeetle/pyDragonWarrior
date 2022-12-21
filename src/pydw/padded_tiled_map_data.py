#!/usr/bin/env python

"""
Variant of pyscroll.data.TileMapData.
ScrollTest was copied and modified from pyscroll/apps/demo.py.

Source copied and modified from https://github.com/bitcraft/pyscroll
"""
from typing import Any, Callable, cast, Deque, Dict, Iterator, List, Optional, Tuple

import xml.etree.ElementTree as ET

import pygame
import pyscroll
import pytmx

from generic_utils.point import Point


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

        # Extract out any image layers - image layers are only being used to compare the Tiled map to a template image.
        # The template images are not being controlled and pytmx errors out upon failing to load an image.
        xml_root = ET.parse(tmx_filename).getroot()
        for image_layer_element in xml_root.findall(".//imagelayer"):
            xml_root.remove(image_layer_element)

        # load data from pytmx
        # Would use the following if not for the imagelayer issue: pytmx.util_pygame.load_pygame(tmx_filename)
        self.tmx = pytmx.TiledMap(image_loader=pytmx.util_pygame.pygame_image_loader)
        self.tmx.filename = tmx_filename
        self.tmx.parse_xml(xml_root)

        # Determine desired amount of pre-zoom
        self.pre_zoom = 1.0
        if desired_tile_size is not None:
            self.pre_zoom = desired_tile_size / self.tmx.tilewidth

        # Pre-zoom tile images
        if self.pre_zoom != 1.0:
            images: List[Optional[pygame.surface.Surface]] = []
            for i in self.tmx.images:
                if i is not None:
                    images.append(pygame.transform.scale(i, self.tile_size))
                else:
                    images.append(None)
            self.tmx.images = images

        # Add an image of black
        black_tile = self.tmx.images[-1].copy()
        black_tile.fill("black")
        self.tmx.images.append(black_tile)

        self.image_pad_tiles = image_pad_tiles.ceil()
        self.reload_animations()
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

    def set_pc_character_tile(self, pos_dat_tile: Point) -> bool:
        """
        :param pos_dat_tile: Tile position of player character
        :return: If a redraw of the map is needed for the new PC position
        """
        object_group_to_bound_rendering_orig = self.object_group_to_bound_rendering
        self.object_group_to_bound_rendering = (
            self.get_overlapping_overlay_mask_layer_index(pos_dat_tile)
        )
        if self.object_group_to_bound_rendering is not None:
            self.set_tile_layers_to_render(self.base_tile_layers)
        else:
            self.set_tile_layers_to_render(self.all_tile_layers)
        return (
            object_group_to_bound_rendering_orig != self.object_group_to_bound_rendering
        )

    def is_interior(self, pos_dat_tile: Point) -> bool:
        return self.get_overlapping_overlay_mask_layer_index(pos_dat_tile) is not None

    def is_exterior(self, pos_dat_tile: Point) -> bool:
        return not self.is_interior(pos_dat_tile)

    def get_monster_set_name(self, pos_dat_tile: Point) -> Optional[str]:
        layer_name = self.get_overlapping_monster_set_layer_name(pos_dat_tile)
        if layer_name:
            return layer_name[
                len(PaddedTiledMapData.TILED_MAP_MONSTER_SET_LAYER_NAME_PREFIX) :
            ]
        return None

    def get_overlapping_overlay_mask_layer_index(
        self, pos_dat_tile: Point
    ) -> Optional[int]:
        def layer_filter(layer: pytmx.pytmx.TiledObjectGroup) -> bool:
            return "is_overlay" in layer.properties and layer.properties["is_overlay"]

        object_group_info = self.get_overlapping_object_group_info(
            pos_dat_tile, layer_filter
        )
        if object_group_info:
            return object_group_info[0]
        return None

    def get_overlapping_monster_set_layer_name(
        self, pos_dat_tile: Point
    ) -> Optional[str]:
        # TODO: Change this to be property driven
        def layer_filter(layer: pytmx.pytmx.TiledObjectGroup) -> bool:
            return isinstance(layer.name, str) and layer.name.startswith(
                PaddedTiledMapData.TILED_MAP_MONSTER_SET_LAYER_NAME_PREFIX
            )

        object_group_info = self.get_overlapping_object_group_info(
            pos_dat_tile, layer_filter
        )
        if object_group_info:
            return object_group_info[1]
        return None

    def get_overlapping_object_group_info(
        self,
        pos_dat_tile: Point,
        layer_filter: Optional[Callable[[pytmx.pytmx.TiledObjectGroup], bool]] = None,
    ) -> Optional[Tuple[int, Optional[str]]]:
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

    def set_tile_layers_to_render(self, layers_to_render: List[int]) -> None:
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
    def all_tile_layers(self) -> List[int]:
        return self._all_tile_layers

    def calc_all_tile_layers(self) -> List[int]:
        return self.calc_base_tile_layers() + self.calc_overlay_tile_layers()

    @property
    def base_tile_layers(self) -> List[int]:
        return self._base_tile_layers

    def calc_base_tile_layers(self) -> List[int]:
        tile_layers = []
        for layer_idx, layer in enumerate(self.tmx.layers):
            # Skip non-tile layers
            if not isinstance(layer, pytmx.pytmx.TiledTileLayer):
                continue

            # Assume base layers are the default
            if layer.visible and (
                "is_overlay" not in layer.properties
                or not layer.properties["is_overlay"]
            ):
                tile_layers.append(layer_idx)
        return tile_layers

    @property
    def decoration_layer(self) -> int:
        return self._decoration_layer

    @property
    def character_layer(self) -> int:
        return self._character_layer

    @property
    def overlay_tile_layers(self) -> List[int]:
        return self._overlay_tile_layers

    def calc_overlay_tile_layers(self) -> List[int]:
        tile_layers = []
        for layer_idx, layer in enumerate(self.tmx.layers):
            # Skip non-tile layers
            if not isinstance(layer, pytmx.pytmx.TiledTileLayer):
                continue

            # Assume base layers are the default
            if (
                layer.visible
                and "is_overlay" in layer.properties
                and layer.properties["is_overlay"]
            ):
                tile_layers.append(layer_idx + self.overlay_layer_offset)
        return tile_layers

    def get_animations(self) -> Iterator[Tuple[int, Any]]:
        for gid, d in self.tmx.tile_properties.items():
            try:
                frames = d["frames"]
            except KeyError:
                continue

            if frames:
                yield gid, frames

    def convert_surfaces(
        self, parent: pygame.surface.Surface, alpha: bool = False
    ) -> None:
        """Convert all images in the data to match the parent

        :param parent: pygame.surface.Surface
        :param alpha: preserve alpha channel or not
        :return: None
        """
        images = list()
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
    def tile_size(self) -> Tuple[int, int]:
        """This is the pixel size of tiles to be rendered

        :return: (int, int)
        """
        if self.pre_zoom == 1.0:
            return self.tmx.tilewidth, self.tmx.tileheight
        else:
            return int(self.pre_zoom * self.tmx.tilewidth), int(
                self.pre_zoom * self.tmx.tileheight
            )

    @property
    def map_size(self) -> Tuple[int, int]:
        """This is the size of the map in tiles

        :return: (int, int)
        """
        # This size INCLUDES the padding
        return (
            self.tmx.width + 2 * self.image_pad_tiles[0],
            self.tmx.height + 2 * self.image_pad_tiles[1],
        )

    @property
    def visible_tile_layers(self) -> List[int]:
        """This must return layer numbers, not objects

        :return: [int, int, ...]
        """
        return self.layers_to_render

    @property
    def visible_object_layers(self) -> Iterator[pytmx.TiledObjectGroup]:
        """This must return layer objects

        This is not required for custom data formats.

        :return: Sequence of pytmx object layers/groups
        """
        return (
            layer
            for layer in self.tmx.visible_layers
            if isinstance(layer, pytmx.TiledObjectGroup)
        )

    def get_tile_properties(
        self, x: int, y: int, layer_idx: int
    ) -> Optional[Dict[str, str]]:
        if layer_idx not in self.base_tile_layers:
            layer_idx -= self.overlay_layer_offset
        if not isinstance(self.tmx.layers[layer_idx], pytmx.pytmx.TiledTileLayer):
            return None
        x = min(max(0, x), self.tmx.width - 1)
        y = min(max(0, y), self.tmx.height - 1)
        return cast(
            Optional[Dict[str, str]], self.tmx.get_tile_properties(x, y, layer_idx)
        )

    def _get_tile_image(
        self,
        x: int,
        y: int,
        layer_idx: int,
        image_indexing: bool = True,
        limit_to_visible: bool = True,
    ) -> Optional[pygame.surface.Surface]:
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

        :param id:
        :return:
        """
        return cast(Optional[pygame.surface.Surface], self.tmx.images[id])

    def get_tile_images_by_rect(
        self, rect: pygame.Rect
    ) -> Iterator[Tuple[int, int, int, pygame.surface.Surface]]:
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
                row = layers[layer_idx].data[
                    min(max(0, y - self.image_pad_tiles[1]), self.tmx.height - 1)
                ]

                for x in range(x1, x2 + 1):
                    gid = row[
                        min(max(0, x - self.image_pad_tiles[0]), self.tmx.width - 1)
                    ]
                    if not gid:
                        continue

                    if self.object_group_to_bound_rendering is not None:
                        render_tile = False
                        for obj in self.tmx.layers[
                            self.object_group_to_bound_rendering
                        ]:
                            rect = pygame.Rect(
                                obj.x / self.tmx.tilewidth,
                                obj.y / self.tmx.tileheight,
                                obj.width / self.tmx.tilewidth,
                                obj.height / self.tmx.tileheight,
                            )
                            rect.inflate_ip(2, 2)
                            if rect.collidepoint(
                                x - self.image_pad_tiles[0], y - self.image_pad_tiles[1]
                            ):
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


class ScrollTest:
    SCROLL_SPEED = 5000

    """ Test and demo of pyscroll

    For normal use, please see the quest demo, not this.

    """

    def __init__(self, screen: pygame.surface.Surface, filename: str) -> None:
        self.screen = screen

        # create new data source
        map_data = PaddedTiledMapData(filename, Point(100, 100))

        # create new renderer
        self.map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data, self.screen.get_size()
        )

        # create a font and pre-render some text to be displayed over the map
        f = pygame.font.Font(pygame.font.get_default_font(), 20)
        t = ["scroll demo. press escape to quit", "arrow keys move"]

        # save the rendered text
        self.text_overlay = [f.render(i, True, (180, 180, 0)) for i in t]

        # set our initial viewpoint in the center of the map
        self.center = [
            self.map_layer.map_rect.width / 2,
            self.map_layer.map_rect.height / 2,
        ]

        # the camera vector is used to handle camera movement
        self.camera_acc = [0.0, 0.0, 0.0]
        self.camera_vel = [0.0, 0.0, 0.0]
        self.last_update_time = 0.0

        # true when running
        self.running = False

    def draw(self, surface: pygame.surface.Surface) -> None:

        # tell the map_layer (BufferedRenderer) to draw to the surface
        # the draw function requires a rect to draw to.
        self.map_layer.draw(surface, surface.get_rect())

        # blit our text over the map
        self.draw_text(surface)

    def draw_text(self, surface: pygame.surface.Surface) -> None:
        y = 0
        for text in self.text_overlay:
            surface.blit(text, (0, y))
            y += text.get_height()

    def handle_input(self) -> None:
        """Simply handle pygame input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_EQUALS:
                    self.map_layer.zoom *= 2.0
                elif event.key == pygame.K_MINUS:
                    self.map_layer.zoom *= 0.5
                elif event.key == pygame.K_LEFTBRACKET:
                    self.map_layer.data.decrement_layers_to_render()
                    self.map_layer.redraw_tiles(self.map_layer._buffer)
                elif event.key == pygame.K_RIGHTBRACKET:
                    self.map_layer.data.increment_layers_to_render()
                    self.map_layer.redraw_tiles(self.map_layer._buffer)

            # this will be handled if the window is resized
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
                self.map_layer.set_size((event.w, event.h))

        # these keys will change the camera vector
        # the camera vector changes the center of the viewport,
        # which causes the map to scroll

        # using get_pressed is slightly less accurate than testing for events
        # but is much easier to use.
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            self.camera_acc[1] = -ScrollTest.SCROLL_SPEED * self.last_update_time
        elif pressed[pygame.K_DOWN]:
            self.camera_acc[1] = ScrollTest.SCROLL_SPEED * self.last_update_time
        else:
            self.camera_acc[1] = 0

        if pressed[pygame.K_LEFT]:
            self.camera_acc[0] = -ScrollTest.SCROLL_SPEED * self.last_update_time
        elif pressed[pygame.K_RIGHT]:
            self.camera_acc[0] = ScrollTest.SCROLL_SPEED * self.last_update_time
        else:
            self.camera_acc[0] = 0

    def update(self, td: float) -> None:
        self.last_update_time = td

        friction = pow(0.0001, self.last_update_time)

        # update the camera vector
        self.camera_vel[0] += self.camera_acc[0] * td
        self.camera_vel[1] += self.camera_acc[1] * td

        self.camera_vel[0] *= friction
        self.camera_vel[1] *= friction

        # make sure the movement vector stops when scrolling off the screen if
        # the camera is clamped
        if self.map_layer.clamp_camera:
            if self.center[0] < 0:
                self.center[0] -= self.camera_vel[0]
                self.camera_acc[0] = 0
                self.camera_vel[0] = 0
            if self.center[0] >= self.map_layer.map_rect.width:
                self.center[0] -= self.camera_vel[0]
                self.camera_acc[0] = 0
                self.camera_vel[0] = 0

            if self.center[1] < 0:
                self.center[1] -= self.camera_vel[1]
                self.camera_acc[1] = 0
                self.camera_vel[1] = 0
            if self.center[1] >= self.map_layer.map_rect.height:
                self.center[1] -= self.camera_vel[1]
                self.camera_acc[1] = 0
                self.camera_vel[1] = 0

        self.center[0] += self.camera_vel[0]
        self.center[1] += self.camera_vel[1]

        # set the center somewhere else
        # in a game, you would set center to a playable character
        self.map_layer.center(self.center)

    def run(self) -> None:
        import collections

        clock = pygame.time.Clock()
        self.running = True
        fps = 60.0
        fps_log: Deque[float] = collections.deque(maxlen=20)

        try:
            while self.running:
                # somewhat smoother way to get fps and limit the framerate
                clock.tick(int(fps * 2))

                try:
                    fps_log.append(clock.get_fps())
                    fps = sum(fps_log) / len(fps_log)
                    dt = 1 / fps
                except (OverflowError, ZeroDivisionError):
                    fps = 60.0
                    dt = 1 / fps

                self.handle_input()
                self.update(dt)
                self.draw(self.screen)
                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


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
        test = ScrollTest(screen, filename)
        test.run()
    except Exception as e:
        import traceback

        print(
            traceback.format_exception(
                None, e, e.__traceback__  # <- type(e) by docs, but ignored
            ),
            file=sys.stderr,
            flush=True,
        )
        traceback.print_exc()

    pygame.quit()
