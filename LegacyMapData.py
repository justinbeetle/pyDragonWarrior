#!/usr/bin/env python

"""
Variant of pyscroll.data.TileMapData.
ScrollTest was copied and modified from pyscroll/apps/demo.py.

Source copied and modified from https://github.com/bitcraft/pyscroll
"""
from typing import Iterator, List, Optional, Tuple

import collections
import pygame
import pyscroll

from GameInfo import GameInfo
from Point import Point


class LegacyMapData(pyscroll.data.PyscrollDataAdapter):  # type: ignore
    BASE_MAP_LAYER = 0
    DECORATION_LAYER = 1
    CHARACTER_LAYER = 2
    OVERLAY_MAP_LAYER = 3

    def __init__(self,
                 game_info: GameInfo,
                 map_name: str,
                 image_pad_tiles: Point = Point(0, 0)):
        super(LegacyMapData, self).__init__()
        self.game_info = game_info
        self.map_name = map_name
        self.image_pad_tiles = Point(image_pad_tiles)

        self.map_size_tiles = Point(
            len(self.game_info.maps[self.map_name].dat[0]),
            len(self.game_info.maps[self.map_name].dat)) + 2 * self.image_pad_tiles

        # Load up the images for the base map and overlay
        self.base_map_images = self.get_map_images_from_game_info(self.game_info.maps[map_name].dat)
        self.overlay_images = None
        overlay_dat = self.game_info.maps[map_name].overlay_dat
        if overlay_dat is not None:
            self.overlay_images = self.get_map_images_from_game_info(overlay_dat)
        self.layers_to_render = self.all_tile_layers

    def get_map_images_from_game_info(self, dat: List[str]) -> List[List[Optional[pygame.surface.Surface]]]:

        def pad_row(row_to_pad: str) -> str:
            pad_width = int(self.image_pad_tiles.w)
            return row_to_pad[0] * pad_width + row_to_pad + row_to_pad[-1] * pad_width

        # Pad dat to generate padded_dat
        padded_dat: List[str] = []

        # Top padding
        padded_row = pad_row(dat[0])
        for i in range(int(self.image_pad_tiles.h)):
            padded_dat.append(padded_row)

        # Middle
        for row in dat:
            padded_dat.append(pad_row(row))

        # Bottom padding
        padded_row = pad_row(dat[-1])
        for i in range(int(self.image_pad_tiles.h) + 1):
            padded_dat.append(padded_row)

        # Generate map_images from padded_dat
        map_images: List[List[Optional[pygame.surface.Surface]]] = []
        for y, row_data in enumerate(padded_dat):
            map_images_row: List[Optional[pygame.surface.Surface]] = []
            for x, tile_symbol in enumerate(row_data):
                if tile_symbol not in self.game_info.tile_symbols:
                    map_images_row.append(None)
                    continue
                # Determine which image to use
                image_idx = 0
                # TODO: Fix hardcoded exception for the bridge tile_symbol of 'b'
                if y > 0 and padded_dat[y-1][x] != tile_symbol and padded_dat[y-1][x] != 'b':
                    image_idx += 8
                if y < len(padded_dat)-1 and padded_dat[y+1][x] != tile_symbol and padded_dat[y+1][x] != 'b':
                    image_idx += 2
                if x > 0 and row_data[x-1] != tile_symbol and row_data[x-1] != 'b':
                    image_idx += 1
                if x < len(row_data)-1 and row_data[x+1] != tile_symbol and row_data[x+1] != 'b':
                    image_idx += 4
                map_images_row.append(self.game_info.random_tile_image(tile_symbol, image_idx))
            map_images.append(map_images_row)

        return map_images

    def set_pc_character_tile(self, pos_dat_tile: Point) -> bool:
        """
        :param pos_dat_tile: Tile position of player character
        :return: If a redraw of the map is needed for the new PC position
        """
        layers_to_render_orig = self.visible_tile_layers
        if self.is_interior(pos_dat_tile):
            self.set_tile_layers_to_render(self.base_tile_layers)
        else:
            self.set_tile_layers_to_render(self.all_tile_layers)
        return layers_to_render_orig != self.visible_tile_layers

    def is_interior(self, pos_dat_tile: Point) -> bool:
        tile_x, tile_y = pos_dat_tile.getAsIntTuple()
        for l in self.overlay_tile_layers:
            if self._get_tile_image(tile_x, tile_y, l,
                                    image_indexing=False, limit_to_visible=False) is not None:
                return True
        return False

    def is_exterior(self, pos_dat_tile: Point) -> bool:
        return not self.is_interior(pos_dat_tile)

    def set_tile_layers_to_render(self, layers_to_render: List[int]) -> None:
        if self.layers_to_render != layers_to_render:
            self.layers_to_render = layers_to_render

    def decrement_layers_to_render(self) -> None:
        self.layers_to_render = self.base_tile_layers

    def increment_layers_to_render(self) -> None:
        self.layers_to_render = self.all_tile_layers

    @property
    def all_tile_layers(self) -> List[int]:
        return self.base_tile_layers + self.overlay_tile_layers

    @property
    def base_tile_layers(self) -> List[int]:
        return [LegacyMapData.BASE_MAP_LAYER]

    @property
    def decoration_layer(self) -> int:
        return LegacyMapData.DECORATION_LAYER

    @property
    def character_layer(self) -> int:
        return LegacyMapData.CHARACTER_LAYER

    @property
    def overlay_tile_layers(self) -> List[int]:
        if self.overlay_images is not None:
            return[LegacyMapData.OVERLAY_MAP_LAYER]
        return []

    def get_animations(self) -> None:
        return

    def convert_surfaces(self, parent: pygame.surface.Surface, alpha: bool=False) -> None:
        """ Convert all images in the data to match the parent

        :param parent: pygame.Surface
        :param alpha: preserve alpha channel or not
        :return: None
        """

        def convert_surfaces_helper(map_images: List[List[Optional[pygame.surface.Surface]]],
                                    parent: pygame.surface.Surface,
                                    alpha: bool=False) -> List[List[Optional[pygame.surface.Surface]]]:
            converted_map_images: List[List[Optional[pygame.surface.Surface]]] = []
            for map_images_row in map_images:
                converted_images_row: List[Optional[pygame.surface.Surface]] = []
                for image in map_images_row:
                    if image is None:
                        converted_images_row.append(None)
                    elif alpha:
                        converted_images_row.append(image.convert_alpha(parent))
                    else:
                        converted_images_row.append(image.convert(parent))
                converted_map_images.append(converted_images_row)
            return converted_map_images

        self.base_map_images = convert_surfaces_helper(self.base_map_images, parent, alpha)
        if self.overlay_images is not None:
            self.overlay_images = convert_surfaces_helper(self.overlay_images, parent, alpha)

    @property
    def tile_size(self) -> Tuple[int, int]:
        """ This is the pixel size of tiles to be rendered
        
        :return: (int, int)
        """
        return self.game_info.tile_size_pixels, self.game_info.tile_size_pixels

    @property
    def map_size(self) -> Tuple[int, int]:
        """ This is the size of the map in tiles

        :return: (int, int)
        """
        # This size INCLUDES the padding
        return self.map_size_tiles.getAsIntTuple()

    @property
    def visible_tile_layers(self) -> List[int]:
        return self.layers_to_render

    @property
    def visible_object_layers(self) -> List[int]:
        return []

    def _get_tile_image(self,
                        x: int,
                        y: int,
                        l: int,
                        image_indexing: bool=True,
                        limit_to_visible: bool=True) -> Optional[pygame.surface.Surface]:
        if l not in self.all_tile_layers or (limit_to_visible and l not in self.layers_to_render):
            return None

        if not image_indexing:
            # With image_indexing, coord (0,0) is where the pad starts.
            # Without image_indexing, coord (0,0) is where the Tiled map starts.
            x = x + int(self.image_pad_tiles[0])
            y = y + int(self.image_pad_tiles[1])

        if l == LegacyMapData.BASE_MAP_LAYER:
            return self.base_map_images[y][x]
        elif l == LegacyMapData.OVERLAY_MAP_LAYER and self.overlay_images is not None:
            return self.overlay_images[y][x]

        return None

    def _get_tile_image_by_id(self, id: int) -> Optional[pygame.surface.Surface]:
        """ Return Image by a custom ID

        Used for animations.  Not required for static maps.

        :param id:
        :return:
        """
        return None

    def get_tile_images_by_rect(self, rect: pygame.Rect) -> Iterator[Tuple[int, int, int, pygame.surface.Surface]]:
        x1, y1, x2, y2 = pyscroll.rect_to_bb(rect)
        tiles_w, tiles_h = self.map_size_tiles.getAsIntTuple()
        x1 = min(max(x1, 0), tiles_w - 1)
        x2 = min(max(x2, 0), tiles_w - 1)
        y1 = min(max(y1, 0), tiles_h - 1)
        y2 = min(max(y2, 0), tiles_h - 1)

        for l in self.visible_tile_layers:
            for y in range(y1, y2+1):
                for x in range(x1, x2+1):
                    tile_image = self._get_tile_image(x, y, l)
                    if tile_image is not None:
                        yield x, y, l, tile_image


