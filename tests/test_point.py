import math

from generic_utils.point import Point


def validate_point_values(point: Point,
                          expected_x: Point.PointTypeElemType,
                          expected_y: Point.PointTypeElemType) -> None:
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

    assert point.mag() == abs(expected_x + expected_y)
    if isinstance(expected_x, int) and isinstance(expected_y, int):
        assert isinstance(point.mag(), int)
    else:
        assert isinstance(point.mag(), float)


def point_unary_operations(x: Point.PointTypeElemType, y: Point.PointTypeElemType) -> Point:
    point = Point(x, y)
    validate_point_values(point, x, y)
    validate_point_values(point.floor(), int(math.floor(x)), int(math.floor(y)))
    validate_point_values(point.ceil(), int(math.ceil(x)), int(math.ceil(y)))
    validate_point_values(point.round(), int(round(x)), int(round(y)))
    validate_point_values(Point(point.get_as_int_tuple()), int(round(x)), int(round(y)))
    validate_point_values(Point(point.get_as_float_tuple()), float(x), float(y))
    return point


def point_binary_operations(x1: int, y1: int, x2: int, y2: int) -> None:
    point1 = point_unary_operations(x1, y1)
    point2 = point_unary_operations(x2, y2)

    # point1+point2
    validate_point_values(point1+point2, x1+x2, y1+y2)
    validate_point_values((x1, y1)+point2, x1+x2, y1+y2)
    validate_point_values(point1+(x2, y2), x1+x2, y1+y2)
    assert (x1, y1)+(x2, y2) != (x1+x2, y1+y2)  # Normal tuples instead concatenate!

    # point2+point1
    validate_point_values(point2+point1, x1+x2, y1+y2)
    validate_point_values((x2, y2)+point1, x1+x2, y1+y2)
    validate_point_values(point2+(x1, y1), x1+x2, y1+y2)
    assert (x2, y2)+(x1, y1) != (x1+x2, y1+y2)  # Normal tuples instead concatenate!

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


def test_int_coordinates():
    point_binary_operations(0, 0, 0, 0)
    point_binary_operations(0, 1, 2, 3)
    point_binary_operations(0, -1, -2, -3)
    point_binary_operations(-10, 9, 4, -6)


def test_float_coordinates():
    point_binary_operations(0.0, 0.0, 0.0, 0.0)
    point_binary_operations(0.0, 1.25, 2.5, 3.75)
    point_binary_operations(0.0, -1.5, -2.0, -3.25)
    point_binary_operations(-10.5, 9.0, 4.25, -6.75)


def test_mixed_coordinates():
    point_binary_operations(0, 0, 0.0, 0.0)
    point_binary_operations(0, 1, 2.5, 3.75)
    point_binary_operations(0, -2, -2.0, -3.25)
    point_binary_operations(-10.5, 9.0, 4, -6)
