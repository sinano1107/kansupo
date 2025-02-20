from dataclasses import dataclass, field
from enum import IntEnum
from dataclasses_json import config, dataclass_json


class MissionState(IntEnum):
    """任務の状態を表す列挙型"""

    # 未出撃
    NOT_STARTED = 0
    # 遠征中
    IN_PROGRESS = 1
    # 遠征帰投
    COMPLETED = 2
    # 強制帰投中
    FORCED_RETURN = 3


@dataclass_json
@dataclass(frozen=True)
class Deck:
    mission: list[int] = field(metadata=config(field_name="api_mission"))

    @property
    def mission_state(self) -> MissionState:
        return self.mission[0]


@dataclass_json
@dataclass(frozen=True)
class PortResponse:
    deck_list: list[Deck] = field(metadata=config(field_name="api_deck_port"))
