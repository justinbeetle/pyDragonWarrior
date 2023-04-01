""" Module defining the Point class """

# Imports to support type annotations
from __future__ import annotations
from typing import Tuple, Union

import math


PointTypeElemType = Union[float, int]


class Point(Tuple[PointTypeElemType, PointTypeElemType]):
    """Immutable 2D Point class extending a tuple for ease of use with pygame, where points are specified as tuples.

    WARNING:  Point addition adds the pairs of X and Y coordinates instead of concatenating the tuple.  Point
    multiplcation multiplies
    intentional violation of the Liskov Substitution Principal.  As such, instances of Point and Tuple need to be used
    together carefully.
    """

    PointTupleType = Union["Point", Tuple[PointTypeElemType, PointTypeElemType]]
    ScalarOrPointTupleType = Union[PointTypeElemType, PointTupleType]

    def __new__(cls, x: ScalarOrPointTupleType = 0, y: PointTypeElemType = 0) -> Point:
        # TODO: Remove type ignores in this method once mypy bug https://github.com/python/mypy/issues/14890 is fixed
        if isinstance(x, tuple):
            return tuple.__new__(cls, (x[0], x[1]))  # type: ignore
        return tuple.__new__(cls, (x, y))  # type: ignore

    @property
    def x(self) -> PointTypeElemType:
        """Return the X coordinate"""
        if isinstance(self[0], (float, int)):
            return self[0]
        return float(self[0])

    @property
    def w(self) -> PointTypeElemType:
        """Return the X, or width, coordinate"""
        return self.x

    @property
    def y(self) -> PointTypeElemType:
        """Return the Y coordinate"""
        if isinstance(self[1], (float, int)):
            return self[1]
        return float(self[1])

    @property
    def h(self) -> PointTypeElemType:
        """Return the Y, or height, coordinate"""
        return self.y

    def __add__(self, point: PointTupleType) -> Point:  # type: ignore
        """Return a Point calculated as the Vector addition of two Points

        WARNING: The behavior for adding tuples is concatenation, so this behavior constitutes a violation of the
        Liskov Substitution Principal.
        """
        return Point(self.x + point[0], self.y + point[1])

    def __radd__(self, point: PointTupleType) -> Point:
        """Return a Point calculated as the Vector addition of two Points

        WARNING: The behavior for adding tuples is concatenation, so this behavior constitutes a violation of the
        Liskov Substitution Principal.
        """
        return self + point

    def __sub__(self, point: PointTupleType) -> Point:
        return Point(self.x - point[0], self.y - point[1])

    def __rsub__(self, point: PointTupleType) -> Point:
        return Point(point) - self

    def __mul__(self, point: ScalarOrPointTupleType) -> Point:  # type: ignore[override]
        """Return a Point calculated as either the Vector or scalar multiplication of two Points

        WARNING: The behavior for multiplying a tuple by an int is repeated concatenation, so this behavior constitutes
        a violation of the Liskov Substitution Principal.
        """
        if isinstance(point, tuple):
            return Point(self.x * point[0], self.y * point[1])
        return Point(self.x * point, self.y * point)

    def __rmul__(self, point: ScalarOrPointTupleType) -> Point:  # type: ignore[override]
        """Return a Point calculated as either the Vector or scalar multiplication of two Points

        WARNING: The behavior for multiplying a tuple by an int is repeated concatenation, so this behavior constitutes
        a violation of the Liskov Substitution Principal.
        """
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
        """Returns a Point where both the X and Y coordinates are converted to int using the floor function"""
        return Point(int(math.floor(self.x)), int(math.floor(self.y)))

    def ceil(self) -> Point:
        """Returns a Point where both the X and Y coordinates are converted to int using the ceil function"""
        return Point(int(math.ceil(self.x)), int(math.ceil(self.y)))

    def round(self) -> Point:
        """Returns a Point where both the X and Y coordinates are converted to int using the round function"""
        return Point(int(round(self.x)), int(round(self.y)))

    def mag(self) -> float:
        """Returns the square root of (X*X + Y*Y)"""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.x!r}, {self.y!r})"

    def get_as_int_tuple(self) -> Tuple[int, int]:
        """Returns the Point as tuple of ints using the round function"""
        return int(round(self.x)), int(round(self.y))

    def get_as_float_tuple(self) -> Tuple[float, float]:
        """Returns the Point as tuple of floats"""
        return float(self.x), float(self.y)
