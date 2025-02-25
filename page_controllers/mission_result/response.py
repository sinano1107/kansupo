from dataclasses import dataclass, field
from enum import IntEnum

from dataclasses_json import config, dataclass_json


class ClearResult(IntEnum):
    """クリア結果を表す列挙型"""

    # 失敗
    FAILED = 0
    # 成功
    SUCCESS = 1
    # 大成功
    GREAT_SUCCESS = 2

    def __str__(self):
        if self == ClearResult.FAILED:
            return "失敗"
        if self == ClearResult.SUCCESS:
            return "成功"
        if self == ClearResult.GREAT_SUCCESS:
            return "大成功"
        raise ValueError(f"不明なclear_result {self}")


@dataclass_json
@dataclass(frozen=True)
class MissionResultResponse:
    clear_result: ClearResult = field(metadata=config(field_name="api_clear_result"))
