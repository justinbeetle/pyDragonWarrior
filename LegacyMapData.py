#!/usr/bin/env python

"""
Variant of pyscroll.data.TileMapData.
ScrollTest was copied and modified from pyscroll/apps/demo.py.

Source copied and modified from https://github.com/bitcraft/pyscroll
"""
from typing import List, Optional

import collections
import pygame
import pyscroll

from GameInfo import GameInfo
from GameTypes import MapDecoration, Tile
from Point import Point


class LegacyMapData(pyscroll.data.PyscrollDataAdapter):
    def __init__(self,
                 game_info: GameInfo,
                 map_name: str,
                 image_pad_tiles: Point = Point(0, 0)):
        super(LegacyMapData, self).__init__()
        self.game_info = game_info
        self.map_name = map_name
        self.image_pad_tiles = Point(image_pad_tiles)

        self.map_size_tiles = self.game_info.maps[self.map_name].size + 2 * self.image_pad_tiles

        # Load up the images for the base map and overlay
        self.base_map_images = self.get_map_images_from_game_info(self.game_info.maps[map_name].dat)
        self.overlay_images = None
        if self.game_info.maps[map_name].overlay_dat is not None:
            self.overlay_images = self.get_map_images_from_game_info(self.game_info.maps[map_name].overlay_dat)
        self.layers_to_render = self.get_num_layers()

    def get_map_images_from_game_info(self, dat: List[str]) -> List[List[Optional[pygame.Surface]]]:

        def pad_row(row_to_pad: str) -> str:
            return row_to_pad[0] * self.image_pad_tiles.w + row_to_pad + row_to_pad[-1] * self.image_pad_tiles.w

        # Pad dat to generate padded_dat
        padded_dat: List[str] = []

        # Top padding
        padded_row = pad_row(dat[0])
        for i in range(self.image_pad_tiles.h):
            padded_dat.append(padded_row)

        # Middle
        for row in dat:
            padded_dat.append(pad_row(row))

        # Bottom padding
        padded_row = pad_row(dat[-1])
        for i in range(self.image_pad_tiles.h + 1):
            padded_dat.append(padded_row)

        # Generate map_images from padded_dat
        map_images: List[List[Optional[pygame.Surface]]] = []
        for y, row_data in enumerate(padded_dat):
            map_images_row: List[Optional[pygame.Surface]] = []
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

    def get_num_layers(self):
        if self.overlay_images is None:
            return 1
        return 2

    def decrement_layers_to_render(self):
        self.layers_to_render = max(1, self.layers_to_render-1)

    def increment_layers_to_render(self):
        self.layers_to_render = min(self.get_num_layers(), self.layers_to_render+1)

    def get_animations(self):
        return None

    def convert_surfaces(self, parent, alpha=False):
        """ Convert all images in the data to match the parent

        :param parent: pygame.Surface
        :param alpha: preserve alpha channel or not
        :return: None
        """

        def convert_surfaces_helper(map_images: List[List[Optional[pygame.Surface]]],
                                    parent: pygame.Surface,
                                    alpha=False) -> List[List[Optional[pygame.Surface]]]:
            converted_map_images: List[List[Optional[pygame.Surface]]] = []
            for map_images_row in map_images:
                converted_images_row: List[Optional[pygame.Surface]] = []
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
    def tile_size(self):
        """ This is the pixel size of tiles to be rendered
        
        :return: (int, int)
        """
        return self.game_info.tile_size_pixels, self.game_info.tile_size_pixels

    @property
    def map_size(self):
        """ This is the size of the map in tiles

        :return: (int, int)
        """
        # This size INCLUDES the padding
        return self.map_size_tiles.w, self.map_size_tiles.h

    @property
    def visible_tile_layers(self):
        # 0 = Base Map
        # 4 = Overlay Map (Roofs)
        tile_layers = [0]
        if self.overlay_images is not None and self.layers_to_render > 1:
            tile_layers.append(4)
        return tile_layers

    @property
    def visible_object_layers(self):
        return []

    def _get_tile_image(self, x, y, l):
        if l == 0:   # Base Map
            return self.base_map_images[y][x]
        elif l == 4 and self.layers_to_render > 1:  # Overlay Map
            return self.overlay_images[y][x]

        return None

    def _get_tile_image_by_id(self, id):
        """ Return Image by a custom ID

        Used for animations.  Not required for static maps.

        :param id:
        :return:
        """
        return None

    def get_tile_images_by_rect(self, rect):
        x1, y1, x2, y2 = pyscroll.rect_to_bb(rect)
        x1 = min(max(x1, 0), self.map_size_tiles.w - 1)
        x2 = min(max(x2, 0), self.map_size_tiles.w - 1)
        y1 = min(max(y1, 0), self.map_size_tiles.h - 1)
        y2 = min(max(y2, 0), self.map_size_tiles.h - 1)

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
    def __init__(self, screen: pygame.Surface, game_info: GameInfo, map_name: str):
        self.screen = screen

        # create new data source
        map_data = LegacyMapData(game_info, map_name, (100, 100))

        # create new renderer
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())

        # create a font and pre-render some text to be displayed over the map
        f = pygame.font.Font(pygame.font.get_default_font(), 20)
        t = ["scroll demo. press escape to quit",
             "arrow keys move"]

        # save the rendered text
        self.text_overlay = [f.render(i, 1, (180, 180, 0)) for i in t]

        # set our initial viewpoint in the center of the map
        self.center = [self.map_layer.map_rect.width / 2,
                       self.map_layer.map_rect.height / 2]

        # the camera vector is used to handle camera movement
        self.camera_acc = [0, 0, 0]
        self.camera_vel = [0, 0, 0]
        self.last_update_time = 0

        # true when running
        self.running = False

    def draw(self, surface):

        # tell the map_layer (BufferedRenderer) to draw to the surface
        # the draw function requires a rect to draw to.
        self.map_layer.draw(surface, surface.get_rect())

        # blit our text over the map
        self.draw_text(surface)

    def draw_text(self, surface):
        y = 0
        for text in self.text_overlay:
            surface.blit(text, (0, y))
            y += text.get_height()

    def handle_input(self):
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

    def update(self, td):
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

    def run(self):
        clock = pygame.time.Clock()
        self.running = True
        fps = 60.
        fps_log = collections.deque(maxlen=20)

        try:
            while self.running:
                # somewhat smoother way to get fps and limit the framerate
                clock.tick(fps*2)

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
            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.HWSURFACE)
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
        self.game_info = GameInfo(base_path, game_xml_path, self.tile_size_pixels)

        self.is_running = True

    def __del__(self) -> None:
        # Terminate pygame
        self.audio_player.terminate()
        pygame.quit()

    def view_map(self, map_name: str) -> None:
        if not self.is_running:
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
