from abc import ABCMeta, abstractmethod
from typing import Self
from playwright.sync_api import Locator


class Command(metaclass=ABCMeta):
    @staticmethod
    def instantiate(args: list[str]) -> Self:
        raise Exception("instantiateメソッドがオーバーライドされていない")
    
    @abstractmethod
    def run(self, canvas: Locator):
        raise Exception("runメソッドがオーバーライドされていない")