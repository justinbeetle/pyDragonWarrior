#!/usr/bin/env python

"""
Variant of pyscroll.data.TileMapData.
ScrollTest was copied and modified from pyscroll/apps/demo.py.

Source copied and modified from https://github.com/bitcraft/pyscroll
"""
from typing import Iterator, Optional

import pygame
import pyscroll

from generic_utils.point import Point
from pydw.game_info import GameInfo
from pyscroll_utils.scroll_test import ScrollTest


class LegacyMapData(pyscroll.data.PyscrollDataAdapter):  # type: ignore
    BASE_MAP_LAYER = 0
    DECORATION_LAYER = 1
    CHARACTER_LAYER = 2
    OVERLAY_MAP_LAYER = 3
    CLOUD_LAYER = 4

    def __init__(self, game_info: GameInfo, map_name: str, image_pad_tiles: Point = Point(0, 0)):
        super().__init__()
        self.game_info = game_info
        self.map_name = map_name
        self.image_pad_tiles = Point(image_pad_tiles)

        self.map_size_tiles = (
            Point(
                len(self.game_info.maps[self.map_name].dat[0]),
                len(self.game_info.maps[self.map_name].dat),
            )
            + 2 * self.image_pad_tiles
        )

        # Load up the images for the base map and overlay
        self.base_map_images = self.get_map_images_from_game_info(self.game_info.maps[map_name].dat)
        self.overlay_images = None
        overlay_dat = self.game_info.maps[map_name].overlay_dat
        if overlay_dat is not None:
            self.overlay_images = self.get_map_images_from_game_info(overlay_dat)
        self.layers_to_render = self.all_tile_layers

    def reload_data(self) -> None:
        """Reload the tiles"""
        pass

    def get_map_images_from_game_info(self, dat: list[str]) -> list[list[Optional[pygame.surface.Surface]]]:
        def pad_row(row_to_pad: str) -> str:
            pad_width = int(self.image_pad_tiles.w)
            return row_to_pad[0] * pad_width + row_to_pad + row_to_pad[-1] * pad_width

        # Pad dat to generate padded_dat
        padded_dat: list[str] = []

        # Top padding
        padded_row = pad_row(dat[0])
        for _ in range(int(self.image_pad_tiles.h)):
            padded_dat.append(padded_row)

        # Middle
        for row in dat:
            padded_dat.append(pad_row(row))

        # Bottom padding
        padded_row = pad_row(dat[-1])
        for _ in range(int(self.image_pad_tiles.h) + 1):
            padded_dat.append(padded_row)

        # Generate map_images from padded_dat
        map_images: list[list[Optional[pygame.surface.Surface]]] = []
        for y, row_data in enumerate(padded_dat):
            map_images_row: list[Optional[pygame.surface.Surface]] = []
            for x, tile_symbol in enumerate(row_data):
                if tile_symbol not in self.game_info.tile_symbols:
                    map_images_row.append(None)
                    continue
                # Determine which image to use
                image_idx = 0
                # TODO: Fix hardcoded exception for the bridge tile_symbol of 'b'
                if y > 0 and padded_dat[y - 1][x] != tile_symbol and padded_dat[y - 1][x] != "b":
                    image_idx += 8
                if y < len(padded_dat) - 1 and padded_dat[y + 1][x] != tile_symbol and padded_dat[y + 1][x] != "b":
                    image_idx += 2
                if x > 0 and row_data[x - 1] != tile_symbol and row_data[x - 1] != "b":
                    image_idx += 1
                if x < len(row_data) - 1 and row_data[x + 1] != tile_symbol and row_data[x + 1] != "b":
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
        tile_x, tile_y = pos_dat_tile.get_as_int_tuple()
        for layer_idx in self.overlay_tile_layers:
            if (
                self._get_tile_image(
                    tile_x,
                    tile_y,
                    layer_idx,
                    image_indexing=False,
                    limit_to_visible=False,
                )
                is not None
            ):
                return True
        return False

    def is_exterior(self, pos_dat_tile: Point) -> bool:
        return not self.is_interior(pos_dat_tile)

    def get_monster_set_name(self, pos_dat_tile: Point) -> Optional[str]:
        _ = pos_dat_tile  # appease pylint - pos_dat_tile is needed to conform to the interface
        return None

    def set_tile_layers_to_render(self, layers_to_render: list[int]) -> None:
        if self.layers_to_render != layers_to_render:
            self.layers_to_render = layers_to_render

    def decrement_layers_to_render(self) -> None:
        self.layers_to_render = self.base_tile_layers

    def increment_layers_to_render(self) -> None:
        self.layers_to_render = self.all_tile_layers

    @property
    def all_tile_layers(self) -> list[int]:
        return self.base_tile_layers + self.overlay_tile_layers

    @property
    def base_tile_layers(self) -> list[int]:
        return [LegacyMapData.BASE_MAP_LAYER]

    @property
    def decoration_layer(self) -> int:
        return LegacyMapData.DECORATION_LAYER

    @property
    def character_layer(self) -> int:
        return LegacyMapData.CHARACTER_LAYER

    @property
    def cloud_layer(self) -> int:
        return LegacyMapData.CLOUD_LAYER

    @property
    def overlay_tile_layers(self) -> list[int]:
        if self.overlay_images is not None:
            return [LegacyMapData.OVERLAY_MAP_LAYER]
        return []

    def get_animations(self) -> None:
        return

    def convert_surfaces(self, parent: pygame.surface.Surface, alpha: bool = False) -> None:
        """Convert all images in the data to match the parent

        :param parent: pygame.surface.Surface
        :param alpha: preserve alpha channel or not
        :return: None
        """

        def convert_surfaces_helper(
            map_images: list[list[Optional[pygame.surface.Surface]]],
        ) -> list[list[Optional[pygame.surface.Surface]]]:
            converted_map_images: list[list[Optional[pygame.surface.Surface]]] = []
            for map_images_row in map_images:
                converted_images_row: list[Optional[pygame.surface.Surface]] = []
                for image in map_images_row:
                    if image is None:
                        converted_images_row.append(None)
                    elif alpha:
                        converted_images_row.append(image.convert_alpha())
                    else:
                        converted_images_row.append(image.convert(parent))
                converted_map_images.append(converted_images_row)
            return converted_map_images

        self.base_map_images = convert_surfaces_helper(self.base_map_images)
        if self.overlay_images is not None:
            self.overlay_images = convert_surfaces_helper(self.overlay_images)

    @property
    def tile_size(self) -> tuple[int, int]:
        """This is the pixel size of tiles to be rendered

        :return: (int, int)
        """
        return self.game_info.tile_size_pixels, self.game_info.tile_size_pixels

    @property
    def map_size(self) -> tuple[int, int]:
        """This is the size of the map in tiles

        :return: (int, int)
        """
        # This size INCLUDES the padding
        return self.map_size_tiles.get_as_int_tuple()

    @property
    def visible_tile_layers(self) -> list[int]:
        return self.layers_to_render

    @property
    def visible_object_layers(self) -> list[int]:
        return []

    def _get_tile_image(
        self,
        x: int,
        y: int,
        l: int,
        image_indexing: bool = True,
        limit_to_visible: bool = True,
    ) -> Optional[pygame.surface.Surface]:
        layer_idx = l
        if layer_idx not in self.all_tile_layers or (limit_to_visible and layer_idx not in self.layers_to_render):
            return None

        if not image_indexing:
            # With image_indexing, coord (0,0) is where the pad starts.
            # Without image_indexing, coord (0,0) is where the Tiled map starts.
            x = x + int(self.image_pad_tiles[0])
            y = y + int(self.image_pad_tiles[1])

        if layer_idx == LegacyMapData.BASE_MAP_LAYER:
            return self.base_map_images[y][x]
        elif layer_idx == LegacyMapData.OVERLAY_MAP_LAYER and self.overlay_images is not None:
            return self.overlay_images[y][x]

        return None

    def _get_tile_image_by_id(self, id: int) -> Optional[pygame.surface.Surface]:
        """Return Image by a custom ID

        Used for animations.  Not required for static maps.

        :param id:
        :return:
        """
        return None

    def get_tile_images_by_rect(self, rect: pygame.Rect) -> Iterator[tuple[int, int, int, pygame.surface.Surface]]:
        x1, y1, x2, y2 = pyscroll.common.rect_to_bb(rect)
        tiles_w, tiles_h = self.map_size_tiles.get_as_int_tuple()
        x1 = min(max(x1, 0), tiles_w - 1)
        x2 = min(max(x2, 0), tiles_w - 1)
        y1 = min(max(y1, 0), tiles_h - 1)
        y2 = min(max(y2, 0), tiles_h - 1)

        for layer_idx in self.visible_tile_layers:
            for y in range(y1, y2 + 1):
                for x in range(x1, x2 + 1):
                    tile_image = self._get_tile_image(x, y, layer_idx)
                    if tile_image is not None:
                        yield x, y, layer_idx, tile_image


