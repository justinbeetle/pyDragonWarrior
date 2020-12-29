#!/usr/bin/env python

"""
Variant of pyscroll.data.TileMapData.
ScrollTest was copied and modified from pyscroll/apps/demo.py.

Source copied and modified from https://github.com/bitcraft/pyscroll
"""
import pygame
import pyscroll
import pytmx


class PaddedTiledMapData(pyscroll.data.PyscrollDataAdapter):
    """ For data loaded from pytmx

    Use of this class requires a recent version of pytmx.
    """

    def __init__(self, tmx, image_pad_tiles=(0, 0)):
        super(PaddedTiledMapData, self).__init__()
        self.tmx = tmx
        self.image_pad_tiles = image_pad_tiles
        self.reload_animations()
        self.layers_to_render = self.get_num_layers()

    def get_num_layers(self):
        return sum(1 for l in self.tmx.visible_tile_layers)

    def decrement_layers_to_render(self):
        self.layers_to_render = max(1, self.layers_to_render-1)

    def increment_layers_to_render(self):
        self.layers_to_render = min(self.get_num_layers(), self.layers_to_render+1)

    def get_animations(self):
        for gid, d in self.tmx.tile_properties.items():
            try:
                frames = d['frames']
            except KeyError:
                continue

            if frames:
                yield gid, frames

    def convert_surfaces(self, parent, alpha=False):
        pass
        """ Convert all images in the data to match the parent

        :param parent: pygame.Surface
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
    def tile_size(self):
        """ This is the pixel size of tiles to be rendered
        
        :return: (int, int)
        """
        return self.tmx.tilewidth, self.tmx.tileheight

    @property
    def map_size(self):
        """ This is the size of the map in tiles
        
        :return: (int, int)
        """
        return self.tmx.width + 2*self.image_pad_tiles[0], self.tmx.height + 2*self.image_pad_tiles[1]

    @property
    def visible_tile_layers(self):
        """ This must return layer numbers, not objects
        
        :return: [int, int, ...]
        """
        visible_tile_layers = []
        for idx, l in enumerate(self.tmx.visible_tile_layers):
            if idx >= self.layers_to_render:
                break
            visible_tile_layers.append(l)
        return visible_tile_layers

    @property
    def visible_object_layers(self):
        """ This must return layer objects

        This is not required for custom data formats.

        :return: Sequence of pytmx object layers/groups
        """
        return (layer for layer in self.tmx.visible_layers
                if isinstance(layer, pytmx.TiledObjectGroup))

    def _get_tile_image(self, x, y, l):
        if l not in self.visible_tile_layers:
            return None
        try:
            return self.tmx.get_tile_image(
                min(max(0, x-self.image_pad_tiles[0]), self.tmx.width-1),
                min(max(0, y-self.image_pad_tiles[1]), self.tmx.height-1),
                l)
        except ValueError:
            return None

    def _get_tile_image_by_id(self, id):
        """ Return Image by a custom ID

        Used for animations.  Not required for static maps.

        :param id:
        :return:
        """
        return self.tmx.images[id]

    def get_tile_images_by_rect(self, rect):
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
            for y in range(y1, y2+1):
                row = layers[l].data[min(max(0, y-self.image_pad_tiles[1]), self.tmx.height-1)]

                for x in range(x1, x2+1):
                    gid = row[min(max(0, x-self.image_pad_tiles[0]), self.tmx.width-1)]
                    if not gid:
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
    def __init__(self, screen, filename):
        self.screen = screen

        # load data from pytmx
        tmx_data = pytmx.util_pygame.load_pygame(filename)

        # create new data source
        map_data = PaddedTiledMapData(tmx_data, (100, 100))

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
        import collections

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
