from .GuitarString import GuitarString
from typing import List


class Guitar():
    """
    params:
    guitarStrings: List of guitar strings. 吉他弦列表
    stringDistance: String spacing. 弦间距
    fullString: Length of string. 整根弦的长度
    """

    def __init__(self, guitarStrings: List[GuitarString], stringDistance: float = 0.85, fullString: float = 64.7954):
        self._ETC = 1.0594630943592956
        self._stringDistance = stringDistance
        self._fullString = fullString
        self.guitarStrings = guitarStrings

    @property
    def getETC(self) -> float:
        return self._ETC

    @property
    def getStringDistance(self) -> float:
        return self._stringDistance

    @property
    def getFullString(self) -> float:
        return self._fullString