class MapViewer:
    def __init__(self) -> None:
        # Initialize pygame
        pygame.init()
        from pygame_utils.audio_player import AudioPlayer

        self.audio_player = AudioPlayer()

        # Setup to draw maps
        self.tile_size_pixels = 20
        desired_win_size_pixels = Point(2560, 1340)
        if desired_win_size_pixels is None:
            self.screen: pygame.surface.Surface = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.HWSURFACE,
            )
            self.win_size_pixels: Point = Point(self.screen.get_size())
            self.win_size_tiles: Point = (self.win_size_pixels / self.tile_size_pixels).floor()
        else:
            self.win_size_tiles = (desired_win_size_pixels / self.tile_size_pixels).floor()
            self.win_size_pixels = self.win_size_tiles * self.tile_size_pixels
            self.screen = pygame.display.set_mode(
                self.win_size_pixels.get_as_int_tuple(),
                pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.HWSURFACE,
            )
        self.image_pad_tiles = self.win_size_tiles // 2 * 4

        # Initialize GameInfo
        import os

        base_path = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
        game_xml_path = os.path.join(base_path, "data", "game.xml")
        self.game_info = GameInfo(base_path, game_xml_path, self.tile_size_pixels, 1, self.win_size_pixels)

        self.is_running = True

    def __del__(self) -> None:
        # Terminate pygame
        self.audio_player.terminate()
        pygame.quit()

    def view_map(self, map_name: str) -> None:
        if not self.is_running:
            return

        if self.game_info.maps[map_name].tiled_filename is not None:
            print("Skipping tiled map", map_name, flush=True)
            return

        self.audio_player.play_music(self.game_info.maps[map_name].music)

        ScrollTest(self.screen, LegacyMapData(self.game_info, map_name, Point(100, 100))).run()


def main() -> None:
    # Iterate through and render the different maps
    viewer = MapViewer()
    for map_name in viewer.game_info.maps:
        viewer.view_map(map_name)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import sys
        import traceback

        print(
            traceback.format_exception(None, e, e.__traceback__),  # <- type(e) by docs, but ignored
            file=sys.stderr,
            flush=True,
        )
        traceback.print_exc()
