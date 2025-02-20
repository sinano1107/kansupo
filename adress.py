from enum import Enum

API_ROOT = "http://w14h.kancolle-server.com/kcsapi/"


class Address(Enum):
    OPTION_SETTING = API_ROOT + "api_start2/get_option_setting"
    PORT = API_ROOT + "api_port/port"
