from .MusicNote import MusicNote
from typing import List


class GuitarString():
    """
    params:
    baseNote: Base note of the string. 弦的基音
    stringIndex: Index of the string, starting with the highest pitch as string 0. 弦的索引,以最高音为0弦开始计算
    """

    def __init__(self, baseNote: MusicNote, stringIndex: int):
        self._baseNote = baseNote
        self._stringIndex = stringIndex

    @property
    def getBaseNote(self) -> MusicNote:
        return self._baseNote

    @property
    def getStringIndex(self) -> int:
        return self._stringIndex

    def getFretByNote(self, note: int) -> int | bool:
        fret = note - self._baseNote.num
        if fret < 0 or fret > 23:
            return False
        return note - self._baseNote.num


def createGuitarStrings(notes: List[str]) -> List[GuitarString]:
    from src.utils.utils import getKeynoteByValue
    guitar_string_list = []
    for index in range(len(notes)):
        note = notes[index]
        # 第一弦是高音e弦
        guitar_string_list.append(GuitarString(
            MusicNote(getKeynoteByValue(note)), index))

    return guitar_string_list
