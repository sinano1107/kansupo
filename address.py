from enum import Enum

API_ROOT = "http://w14h.kancolle-server.com/kcsapi/"


class Address(Enum):
    GET_DATA = API_ROOT + "api_start2/getData"
    OPTION_SETTING = API_ROOT + "api_start2/get_option_setting"
    PORT = API_ROOT + "api_port/port"
    MISSION_RESULT = API_ROOT + "api_req_mission/result"
