from pytest import raises
from page_controllers.pagination import Pagination


def test_calc():
    class TestPagination(Pagination):
        def __init__(self, contents_count: int):
            super().__init__(contents_count=contents_count)

        def page_button(self, _: int):
            pass

        def sync(self):
            pass

    pagination = TestPagination(100)

    # 引数の例外検知のテスト
    with raises(AssertionError):
        pagination._calc(100)
        pagination._calc(-10)

    # 右行きのテスト
    assert pagination._calc(0) == []
    assert pagination._calc(5) == []
    assert pagination._calc(9) == []
    assert pagination._calc(10) == [(1, 1)]
    assert pagination._calc(15) == [(1, 1)]
    assert pagination._calc(19) == [(1, 1)]
    assert pagination._calc(20) == [(2, 2)]
    assert pagination._calc(25) == [(2, 2)]
    assert pagination._calc(29) == [(2, 2)]
    assert pagination._calc(30) == [(3, 3)]
    assert pagination._calc(35) == [(3, 3)]
    assert pagination._calc(39) == [(3, 3)]
    assert pagination._calc(40) == [(4, 4)]
    assert pagination._calc(45) == [(4, 4)]
    assert pagination._calc(49) == [(4, 4)]
    assert pagination._calc(50) == [(4, 4), (3, 5)]
    assert pagination._calc(55) == [(4, 4), (3, 5)]
    assert pagination._calc(59) == [(4, 4), (3, 5)]
    assert pagination._calc(60) == [(4, 4), (4, 6)]
    assert pagination._calc(65) == [(4, 4), (4, 6)]
    assert pagination._calc(69) == [(4, 4), (4, 6)]
    assert pagination._calc(70) == [(4, 4), (4, 6), (3, 7)]
    assert pagination._calc(75) == [(4, 4), (4, 6), (3, 7)]
    assert pagination._calc(79) == [(4, 4), (4, 6), (3, 7)]
    assert pagination._calc(80) == [(4, 4), (4, 6), (4, 8)]
    assert pagination._calc(85) == [(4, 4), (4, 6), (4, 8)]
    assert pagination._calc(89) == [(4, 4), (4, 6), (4, 8)]
    assert pagination._calc(90) == [(4, 4), (4, 6), (4, 8), (4, 9)]
    assert pagination._calc(95) == [(4, 4), (4, 6), (4, 8), (4, 9)]
    assert pagination._calc(99) == [(4, 4), (4, 6), (4, 8), (4, 9)]

    # 左行きのテスト
    pagination.current_page_index = 9
    assert pagination._calc(99) == []
    assert pagination._calc(95) == []
    assert pagination._calc(90) == []
    assert pagination._calc(89) == [(3, 8)]
    assert pagination._calc(85) == [(3, 8)]
    assert pagination._calc(80) == [(3, 8)]
    assert pagination._calc(79) == [(2, 7)]
    assert pagination._calc(75) == [(2, 7)]
    assert pagination._calc(70) == [(2, 7)]
    assert pagination._calc(69) == [(1, 6)]
    assert pagination._calc(65) == [(1, 6)]
    assert pagination._calc(60) == [(1, 6)]
    assert pagination._calc(59) == [(0, 5)]
    assert pagination._calc(55) == [(0, 5)]
    assert pagination._calc(50) == [(0, 5)]
    assert pagination._calc(49) == [(0, 5), (1, 4)]
    assert pagination._calc(45) == [(0, 5), (1, 4)]
    assert pagination._calc(40) == [(0, 5), (1, 4)]
    assert pagination._calc(39) == [(0, 5), (0, 3)]
    assert pagination._calc(35) == [(0, 5), (0, 3)]
    assert pagination._calc(30) == [(0, 5), (0, 3)]
    assert pagination._calc(29) == [(0, 5), (0, 3), (1, 2)]
    assert pagination._calc(25) == [(0, 5), (0, 3), (1, 2)]
    assert pagination._calc(20) == [(0, 5), (0, 3), (1, 2)]
    assert pagination._calc(19) == [(0, 5), (0, 3), (0, 1)]
    assert pagination._calc(15) == [(0, 5), (0, 3), (0, 1)]
    assert pagination._calc(10) == [(0, 5), (0, 3), (0, 1)]
    assert pagination._calc(9) == [(0, 5), (0, 3), (0, 1), (0, 0)]
    assert pagination._calc(5) == [(0, 5), (0, 3), (0, 1), (0, 0)]
    assert pagination._calc(0) == [(0, 5), (0, 3), (0, 1), (0, 0)]
