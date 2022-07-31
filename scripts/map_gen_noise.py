#!/usr/bin/env python

from typing import List

import os

from opensimplex import OpenSimplex

from pydw.game_map_viewer import GameMapViewer
from pydw.game_types import Map


class MapGenNoise:
    @staticmethod
    def gen_map_dat(width: int,
                    height: int,
                    elevation_seed: int,
                    moisture_seed: int) -> List[str]:
        elevation_simplex = OpenSimplex(elevation_seed)
        moisture_simplex = OpenSimplex(moisture_seed)

        dat: List[str] = []
        dat.append('w' * (width + 2))
        for y in range(height):
            edge_dist_y = min(y+1, height-y)
            elevation_factor_y = min(1.0, edge_dist_y/16.0)
            center_dist_y = max(height/2-y, y-height/2)
            moisture_factor_y = min(1.1, 0.75 + center_dist_y/(height/2))
            # print('y=', y, '; moisture_factor_y=', moisture_factor_y)

            row = 'w'
            for x in range(width):
                edge_dist_x = min(x+1, width-x)
                elevation_factor_x = min(1.0, edge_dist_x/16.0)
                moisture_factor_x = 1.0

                elevation_noise = ((elevation_simplex.noise2(x/8.0, y/8.0) + 1) / 2.0
                                   * elevation_factor_x * elevation_factor_y)
                moisture_noise = ((moisture_simplex.noise2(x/20.0, y/20.0) + 1) / 2.0
                                  * moisture_factor_x
                                  * moisture_factor_y)
                # print('x=', x, "; y=", y, "; elevation_noise=", elevation_noise)
                if elevation_noise > 0.725:  # mountain elevation
                    row += 'M'  # mountain
                elif elevation_noise > 0.625:  # hill elevation
                    if moisture_noise > 0.60:
                        row += 'f'  # forest
                    else:
                        row += 'm'  # hill
                elif elevation_noise > 0.35:  # high plains elevation
                    if moisture_noise > 0.95:
                        row += 's'  # swamp
                    elif moisture_noise > 0.60:
                        row += 'f'  # forest
                    elif moisture_noise > 0.15:
                        row += '_'  # plain
                    else:
                        row += '-'  # desert
                elif elevation_noise > 0.30:  # low plains elevation
                    if moisture_noise > 0.95:
                        row += 's'  # swamp
                    elif moisture_noise > 0.60:
                        row += 'f'  # forest
                    elif moisture_noise > 0.30:
                        row += '_'  # plain
                    else:
                        row += '-'  # desert
                else:  # ocean elevation
                    if edge_dist_x > 20 and edge_dist_y > 20:  # ocean elevation away from the edge of the map
                        if moisture_noise > 0.25:
                            row += 'w'  # water
                        else:
                            row += '-'  # desert (as beach)
                    else:
                        row += 'w'  # water
            row += 'w'
            dat.append(row)
        dat.append('w'*(width+2))
        return dat


def main() -> None:
    # Generate and render a map
    map_name = 'mapGenNoise'
    viewer = GameMapViewer(os.path.join(os.path.dirname(__file__), os.path.pardir))
    elevation_seed = 0      # int(random.random() * 10000)
    moisture_seed = 123456  # int(random.random() * 10000)
    print('elevation_seed =', elevation_seed)
    print('moisture_seed  =', moisture_seed)
    viewer.game_info.maps[map_name] = Map.create(map_name,
                                                 MapGenNoise.gen_map_dat(192,
                                                                         96,
                                                                         elevation_seed,
                                                                         moisture_seed))
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
