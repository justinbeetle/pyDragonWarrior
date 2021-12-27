#!/usr/bin/env python

"""
Variant of pyscroll.data.TileMapData.
ScrollTest was copied and modified from pyscroll/apps/demo.py.

Source copied and modified from https://github.com/bitcraft/pyscroll
"""
from typing import Any, cast, Dict, Iterator, List, Optional, Tuple

import pygame
import pyscroll
import pytmx

from Point import Point


class PaddedTiledMapData(pyscroll.data.PyscrollDataAdapter):  # type: ignore
    """ For data loaded from pytmx

    Use of this class requires a recent version of pytmx.
    """

    def __init__(self, tmx_filename: str,
                 image_pad_tiles: Point=Point(0, 0),
                 desired_tile_size: Optional[int] = None):
        super(PaddedTiledMapData, self).__init__()

        # load data from pytmx
        self.tmx = pytmx.util_pygame.load_pygame(tmx_filename)

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
        black_tile.fill(pygame.Color('black'))
        self.tmx.images.append(black_tile)

        self.image_pad_tiles = image_pad_tiles
        self.reload_animations()
        self.overlay_layer_offset = 0
        self.layers_to_render = self.all_tile_layers
        self.object_group_to_bound_rendering: Optional[int] = None

        decoration_layer = None
        character_layer = None
        for idx, l in enumerate(self.tmx.layers):
            if 'decoration' == l.name:
                decoration_layer = idx
            elif 'character' == l.name:
                character_layer = idx
        if decoration_layer is None:
            self.overlay_layer_offset += 1
            decoration_layer = self.base_tile_layers[-1] + self.overlay_layer_offset
        if character_layer is None:
            self.overlay_layer_offset += 1
            character_layer = self.base_tile_layers[-1] + self.overlay_layer_offset
        self._decoration_layer = decoration_layer
        self._character_layer = character_layer

        '''print('self.tmx', self.tmx, flush=True)
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
        print('character layer', self.character_layer, flush=True)'''

    def set_pc_character_tile(self, pos_dat_tile: Point) -> bool:
        """
        :param pos_dat_tile: Tile position of player character
        :return: If a redraw of the map is needed for the new PC position
        """
        object_group_to_bound_rendering_orig = self.object_group_to_bound_rendering
        self.object_group_to_bound_rendering = self.get_overlapping_object_group_index(pos_dat_tile)
        if self.object_group_to_bound_rendering is not None:
            self.set_tile_layers_to_render(self.base_tile_layers)
        else:
            self.set_tile_layers_to_render(self.all_tile_layers)
        return object_group_to_bound_rendering_orig != self.object_group_to_bound_rendering

    def is_interior(self, pos_dat_tile: Point) -> bool:
        return self.get_overlapping_object_group_index(pos_dat_tile) is not None

    def is_exterior(self, pos_dat_tile: Point) -> bool:
        return not self.is_interior(pos_dat_tile)

    def get_overlapping_object_group_index(self, pos_dat_tile: Point) -> Optional[int]:
        # Iterate through TiledOjbectGroup layers looking for any layer which the PC collides with tile
        for idx, l in enumerate(self.tmx.layers):
            if not isinstance(l, pytmx.pytmx.TiledObjectGroup):
                continue
            for obj in l:
                rect = pygame.Rect(obj.x / self.tmx.tilewidth,
                                   obj.y / self.tmx.tileheight,
                                   obj.width / self.tmx.tilewidth,
                                   obj.height / self.tmx.tileheight)
                if rect.collidepoint(pos_dat_tile.getAsIntTuple()):
                    return idx
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
        for l in self.all_tile_layers:
            if l in self.layers_to_render:
                new_layers.append(l)
            elif not layer_added:
                new_layers.append(l)
                layer_added = True
        self.layers_to_render = new_layers

    @property
    def all_tile_layers(self) -> List[int]:
        return self.base_tile_layers + self.overlay_tile_layers

    @property
    def base_tile_layers(self) -> List[int]:
        tile_layers = []
        for idx, l in enumerate(self.tmx.layers):
            # Skip non-tile layers
            if not isinstance(l, pytmx.pytmx.TiledTileLayer):
                continue

            # Assume base layers are the default
            if l.visible and ('is_overlay' not in l.properties or not l.properties['is_overlay']):
                tile_layers.append(idx)
        return tile_layers

    @property
    def decoration_layer(self) -> int:
        return self._decoration_layer

    @property
    def character_layer(self) -> int:
        return self._character_layer

    @property
    def overlay_tile_layers(self) -> List[int]:
        tile_layers = []
        for idx, l in enumerate(self.tmx.layers):
            # Skip non-tile layers
            if not isinstance(l, pytmx.pytmx.TiledTileLayer):
                continue

            # Assume base layers are the default
            if l.visible and 'is_overlay' in l.properties and l.properties['is_overlay']:
                tile_layers.append(idx + self.overlay_layer_offset)
        return tile_layers

    def get_animations(self) -> Iterator[Tuple[int, Any]]:
        for gid, d in self.tmx.tile_properties.items():
            try:
                frames = d['frames']
            except KeyError:
                continue

            if frames:
                yield gid, frames

    def convert_surfaces(self, parent: pygame.surface.Surface, alpha: bool=False) -> None:
        """ Convert all images in the data to match the parent

        :param parent: pygame.surface.Surface
        :param alpha: preserve alpha channel or not
        :return: None
        """
        images = list()
        for i in self.tmx.images:
            try:
                if alpha:
                    images.append(i.convert_alpha(parent))
                else:
                    images.append(i.convert(parent))
            except AttributeError:
                images.append(None)
        self.tmx.images = images

    @property
    def tile_size(self) -> Tuple[int, int]:
        """ This is the pixel size of tiles to be rendered
        
        :return: (int, int)
        """
        if self.pre_zoom == 1.0:
            return self.tmx.tilewidth, self.tmx.tileheight
        else:
            return int(self.pre_zoom*self.tmx.tilewidth), int(self.pre_zoom*self.tmx.tileheight)

    @property
    def map_size(self) -> Tuple[int, int]:
        """ This is the size of the map in tiles
        
        :return: (int, int)
        """
        # This size INCLUDES the padding
        return self.tmx.width + 2*self.image_pad_tiles[0], self.tmx.height + 2*self.image_pad_tiles[1]

    @property
    def visible_tile_layers(self) -> List[int]:
        """ This must return layer numbers, not objects
        
        :return: [int, int, ...]
        """
        return self.layers_to_render

    @property
    def visible_object_layers(self) -> Iterator[pytmx.TiledObjectGroup]:
        """ This must return layer objects

        This is not required for custom data formats.

        :return: Sequence of pytmx object layers/groups
        """
        return (layer for layer in self.tmx.visible_layers
                if isinstance(layer, pytmx.TiledObjectGroup))

    def get_tile_properties(self, x: int, y: int, l: int) -> Optional[Dict[str, str]]:
        if l not in self.base_tile_layers:
            l = l - self.overlay_layer_offset
        if not isinstance(self.tmx.layers[l], pytmx.pytmx.TiledTileLayer):
            return None
        x = min(max(0, x), self.tmx.width-1)
        y = min(max(0, y), self.tmx.height-1)
        return cast(Optional[Dict[str, str]], self.tmx.get_tile_properties(x, y, l))

    def _get_tile_image(self,
                        x: int,
                        y: int,
                        l: int,
                        image_indexing: bool=True,
                        limit_to_visible: bool=True) -> Optional[pygame.surface.Surface]:
        if l not in self.visible_tile_layers and limit_to_visible:
            return None
        if l not in self.base_tile_layers:
            l = l - self.overlay_layer_offset
        if not isinstance(self.tmx.layers[l], pytmx.pytmx.TiledTileLayer):
            return None
        if image_indexing:
            # With image_indexing, coord (0,0) is where the pad starts.
            # Without image_indexing, coord (0,0) is where the Tiled map starts.
            x = min(max(0, x-self.image_pad_tiles[0]), self.tmx.width-1)
            y = min(max(0, y-self.image_pad_tiles[1]), self.tmx.height-1)
        if self.object_group_to_bound_rendering is not None:
            render_tile = False
            for obj in self.tmx.layers[self.object_group_to_bound_rendering]:
                rect = pygame.Rect(obj.x / self.tmx.tilewidth,
                                   obj.y / self.tmx.tileheight,
                                   obj.width / self.tmx.tilewidth,
                                   obj.height / self.tmx.tileheight)
                rect.inflate_ip(2, 2)
                if rect.collidepoint(x, y):
                    render_tile = True
                    break
            if not render_tile:
                return cast(Optional[pygame.surface.Surface], self.tmx.images[-1])
        try:
            return cast(Optional[pygame.surface.Surface], self.tmx.get_tile_image(x, y, l))
        except ValueError:
            return None

    def _get_tile_image_by_id(self, id: int) -> Optional[pygame.surface.Surface]:
        """ Return Image by a custom ID

        Used for animations.  Not required for static maps.

        :param id:
        :return:
        """
        return cast(Optional[pygame.surface.Surface], self.tmx.images[id])

    def get_tile_images_by_rect(self, rect: pygame.Rect) -> Iterator[Tuple[int, int, int, pygame.surface.Surface]]:
        """ Speed up data access

        More efficient because data is accessed and cached locally
        """

        x1, y1, x2, y2 = pyscroll.rect_to_bb(rect)
        images = self.tmx.images
        layers = self.tmx.layers
        at = self._animated_tile
        tracked_gids = self._tracked_gids
        anim_map = self._animation_map
        track = bool(self._animation_queue)

        for l in self.visible_tile_layers:
            if l not in self.base_tile_layers:
                l = l - self.overlay_layer_offset

            if not isinstance(layers[l], pytmx.pytmx.TiledTileLayer):
                continue

            for y in range(y1, y2+1):
                row = layers[l].data[min(max(0, y-self.image_pad_tiles[1]), self.tmx.height-1)]

                for x in range(x1, x2+1):
                    gid = row[min(max(0, x-self.image_pad_tiles[0]), self.tmx.width-1)]
                    if not gid:
                        continue

                    if self.object_group_to_bound_rendering is not None:
                        render_tile = False
                        for obj in self.tmx.layers[self.object_group_to_bound_rendering]:
                            rect = pygame.Rect(obj.x / self.tmx.tilewidth,
                                               obj.y / self.tmx.tileheight,
                                               obj.width / self.tmx.tilewidth,
                                               obj.height / self.tmx.tileheight)
                            rect.inflate_ip(2, 2)
                            if rect.collidepoint(x-self.image_pad_tiles[0], y-self.image_pad_tiles[1]):
                                render_tile = True
                                break
                        if not render_tile:
                            yield x, y, l, images[-1]
                            continue
                    
                    if track and gid in tracked_gids:
                        anim_map[gid].positions.add((x, y, l))

                    try:
                        # animated, so return the correct frame
                        yield x, y, l, at[(x, y, l)]

                    except KeyError:
                        # not animated, so return surface from data, if any
                        yield x, y, l, images[gid]


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
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())

        # create a font and pre-render some text to be displayed over the map
        f = pygame.font.Font(pygame.font.get_default_font(), 20)
        t = ["scroll demo. press escape to quit",
             "arrow keys move"]

        # save the rendered text
        self.text_overlay = [f.render(i, True, (180, 180, 0)) for i in t]

        # set our initial viewpoint in the center of the map
        self.center = [self.map_layer.map_rect.width / 2,
                       self.map_layer.map_rect.height / 2]

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
        """ Simply handle pygame input events
        """
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
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
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

        friction = pow(.0001, self.last_update_time)

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
        fps_log: collections.deque[float] = collections.deque(maxlen=20)

        try:
            while self.running:
                # somewhat smoother way to get fps and limit the framerate
                clock.tick(int(fps*2))

                try:
                    fps_log.append(clock.get_fps())
                    fps = sum(fps_log)/len(fps_log)
                    dt = 1/fps
                except ZeroDivisionError:
                    continue

                self.handle_input()
                self.update(dt)
                self.draw(self.screen)
                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


if __name__ == "__main__":
    import sys

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    pygame.display.set_caption('pyscroll Test')

    try:
        filename = sys.argv[1]
    except IndexError:
        filename = "data/maps/tiled/alefgard.tmx"

    try:
        test = ScrollTest(screen, filename)
        test.run()
    except Exception as e:
        import traceback
        print(traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                         e,
                                         e.__traceback__),
              file=sys.stderr, flush=True)
        traceback.print_exc()

    pygame.quit()
