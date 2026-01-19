"""
Variant of pyscroll.orthographic.BufferedRenderer.

FUTURE: Drop if and when the changes in this version are picked up in a pyscroll release.
        These changes are in pyscroll pull request https://github.com/bitcraft/pyscroll/pull/75.
"""

from typing import Any, Callable, Optional, Union

from pygame import Rect, Surface
from pyscroll.common import Vector2DInt
from pyscroll.data import PyscrollDataAdapter
from pyscroll.orthographic import BufferedRenderer as PyscrolBufferedRenderer


class BufferedRenderer(PyscrolBufferedRenderer):  # type: ignore
    """Variant of pyscroll.BufferedRenderer where the blit list sort key used in _draw_surfaces
    is configurable via the added set_blit_list_sort_key method.
    """

    def __init__(
        self,
        data: PyscrollDataAdapter,
        size: Vector2DInt,
    ) -> None:
        super().__init__(data, size)
        self.blit_list_sort_key: Optional[Callable[[tuple[int, int, int, int, int, Surface, Optional[int]]], Any]] = (
            None
        )

    def _draw_surfaces(
        self,
        surface: Surface,
        offset: Vector2DInt,
        surfaces: list[Union[tuple[Surface, Rect, int], tuple[Surface, Rect, int, int]]],
    ) -> None:
        """
        Override of method in pyscroll.BufferedRenderer modified to sort
        blit_list using key self.blit_list_sort_key.

        Draw surfaces while correcting overlapping tile layers.

        Args:
            surface: destination
            offset: offset to compensate for buffer alignment
            surfaces: sequence of surfaces to blit

        """
        ox, oy = offset
        left, top = self._tile_view.topleft
        hit = self._layer_quadtree.hit
        get_tile = self.data.get_tile_image
        tile_layers = tuple(sorted(self.data.visible_tile_layers))
        top_layer = tile_layers[-1]
        blit_list = []
        sprite_damage = set()
        order = 0

        # get tile that sprites overlap
        for i in surfaces:
            s, r, l = i[:3]

            # sprite must not be over the top layer for damage to matter
            if l <= top_layer:
                damage_rect = Rect(i[1])
                damage_rect.move_ip(ox, oy)
                # tall sprites only damage a portion of the bottom of their sprite
                if self.tall_sprites:
                    damage_rect = Rect(
                        damage_rect.x,
                        damage_rect.y + (damage_rect.height - self.tall_sprites),
                        damage_rect.width,
                        self.tall_sprites,
                    )
                for hit_rect in hit(damage_rect):
                    sprite_damage.add((l, hit_rect))

            # add surface to draw list
            blend = i[3] if len(i) >= 4 else None
            x, y, w, h = r
            blit_op = l, 1, x, y, order, s, blend
            blit_list.append(blit_op)
            order += 1

        # TODO: heightmap to avoid checking tiles in each cell
        # from bottom to top, clear screen and add tiles into the draw
        # list.  while getting tiles for the damage, compare the damaged
        # layer to the highest tile.  if the highest tile is greater or
        # equal to the damaged layer, then add the entire column of
        # tiles to the blit_list.  if not, then discard the column and
        # do not update the screen when the damage was done.
        for dl, damage_rect in sprite_damage:
            x, y, w, h = damage_rect
            tx = x // w + left
            ty = y // h + top
            # TODO: heightmap
            for l in [l for l in tile_layers if dl <= l]:
                tile = get_tile(tx, ty, l)
                if tile:
                    sx = x - ox
                    sy = y - oy
                    blit_op = l, 0, sx, sy, order, tile, None
                    blit_list.append(blit_op)
                    order += 1

        # finally sort and do the thing
        blit_list.sort(key=self.blit_list_sort_key)
        draw_list2 = [(s, (x, y), None, blend) if blend else (s, (x, y)) for _, _, x, y, _, s, blend in blit_list]
        surface.blits(draw_list2, doreturn=False)  # type: ignore

    def set_blit_list_sort_key(
        self,
        key: Optional[Callable[[tuple[int, int, int, int, int, Surface, Optional[int]]], Any]],
    ) -> None:
        """Set the key function for sorting list of blit operations on sprites
        and tiles overlaying sprites in the _draw_surfaces method.  The elements
        in the list are 7-tuples with the following contents:
            element 0 (int): layer number
            element 1 (int): priority - 0 for tile, 1 for sprite
            element 2 (int): x coordinate for the left  corner of the surface
            element 3 (int): y coordinate for the top-left corner of the surface
            element 4 (int): the pre-sorted order of elements in the list
            element 5 (Surface): the source image for the blit
            element 6 (Optional[int]): Special flags for blit operation

        The default key is None, yeilding a sort first on element 0, then 1, 2, ..., 6.

        To alternatinely sort first on layer, then bottom y coordinate, then priority,
        the key function could be set to the following lambda function:
            lambda x: (x[0], x[3]+x[5].get_height(), x[1])
        """
        self.blit_list_sort_key = key
