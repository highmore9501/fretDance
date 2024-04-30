from .MusicNote import MusicNote, KEYNOTES
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
    guitar_string_list = []
    for index in range(len(notes)):
        note = notes[index]
        # 第一弦是高音e弦
        guitar_string_list.append(GuitarString(
            MusicNote(getKeynoteByValue(note)), index))

    return guitar_string_list


def getKeynoteByValue(value: str) -> int | bool:
    """
    transform the note to an integer value, C is 48. 将音符转换为一个整数值，C为48
    :param value: keynote such as `C`, `d`, `F1`. 音符，例如`C`, `d`, `F1`
    :return: an integer value. 一个整数值
    """
    # 如果value在KEYNOTES中，直接返回.如果是value的大写在KEYNOTES中，说明当前值是高音，需要返回+12
    if value in KEYNOTES:
        return KEYNOTES[value]
    elif value.upper() in KEYNOTES:
        return KEYNOTES[value.upper()] + 12
    # 如果value长度为2，并且最后一个值是一个数字
    elif len(value) > 1 and value[1:].isdigit():
        # 如果第一个值在KEYNOTES中，说明当前值是低音，返回-12*value[1]
        if value[0] in KEYNOTES:
            return KEYNOTES[value[0]] - 12 * int(value[1:])
        elif value[0].upper() in KEYNOTES:
            return KEYNOTES[value[0].upper()] + 12 * int(value[1:])
    elif len(value) > 1 and value[1:-1].isdigit() and value[-1] == "#":
        # 如果第一个值在KEYNOTES中，说明当前值是低音，返回-12*value[1]
        if value[0] in KEYNOTES:
            return KEYNOTES[value[0]] - 12 * int(value[1:]) + 1
        elif value[0].upper() in KEYNOTES:
            return KEYNOTES[value[0].upper()] + 12 * int(value[1:]) + 1
    else:
        print("音符格式有误：", value)
        return False
