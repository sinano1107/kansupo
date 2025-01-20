from abc import ABCMeta, abstractmethod
from playwright.sync_api import Locator


class Command(metaclass=ABCMeta):
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def run(self, canvas: Locator):
        pass