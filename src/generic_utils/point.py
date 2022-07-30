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

    @property
    def x(self) -> PointTypeElemType:
        if isinstance(self[0], float) or isinstance(self[0], int):
            return self[0]
        else:
            return float(self[0])

    @property
    def w(self) -> PointTypeElemType:
        return self.x

    @property
    def y(self) -> PointTypeElemType:
        if isinstance(self[1], float) or isinstance(self[1], int):
            return self[1]
        else:
            return float(self[1])

    @property
    def h(self) -> PointTypeElemType:
        return self.y

    # Point addition has a signature which is intentionally incompatible with the supertype 'tuple'
    def __add__(self, point: PointTupleType) -> Point:  # type: ignore
        return Point(self.x + point[0], self.y + point[1])

    def __radd__(self, point: PointTupleType) -> Point:
        return self + point

    def __sub__(self, point: PointTupleType) -> Point:
        return Point(self.x - point[0], self.y - point[1])

    def __rsub__(self, point: PointTupleType) -> Point:
        return Point(point) - self

    def __mul__(self, point: ScalarOrPointTupleType) -> Point:  # type: ignore[override]
        if isinstance(point, tuple):
            return Point(self.x * point[0], self.y * point[1])
        return Point(self.x * point, self.y * point)

    def __rmul__(self, point: ScalarOrPointTupleType) -> Point:  # type: ignore[override]
        return self * point

    def __truediv__(self, point: ScalarOrPointTupleType) -> Point:
        if isinstance(point, tuple):
            return Point(self.x / point[0], self.y / point[1])
        return Point(self.x / point, self.y / point)

    def __rtruediv__(self, point: PointTupleType) -> Point:
        return Point(point) / self

    def __floordiv__(self, point: ScalarOrPointTupleType) -> Point:
        if isinstance(point, tuple):
            return Point(self.x // point[0], self.y // point[1])
        return Point(self.x // point, self.y // point)

    def __rfloordiv__(self, point: PointTupleType) -> Point:
        return Point(point) // self

    def floor(self) -> Point:
        return Point(int(math.floor(self.x)), int(math.floor(self.y)))

    def ceil(self) -> Point:
        return Point(int(math.ceil(self.x)), int(math.ceil(self.y)))

    def round(self) -> Point:
        return Point(int(round(self.x)), int(round(self.y)))

    def mag(self) -> PointTypeElemType:
        return abs(self.x + self.y)

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.x!r}, {self.y!r})'

    def get_as_int_tuple(self) -> Tuple[int, int]:
        return int(round(self.x)), int(round(self.y))

    def get_as_float_tuple(self) -> Tuple[float, float]:
        return float(self.x), float(self.y)
