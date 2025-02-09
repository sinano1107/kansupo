import json
from utils.calc_page_select_process import calc_page_select_process
from utils.context import PortResponse, ResponseMemory


def test_calc_page_select_process():
    with open(
        "test_resources/calc_page_select_process/2025-02-07 12:34:16.637291_api_port-port.json"
    ) as f:
        data = json.load(f).get("api_data")
        ResponseMemory.port = PortResponse.from_dict(data)
    assert calc_page_select_process(1, 1, 10) == []
    assert calc_page_select_process(1, 2, 10) == [2]
    assert calc_page_select_process(1, 3, 10) == [3]
    assert calc_page_select_process(1, 4, 10) == [4]
    assert calc_page_select_process(1, 5, 10) == [5]
    assert calc_page_select_process(1, 6, 10) == [5, 4]
    assert calc_page_select_process(1, 7, 10) == [5, 5]
    assert calc_page_select_process(1, 8, 10) == [5, 5, 4]
    assert calc_page_select_process(1, 9, 10) == [5, 5, 5]
    assert calc_page_select_process(1, 10, 10) == [5, 5, 5, 5]

    assert calc_page_select_process(10, 9, 10) == [4]
    assert calc_page_select_process(10, 8, 10) == [3]
    assert calc_page_select_process(10, 7, 10) == [2]
    assert calc_page_select_process(10, 6, 10) == [1]
    assert calc_page_select_process(10, 5, 10) == [1, 2]
    assert calc_page_select_process(10, 4, 10) == [1, 1]
    assert calc_page_select_process(10, 3, 10) == [1, 1, 2]
    assert calc_page_select_process(10, 2, 10) == [1, 1, 1]
    assert calc_page_select_process(10, 1, 10) == [1, 1, 1, 1]

    assert calc_page_select_process(4, 5, 10) == [4]

    assert calc_page_select_process(1, 1, 5) == []
    assert calc_page_select_process(1, 2, 5) == [2]
    assert calc_page_select_process(1, 3, 5) == [3]
    assert calc_page_select_process(1, 4, 5) == [4]
    assert calc_page_select_process(1, 5, 5) == [5]

    assert calc_page_select_process(5, 5, 5) == []
    assert calc_page_select_process(5, 4, 5) == [4]
    assert calc_page_select_process(5, 3, 5) == [3]
    assert calc_page_select_process(5, 2, 5) == [2]
    assert calc_page_select_process(5, 1, 5) == [1]