class ScrollTest:
    SCROLL_SPEED = 5000

    """ Test and demo of pyscroll

    For normal use, please see the quest demo, not this.

    """
    def __init__(self, screen: pygame.surface.Surface, game_info: GameInfo, map_name: str):
        self.screen = screen

        # create new data source
        map_data = LegacyMapData(game_info, map_name, Point(100, 100))

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


from AudioPlayer import AudioPlayer
class MapViewer:
    def __init__(self) -> None:
        # Initialize pygame
        pygame.init()
        self.audio_player = AudioPlayer()

        # Setup to draw maps
        self.tile_size_pixels = 20
        desired_win_size_pixels = Point(2560, 1340)
        if desired_win_size_pixels is None:
            self.screen: pygame.surface.Surface = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.HWSURFACE)
            self.win_size_pixels: Point = Point(self.screen.get_size())
            self.win_size_tiles: Point = (self.win_size_pixels / self.tile_size_pixels).floor()
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
        self.game_info = GameInfo(base_path, game_xml_path, self.tile_size_pixels)

        self.is_running = True

    def __del__(self) -> None:
        # Terminate pygame
        self.audio_player.terminate()
        pygame.quit()

    def view_map(self, map_name: str) -> None:
        if not self.is_running:
            return

        if self.game_info.maps[map_name].tiled_filename is not None:
            print('Skipping tiled map', map_name, flush=True)
            return

        self.audio_player.play_music(self.game_info.maps[map_name].music)
        ScrollTest(self.screen, self.game_info, map_name).run()


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
