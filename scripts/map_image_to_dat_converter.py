#!/usr/bin/env python

import os
import sys

import pygame


# Run like this: MapImageToDatConverter.py ..\unusedAssets\maps\brecconary.png data\maps\brecconary.dat
def main():
    # Initialize pygame
    pygame.init()

    # Setup to draw maps
    tile_size_pixels = 16
    screen = pygame.display.set_mode((160, 160), pygame.SRCALPHA | pygame.HWSURFACE)
    clock = pygame.time.Clock()

    # Load the map image to convert to dat file
    base_path = os.path.split(os.path.abspath(__file__))[0]
    map_image_file_name = os.path.join(base_path, sys.argv[1])
    print('map_image_file_name =', map_image_file_name, flush=True)
    map_dat_file_name = os.path.join(base_path, sys.argv[2])
    print('mapDatFileName =', map_dat_file_name, flush=True)
    map_image = pygame.image.load(map_image_file_name).convert()
    print('mapImage.get_width() =', map_image.get_width(), flush=True)
    print('mapImage.get_width() / tileSize_pixels =', map_image.get_width() / tile_size_pixels, flush=True)
    print('mapImage.get_height() =', map_image.get_height(), flush=True)
    print('mapImage.get_height() / tileSize_pixels =', map_image.get_height() / tile_size_pixels, flush=True)

    print('Enter symbol for border:', flush=True)
    border_symbol = '\n'
    while border_symbol == '\n':
        border_symbol = sys.stdin.read(1)

    # Convert the image to dat file
    tile_image_to_symbol_map = {}
    with open(map_dat_file_name, 'w') as map_dat_file:
        for map_y in range(map_image.get_height() // tile_size_pixels + 2):
            map_dat_file.write(border_symbol)
        map_dat_file.write('\n')
        for map_y in range(map_image.get_height() // tile_size_pixels):
            map_y_px = map_y * tile_size_pixels
            map_dat_file.write(border_symbol)
            for map_x in range(map_image.get_width() // tile_size_pixels):
                map_x_px = map_x * tile_size_pixels
                current_tile = map_image.subsurface(pygame.Rect(map_x_px, map_y_px, tile_size_pixels, tile_size_pixels))
                screen.blit(current_tile, (0, 0))

                # Determine if the tile has previously been seen
                is_new_tile = True
                for tile, tile_symbol in tile_image_to_symbol_map.items():
                    is_tile_match = True
                    for tile_x in range(tile_size_pixels):
                        for tile_y in range(tile_size_pixels):
                            if tile.get_at((tile_x, tile_y)) != current_tile.get_at((tile_x, tile_y)):
                                is_tile_match = False
                                break
                        if not is_tile_match:
                            break

                    if is_tile_match:
                        symbol = tile_symbol
                        is_new_tile = False
                        break

                if is_new_tile:
                    pygame.display.flip()
                    pygame.event.pump()
                    clock.tick(5)
                    # Prompt user for tile symbol
                    print('Enter symbol for this tile ' + str(map_x) + ',' + str(map_y) + ':', flush=True)
                    symbol = '\n'
                    while symbol == '\n':
                        symbol = sys.stdin.read(1)
                    tile_image_to_symbol_map[current_tile] = symbol

                map_dat_file.write(symbol)
            map_dat_file.write(border_symbol)
            map_dat_file.write('\n')
        for map_y in range(map_image.get_height() // tile_size_pixels + 2):
            map_dat_file.write(border_symbol)

    # Terminate pygame
    pygame.quit()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        print(traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                         e,
                                         e.__traceback__),
              file=sys.stderr, flush=True)
