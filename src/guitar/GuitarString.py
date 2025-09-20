from .MusicNote import MusicNote, KEYNOTES
from typing import List, Any


class GuitarString():
    """
    params:
    baseNote: Base note of the string. 弦的基音
    stringIndex: Index of the string, starting with the highest pitch as string 0. 弦的索引,以最高音为0弦开始计算
    """

    def __init__(self, baseNote: MusicNote, stringIndex: int):
        self._baseNote: MusicNote = baseNote
        self._stringIndex = stringIndex

    def getBaseNote(self) -> int:
        return self._baseNote.num

    @property
    def getStringIndex(self) -> int:
        return self._stringIndex

    def getFretByNote(self, note: int) -> int | bool:
        fret = note - self._baseNote.num
        if fret < 0 or fret > 23:
            return False
        return fret


def createGuitarStrings(notes: List[str]) -> List[GuitarString]:
    guitar_string_list = []
    for index in range(len(notes)):
        note = notes[index]
        note_num = getKeynoteByValue(note)
        base_note = MusicNote(note_num)
        # 第一弦是高音e弦
        guitar_string_list.append(GuitarString(base_note, index))

    return guitar_string_list


def getKeynoteByValue(value: str) -> Any:
    """
    transform the note to an integer value, C is 48. 将音符转换为一个整数值，C为48
    :param value: keynote such as `C`, `F1`
    :return: an integer value. 一个整数值
    """
    # 如果value在KEYNOTES中，直接返回
    if value in KEYNOTES:
        return KEYNOTES[value]
    # 如果value是单个小写字母，表示为高音
    elif value.upper() in KEYNOTES and value.islower() and len(value) == 1:
        return KEYNOTES[value.upper()] + 12
    # 如果value长度大于1，并且最后一个值是一个数字
    elif len(value) > 1 and value[-1].isdigit():
        # 提取音符部分和数字部分
        note_part = value[:-1]
        octave = int(value[-1])

        # 处理带#号的音符+数字（如C#1, c#1）
        if "#" in note_part and note_part.replace("#", "").upper() in KEYNOTES:
            base_note = note_part.replace("#", "").upper()
            # 判断是高音还是低音
            if note_part[0].islower():
                # 小写表示高音
                return KEYNOTES[base_note] + 12 * octave + 1
            else:
                # 大写表示低音
                return KEYNOTES[base_note] - 12 * octave + 1
        # 处理普通音符+数字（如C1, c1）
        elif note_part.upper() in KEYNOTES:
            base_note = note_part.upper()
            # 判断是高音还是低音
            if note_part[0].islower():
                # 小写表示高音
                return KEYNOTES[base_note] + 12 * octave
            else:
                # 大写表示低音
                return KEYNOTES[base_note] - 12 * octave
        else:
            # 音符部分无效
            print("音符格式有误：", value)
            return False
    # 处理带#号的音符（不带数字）
    elif "#" in value and value.replace("#", "").upper() in KEYNOTES:
        base_note = value.replace("#", "").upper()
        return KEYNOTES[base_note] + 1
    # 处理不带数字的大写音符
    elif value.isupper() and value in KEYNOTES:
        return KEYNOTES[value]
    else:
        print("音符格式有误：", value)
        return False
