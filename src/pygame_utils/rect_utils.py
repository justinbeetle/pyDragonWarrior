"""Utilities to supplement pygame.Rect"""

from typing import Optional, Union

from pygame import Rect


def rect_collideline(
    rect: Rect, line: Union[tuple[tuple[int, int], tuple[int, int]], tuple[int, int, int, int]]
) -> bool:
    """Return true if the rectangle collides with the line, else false."""
    # Expand the width and height of the rectangle by one pixel so they are treated as
    # part of the rectangle, per the following note from the pygame-ce docs for clipline.
    #
    # From pygame-ce docs for the pygame.Rect.clipline:
    #     The rect.bottom and rect.right attributes of a pygame.Rectpygame object for
    #     storing rectangular coordinates always lie one pixel outside of its actual border.
    clipped_line = Rect(rect.left, rect.top, rect.width + 1, rect.height + 1).clipline(line)
    return len(clipped_line) == 2 and clipped_line[0] != clipped_line[1]


def rect_intersection(rect1: Rect, rect2: Rect) -> Optional[Rect]:
    """Get a rectangle for the intersection of two rectangles, or None if they don't collide."""
    left = max(rect1.left, rect2.left)
    top = max(rect1.top, rect2.top)
    right = min(rect1.right, rect2.right)
    bottom = min(rect1.bottom, rect2.bottom)
    width = right - left
    height = bottom - top
    if width > 0 and height > 0:
        return Rect(left, top, width, height)
    return None
