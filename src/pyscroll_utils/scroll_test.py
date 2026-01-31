"""
ScrollTest was copied and modified from pyscroll/apps/demo.py.

Source copied and modified from https://github.com/bitcraft/pyscroll
"""

import collections

import pygame
import pyscroll


class ScrollTest:
    SCROLL_SPEED = 5000

    """ Test and demo of pyscroll

    For normal use, please see the quest demo, not this.

    """

    def __init__(self, screen: pygame.surface.Surface, map_data: pyscroll.data.PyscrollDataAdapter) -> None:
        self.screen = screen

        # create new renderer
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())

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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                if event.key == pygame.K_EQUALS:
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
        clock = pygame.time.Clock()
        self.running = True
        fps = 60.0
        fps_log: collections.deque[float] = collections.deque(maxlen=20)

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
