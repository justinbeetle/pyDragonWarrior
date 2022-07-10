import math

from generic_utils.point import Point


def validate_point_values(p: Point, expected_x: Point.PointTypeElemType, expected_y: Point.PointTypeElemType) -> None:
    assert p == (expected_x, expected_y)
    assert p == Point(expected_x, expected_y)

    assert p[0] == expected_x
    assert p.x == expected_x
    assert p.w == expected_x
    assert type(p[0]) == type(expected_x)
    assert type(p.x) == type(expected_x)
    assert type(p.w) == type(expected_x)

    assert p[1] == expected_y
    assert p.y == expected_y
    assert p.h == expected_y
    assert type(p[1]) == type(expected_y)
    assert type(p.y) == type(expected_y)
    assert type(p.h) == type(expected_y)

    assert p.mag() == abs(expected_x + expected_y)
    if isinstance(expected_x, int) and isinstance(expected_y, int):
        assert isinstance(p.mag(), int)
    else:
        assert isinstance(p.mag(), float)


def point_unary_operations(x: Point.PointTypeElemType, y: Point.PointTypeElemType) -> Point:
    p = Point(x, y)
    validate_point_values(p, x, y)
    validate_point_values(p.floor(), int(math.floor(x)), int(math.floor(y)))
    validate_point_values(p.ceil(), int(math.ceil(x)), int(math.ceil(y)))
    validate_point_values(p.round(), int(round(x)), int(round(y)))
    validate_point_values(Point(p.getAsIntTuple()), int(round(x)), int(round(y)))
    validate_point_values(Point(p.getAsFloatTuple()), float(x), float(y))
    return p


def point_binary_operations(x1: int, y1: int, x2: int, y2: int) -> None:
    p1 = point_unary_operations(x1, y1)
    p2 = point_unary_operations(x2, y2)

    # p1+p2
    validate_point_values(p1+p2, x1+x2, y1+y2)
    validate_point_values((x1, y1)+p2, x1+x2, y1+y2)
    validate_point_values(p1+(x2, y2), x1+x2, y1+y2)
    assert (x1, y1)+(x2, y2) != (x1+x2, y1+y2)  # Normal tuples instead concatenate!

    # p2+p1
    validate_point_values(p2+p1, x1+x2, y1+y2)
    validate_point_values((x2, y2)+p1, x1+x2, y1+y2)
    validate_point_values(p2+(x1, y1), x1+x2, y1+y2)
    assert (x2, y2)+(x1, y1) != (x1+x2, y1+y2)  # Normal tuples instead concatenate!

    # p1-p2
    validate_point_values(p1-p2, x1-x2, y1-y2)
    validate_point_values((x1, y1)-p2, x1-x2, y1-y2)
    validate_point_values(p1-(x2, y2), x1-x2, y1-y2)

    # p2-p1
    validate_point_values(p2-p1, x2-x1, y2-y1)
    validate_point_values((x2, y2)-p1, x2-x1, y2-y1)
    validate_point_values(p2-(x1, y1), x2-x1, y2-y1)

    # p1*p2
    validate_point_values(p1*p2, x1*x2, y1*y2)
    validate_point_values((x1, y1)*p2, x1*x2, y1*y2)
    validate_point_values(p1*(x2, y2), x1*x2, y1*y2)

    # p2*p1
    validate_point_values(p2*p1, x1*x2, y1*y2)
    validate_point_values((x2, y2)*p1, x1*x2, y1*y2)
    validate_point_values(p2*(x1, y1), x1*x2, y1*y2)

    if x2 != 0 and y2 != 0:
        # p1/p2
        validate_point_values(p1/p2, x1/x2, y1/y2)
        validate_point_values((x1, y1)/p2, x1/x2, y1/y2)
        validate_point_values(p1/(x2, y2), x1/x2, y1/y2)

        # p1//p2
        validate_point_values(p1//p2, x1//x2, y1//y2)
        validate_point_values((x1, y1)//p2, x1//x2, y1//y2)
        validate_point_values(p1//(x2, y2), x1//x2, y1//y2)

    if x1 != 0 and y1 != 0:
        # p2/p1
        validate_point_values(p2/p1, x2/x1, y2/y1)
        validate_point_values((x2, y2)/p1, x2/x1, y2/y1)
        validate_point_values(p2/(x1, y1), x2/x1, y2/y1)

        # p2//p1
        validate_point_values(p2//p1, x2//x1, y2//y1)
        validate_point_values((x2, y2)//p1, x2//x1, y2//y1)
        validate_point_values(p2//(x1, y1), x2//x1, y2//y1)

    if x2 != 0:
        # p1/x2
        validate_point_values(p1/x2, x1/x2, y1/x2)

        # p1//x2
        validate_point_values(p1//x2, x1//x2, y1//x2)

    if y2 != 0:
        # p1/x2
        validate_point_values(p1/y2, x1/y2, y1/y2)

        # p1//x2
        validate_point_values(p1//y2, x1//y2, y1//y2)

    if x1 != 0:
        # p2/x1
        validate_point_values(p2/x1, x2/x1, y2/x1)

        # p2//x1
        validate_point_values(p2//x1, x2//x1, y2//x1)

    if y1 != 0:
        # p2/y1
        validate_point_values(p2/y1, x2/y1, y2/y1)

        # p2//y1
        validate_point_values(p2//y1, x2//y1, y2//y1)


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
