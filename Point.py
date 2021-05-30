#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Tuple, Union

import math


class Point(Tuple[Union[float, int], Union[float, int]]):
    PointTypeElemType = Union[float, int]
    PointTupleType = Union['Point', Tuple[PointTypeElemType, PointTypeElemType]]
    ScalarOrPointTupleType = Union[PointTypeElemType, PointTupleType]
   
    def __new__(cls, x: ScalarOrPointTupleType = 0, y: PointTypeElemType = 0) -> Point:
        if isinstance(x, tuple):
            return tuple.__new__(Point, (x[0], x[1]))
        return tuple.__new__(Point, (x, y))
   
    def __init__(self, x: ScalarOrPointTupleType = 0, y: PointTypeElemType = 0) -> None:
        pass

    @property
    def x(self) -> PointTypeElemType:
        if isinstance(self[0], float) or isinstance(self[0], int):
            return self[0]
        else:
            return float(self[0])

    @property
    def w(self) -> PointTypeElemType:
        if isinstance(self[0], float) or isinstance(self[0], int):
            return self[0]
        else:
            return float(self[0])

    @property
    def y(self) -> PointTypeElemType:
        if isinstance(self[1], float) or isinstance(self[1], int):
            return self[1]
        else:
            return float(self[1])

    @property
    def h(self) -> PointTypeElemType:
        if isinstance(self[1], float) or isinstance(self[1], int):
            return self[1]
        else:
            return float(self[1])

    # Point addition has a signature which is intentionally incompatible with the supertype 'tuple'
    def __add__(self, p: PointTupleType) -> Point:  # type: ignore
        return Point(self.x + p[0], self.y + p[1])

    def __radd__(self, p: PointTupleType) -> Point:
        return self + p

    def __sub__(self, p: PointTupleType) -> Point:
        return Point(self.x - p[0], self.y - p[1])

    def __rsub__(self, p: PointTupleType) -> Point:
        if isinstance(p, tuple):
            return Point(p) - self
        return NotImplemented

    def __mul__(self, p: ScalarOrPointTupleType) -> Point:
        if isinstance(p, tuple):
            return Point(self.x * p[0], self.y * p[1])
        return Point(self.x * p, self.y * p)

    def __rmul__(self, p: ScalarOrPointTupleType) -> Point:
        return self * p

    def __truediv__(self, p: ScalarOrPointTupleType) -> Point:
        if isinstance(p, tuple):
            return Point(self.x / p[0], self.y / p[1])
        return Point(self.x / p, self.y / p)

    def __rtruediv__(self, p: PointTupleType) -> Point:
        if isinstance(p, tuple):
            return Point(p) / self
        return NotImplemented

    def __floordiv__(self, p: ScalarOrPointTupleType) -> Point:
        if isinstance(p, tuple):
            return Point(self.x // p[0], self.y // p[1])
        return Point(self.x // p, self.y // p)

    def __rfloordiv__(self, p: PointTupleType) -> Point:
        if isinstance(p, tuple):
            return Point(p) / self
        return NotImplemented

    def floor(self) -> Point:
        return Point(math.floor(self.x), math.floor(self.y))

    def ceil(self) -> Point:
        return Point(math.ceil(self.x), math.ceil(self.y))

    def round(self) -> Point:
        return Point(int(round(self.x)), int(round(self.y)))

    def mag(self) -> float:
        return abs(self.x + self.y)

    def __str__(self) -> str:
        return "(%s, %s)" % (self.x, self.y)

    def __repr__(self) -> str:
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)

    def getAsIntTuple(self) -> Tuple[int, int]:
        return int(round(self.x)), int(round(self.y))

    def getAsFloatTuple(self) -> Tuple[float, float]:
        return float(self.x), float(self.y)


def main() -> None:
    p1 = Point()
    p2 = Point(1, 4)
    p3 = Point(2, 7)
    p4 = (2, 2)
    p5 = Point(p4)
    p6 = Point(2, 2)
    p7 = Point(Point(2, 2))
   
    print('p1 =', p1, flush=True)
    print('p2 =', p2, flush=True)
    print('p3 =', p3, flush=True)
    print('p4 =', p4, flush=True)
    print('p5 =', p5, flush=True)
    print('p6 =', p6, flush=True)
    print('p7 =', p7, flush=True)
    print('p5 == p3', p5 == p3, flush=True)
    print('p5 == p4', p5 == p4, flush=True)
    print('p4 == p5', p4 == p5, flush=True)
    print('p5 == p5', p5 == p5, flush=True)
    print('p5 == p6', p5 == p6, flush=True)
    print('p5 == p7', p5 == p7, flush=True)
   
    print('p1.x =', p1.x, flush=True)
    print('p1.y =', p1.y, flush=True)
    print('p1[0] =', p1[0], flush=True)
    print('p1[1] =', p1[1], flush=True)
   
    print('p4[0] =', p4[0], flush=True)
    print('p4[1] =', p4[1], flush=True)

    print('p1[0] =', p1[0], flush=True)
    print('p1[1] =', p1[1], flush=True)
    print('p4[0] =', p4[0], flush=True)
    print('p4[1] =', p4[1], flush=True)
   
    print('p2 + p3 =', p2 + p3, flush=True)
    print('p2 + p4 =', p2 + p4, flush=True)
    print('p4 + p2 =', p4 + p2, flush=True)
   
    print('p2 - p3 =', p2 - p3, flush=True)
    print('p2 - p4 =', p2 - p4, flush=True)
    print('p4 - p2 =', p4 - p2, flush=True)
   
    print('p2 * p3 =', p2 * p3, flush=True)
    print('p2 * p4 =', p2 * p4, flush=True)
    print('p4 * p2 =', p4 * p2, flush=True)
    print('p2 * 5 =', p2 * 5, flush=True)
   
    print('p3 / p2 =', p3 / p2, flush=True)
    print('p3 / p4 =', p3 / p4, flush=True)
    print('p4 / p3 =', p4 / p3, flush=True)
    print('p3 / 2 =', p3 / 2, flush=True)
   
    print('p3 // p2 =', p3 // p2, flush=True)
    print('p3 // p4 =', p3 // p4, flush=True)
    print('p4 // p3 =', p4 // p3, flush=True)
    print('p3 // 2 =', p3 // 2, flush=True)
   
    print('(p3 / p2).ceil() =', (p3 / p2).ceil(), flush=True)
    print('(p3 / p4).ceil() =', (p3 / p4).ceil(), flush=True)
    print('(p4 / p3).ceil() =', (p4 / p3).ceil(), flush=True)
    print('(p3 / 2).ceil() =', (p3 / 2).ceil(), flush=True)


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
