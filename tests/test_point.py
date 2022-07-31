""" Module defining tests for the Point class """

import math

from generic_utils.point import Point, PointTypeElemType


def validate_point_values(point: Point,
                          expected_x: PointTypeElemType,
                          expected_y: PointTypeElemType) -> None:
    """ Validate that the Point has the expected coordinates and magnitude """
    assert point == (expected_x, expected_y)
    assert point == Point(expected_x, expected_y)

    assert point[0] == expected_x
    assert point.x == expected_x
    assert point.w == expected_x
    assert isinstance(point[0], type(expected_x))
    assert isinstance(point.x, type(expected_x))
    assert isinstance(point.w, type(expected_x))

    assert point[1] == expected_y
    assert point.y == expected_y
    assert point.h == expected_y
    assert isinstance(point[1], type(expected_y))
    assert isinstance(point.y, type(expected_y))
    assert isinstance(point.h, type(expected_y))

    assert point.mag() == math.sqrt(expected_x * expected_x + expected_y * expected_y)


def point_unary_operations(x: PointTypeElemType,
                           y: PointTypeElemType) -> Point:
    """ Test unary operations on a point with the provided coordinates """
    point = Point(x, y)
    validate_point_values(point, x, y)
    validate_point_values(point.floor(), int(math.floor(x)), int(math.floor(y)))
    validate_point_values(point.ceil(), int(math.ceil(x)), int(math.ceil(y)))
    validate_point_values(point.round(), int(round(x)), int(round(y)))
    validate_point_values(Point(point.get_as_int_tuple()), int(round(x)), int(round(y)))
    validate_point_values(Point(point.get_as_float_tuple()), float(x), float(y))
    return point


def point_binary_operations(x1: PointTypeElemType,
                            y1: PointTypeElemType,
                            x2: PointTypeElemType,
                            y2: PointTypeElemType) -> None:
    """ Test binary operations on a pair of points with the provided coordinates """
    point1 = point_unary_operations(x1, y1)
    point2 = point_unary_operations(x2, y2)

    # point1+point2
    validate_point_values(point1+point2, x1+x2, y1+y2)
    validate_point_values((x1, y1)+point2, x1+x2, y1+y2)
    validate_point_values(point1+(x2, y2), x1+x2, y1+y2)
    assert len((x1, y1)+(x2, y2)) != len((x1+x2, y1+y2))  # Normal tuples instead concatenate!

    # point2+point1
    validate_point_values(point2+point1, x1+x2, y1+y2)
    validate_point_values((x2, y2)+point1, x1+x2, y1+y2)
    validate_point_values(point2+(x1, y1), x1+x2, y1+y2)
    assert len((x2, y2)+(x1, y1)) != len((x1+x2, y1+y2))  # Normal tuples instead concatenate!

    # point1-point2
    validate_point_values(point1-point2, x1-x2, y1-y2)
    validate_point_values((x1, y1)-point2, x1-x2, y1-y2)
    validate_point_values(point1-(x2, y2), x1-x2, y1-y2)

    # point2-point1
    validate_point_values(point2-point1, x2-x1, y2-y1)
    validate_point_values((x2, y2)-point1, x2-x1, y2-y1)
    validate_point_values(point2-(x1, y1), x2-x1, y2-y1)

    # point1*point2
    validate_point_values(point1*point2, x1*x2, y1*y2)
    validate_point_values((x1, y1)*point2, x1*x2, y1*y2)
    validate_point_values(point1*(x2, y2), x1*x2, y1*y2)

    # point2*point1
    validate_point_values(point2*point1, x1*x2, y1*y2)
    validate_point_values((x2, y2)*point1, x1*x2, y1*y2)
    validate_point_values(point2*(x1, y1), x1*x2, y1*y2)

    # point1*x2
    validate_point_values(point1*x2, x1*x2, y1*x2)

    # point1*y2
    validate_point_values(point1*y2, x1*y2, y1*y2)

    # point2*x1
    validate_point_values(point2*x1, x1*x2, x1*y2)

    # point2*y1
    validate_point_values(point2*y1, y1*x2, y1*y2)

    if x2 != 0 and y2 != 0:
        # point1/point2
        validate_point_values(point1/point2, x1/x2, y1/y2)
        validate_point_values((x1, y1)/point2, x1/x2, y1/y2)
        validate_point_values(point1/(x2, y2), x1/x2, y1/y2)

        # point1//point2
        validate_point_values(point1//point2, x1//x2, y1//y2)
        validate_point_values((x1, y1)//point2, x1//x2, y1//y2)
        validate_point_values(point1//(x2, y2), x1//x2, y1//y2)

    if x1 != 0 and y1 != 0:
        # point2/point1
        validate_point_values(point2/point1, x2/x1, y2/y1)
        validate_point_values((x2, y2)/point1, x2/x1, y2/y1)
        validate_point_values(point2/(x1, y1), x2/x1, y2/y1)

        # point2//point1
        validate_point_values(point2//point1, x2//x1, y2//y1)
        validate_point_values((x2, y2)//point1, x2//x1, y2//y1)
        validate_point_values(point2//(x1, y1), x2//x1, y2//y1)

    if x2 != 0:
        # point1/x2
        validate_point_values(point1/x2, x1/x2, y1/x2)

        # point1//x2
        validate_point_values(point1//x2, x1//x2, y1//x2)

    if y2 != 0:
        # p1/x2
        validate_point_values(point1/y2, x1/y2, y1/y2)

        # p1//x2
        validate_point_values(point1//y2, x1//y2, y1//y2)

    if x1 != 0:
        # p2/x1
        validate_point_values(point2/x1, x2/x1, y2/x1)

        # p2//x1
        validate_point_values(point2//x1, x2//x1, y2//x1)

    if y1 != 0:
        # p2/y1
        validate_point_values(point2/y1, x2/y1, y2/y1)

        # p2//y1
        validate_point_values(point2//y1, x2//y1, y2//y1)


def test_int_coordinates() -> None:
    """ Test Points with int coordinates """
    point_binary_operations(0, 0, 0, 0)
    point_binary_operations(0, 1, 2, 3)
    point_binary_operations(0, -1, -2, -3)
    point_binary_operations(-10, 9, 4, -6)


def test_float_coordinates() -> None:
    """ Test Points with float coordinates """
    point_binary_operations(0.0, 0.0, 0.0, 0.0)
    point_binary_operations(0.0, 1.25, 2.5, 3.75)
    point_binary_operations(0.0, -1.5, -2.0, -3.25)
    point_binary_operations(-10.5, 9.0, 4.25, -6.75)


def test_mixed_coordinates() -> None:
    """ Test Points with a mix of float and int coordinates """
    point_binary_operations(0, 0, 0.0, 0.0)
    point_binary_operations(0, 1, 2.5, 3.75)
    point_binary_operations(0, -2, -2.0, -3.25)
    point_binary_operations(-10.5, 9.0, 4, -6)
