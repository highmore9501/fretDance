from src.guitar.GuitarString import GuitarString
from src.guitar.GuitarNote import GuitarNote
from src.guitar.Guitar import Guitar
from typing import List
import math

PRESSSTATE: dict = {
    "Open": 0,
    "Pressed": 1,
    "Barre": 2,
    "Partial_barre_2_strings": 3,
    "Partial_barre_3_strings": 4
}

FINGERS: dict = {
    "Empty": -1,
    "Thumb": 0,
    "Index": 1,
    "Middle": 2,
    "Ring": 3,
    "Pinky": 4
}


class LeftFinger:
    """
    params:
    fingerIndex: Index of the finger. 手指的索引
    guitarString: The string that the finger is placing. 手指当前所在的弦
    fret: Fret number. 品数
    press: Press state. 按弦状态
    """

    def __init__(self, fingerIndex: int, guitarString: GuitarString, fret: int = 1, press: str = "Open"):

        self._fingerIndex = fingerIndex
        # fingerName等于FINGERS中值为fingerIndex的key值
        self._fingerName = list(FINGERS.keys())[list(
            FINGERS.values()).index(fingerIndex)]
        self.guitarString = guitarString
        self.fret = fret
        self.press = PRESSSTATE[press]

    @property
    def getFingerName(self) -> str:
        return self._fingerName

    @property
    def getFingerIndex(self) -> int:
        return self._fingerIndex

    def output(self) -> None:
        print(self._fingerName, "|",
              self.guitarString._stringIndex, "string | ", self.fret, "fret |  ", list(PRESSSTATE.keys())[list(
                  PRESSSTATE.values()).index(self.press)])

    def getTouchedPoint(self, guitarStrings: List[GuitarString]) -> List[GuitarNote]:
        """
        计算此手指此时的按弦点
        :return: GuitarNote列表。
        """
        currentGuitarNotes = []

        if self.press == PRESSSTATE["Pressed"]:
            currentGuitarNotes.append(GuitarNote(guitarString, self.fret))
        elif self.press == PRESSSTATE["Barre"]:
            for guitarString in guitarStrings:
                currentGuitarNotes.append(GuitarNote(guitarString, self.fret))
        elif self.press == PRESSSTATE["Partial_barre_2_strings"]:
            for guitarString in guitarStrings:
                if guitarString.stringIndex > 1:
                    continue
                currentGuitarNotes.append(GuitarNote(guitarString, self.fret))
        elif self.press == PRESSSTATE["Partial_barre_3_strings"]:
            for guitarString in guitarStrings:
                if guitarString.stringIndex > 2:
                    continue
                currentGuitarNotes.append(GuitarNote(guitarString, self.fret))

        return currentGuitarNotes

    def distanceTo(self, guitar: Guitar, targetFinger: 'LeftFinger') -> float:
        """
        :param targetFinger: 目标手指
        :return: entropy. 熵值大小
        """
        fingerStringDistance = 0
        fingerFretDistance = 0
        etc = guitar._ETC

        if self.guitarString._stringIndex != targetFinger.guitarString._stringIndex:
            fingerStringDistance += abs(
                self.guitarString._stringIndex - targetFinger.guitarString._stringIndex) * guitar._stringDistance
        if self.fret != targetFinger.fret:
            fingerFretDistance += abs(guitar._fullString / pow(etc, self.fret) -
                                      guitar._fullString / pow(etc, targetFinger.fret))

        distance = math.sqrt(
            math.pow(fingerStringDistance, 2) + math.pow(fingerFretDistance, 2))

        return distance

    def fretDistanceTo(self, guitar: Guitar, targetFinger: 'LeftFinger') -> float:
        """
        :params targetFinger: 目标手指
        :return: entropy. 熵
        """
        fingerFretDistance = 0
        if self.fret != targetFinger.fret:
            fingerFretDistance += abs(guitar._fullString / pow(self.guitar._ETC, self.fret) -
                                      guitar._fullString / pow(self.guitar._ETC, targetFinger.fret))
        return fingerFretDistance
