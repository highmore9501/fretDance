from typing import List, Dict, Tuple
from src.guitar.Guitar import Guitar
import itertools

KEYNOTES: dict = {
    "C": 48,
    "C#": 49,
    "D": 50,
    "D#": 51,
    "E": 52,
    "F": 53,
    "F#": 54,
    "G": 55,
    "G#": 56,
    "A": 45,
    "A#": 46,
    "B": 47
}


def getCurrentKeynotes(octave: int) -> dict:
    """
    according to the octave, return the current keynotes. 根据八度值返回一个当前的音符字典
    :param octave: 八度
    :return: a dict like KEYNOTES but with diffrent octave. 一个类似KEYNOTES的字典，但是八度不同
    """
    current_keynotes = {}
    for key, value in KEYNOTES.items():
        if octave == 0:
            newkey = key
        elif octave > 0:
            newkey = (key[0] + str(octave) + key[1:]).lower()
        else:
            newkey = key[0] + str(octave) + key[1:]
        current_keynotes[newkey] = value
    return current_keynotes


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


def convertNotesToChord(notes: List[int], guitar: Guitar) -> List[Dict[str, int]]:
    """
    convert notes to a list of possible positions on the guitar. 将音符转换为吉他上的可能位置列表
    :param notes: notes. 多个音符
    :param guitar: guitar. 吉他
    :return: a list of possible positions on the guitar. 一个吉他上的可能位置列表
    """
    notePositions = []
    result = []
    for note in notes:
        possiblePositions = []
        # 从低到高开始计算在每根弦上的位置
        for guitarString in guitar.guitarStrings:
            guitarStringIndex = guitarString._stringIndex
            fret = guitarString.getFretByNote(note)
            if fret is False:
                continue
            # 如果当前音符在当前弦上有位置，那么记录下来
            possiblePositions.append({
                "index": guitarStringIndex,
                "fret": fret
            })
        notePositions.append(possiblePositions)

    # 对notePositions里所有可能的位置进行组合，确保生成的每个组合都不存在index重复的情况
    combinations = itertools.product(*notePositions)
    for combination in combinations:
        # 如果combination里的元素的index有重复，就跳过
        if len(combination) != len(set([position["index"] for position in combination])):
            continue

        frets = list(filter(bool, [position["fret"]
                     for position in combination]))
        if frets:
            # 如果combination里元素的fret的个数大于4，就跳过，因为四个手指按不下
            if len(set(frets)) > 4:
                continue
            # 如果combination里元素的fret的最小非零值和最大非值的差值大于6，就跳过
            maxFret = max(frets)
            minFret = min(frets)
            outLimitOnLowBar = minFret < 8 and maxFret - minFret > 5
            outLimitOnHighBar = minFret >= 8 and maxFret - minFret > 6
            if outLimitOnLowBar or outLimitOnHighBar:
                continue
            result.append(combination)
        else:
            result.append(combination)

    return result


def convertChordToHands(chord: List[Tuple[Dict[str, int]]]) -> List[List[Dict[str, int]]]:
    """
    convert chord to a list of possible hands. 将和弦转换为可能的手型列表
    :param chord: chord. 和弦
    :return: a list of possible hands. 一个可能的手型列表
    """
    result = []
    fingerList = [1, 2, 3, 4]

    chordList = list(chord)
    for combination in generate_combinations_iter(chordList, fingerList):
        if verifyValidCombination(combination) and combination not in result:
            result.append(combination)

    return result


def generate_combinations_iter(noteList: List[Dict[str, int]], fingerList: List[int]):
    """
    a iterator to generate all possible combinations of notes and fingers. 生成所有可能的音符与手指组合的迭代器
    :param noteList: a list of notes. 音符列表
    :param fingerList: a list of fingers. 手指列表
    """
    if not noteList:
        yield []
        return

    if noteList[0]["fret"] != 0:
        for finger in fingerList:
            for combination in generate_combinations_iter(noteList[1:], fingerList):
                note = noteList[0].copy()
                note["finger"] = finger
                yield [note] + combination
    else:
        for combination in generate_combinations_iter(noteList[1:], fingerList):
            note = noteList[0].copy()
            yield [note] + combination


def verifyValidCombination(combination: List[Dict[str, int]]) -> bool:
    """
    verify if a combination is valid. 验证组合是否有效
    """
    # if finger is smaller and fret is bigger, return false. 如果finger值小的手指，而Fret值反而大，返回false。
    for i in range(len(combination) - 1):
        if "finger" in combination[i+1] and "finger" in combination[i] and combination[i]["finger"] > combination[i + 1]["finger"] and combination[i]["fret"] < combination[i + 1]["fret"]:
            return False

    # if the same finger has different fret, return false. 如果同一个finger值有对应不同的fret，返回false。
    fingerFretDict = {}
    for note in combination:
        if "finger" in note:
            if note["finger"] in fingerFretDict:
                if fingerFretDict[note["finger"]] != note["fret"]:
                    return False
            else:
                fingerFretDict[note["finger"]] = note["fret"]
    # if no above situation, return true. 以上情况都没有发生，返回true.
    return True


def stringIndexIsUsed(index: int, notePositions: List[dict]) -> bool:
    for position in notePositions:
        if position["index"] == index:
            return True
    return False


if __name__ == "__main__":
    result = [
        {'index': 4, 'fret': 3, 'finger': 1},
        {'index': 3, 'fret': 2, 'finger': 2},
        {'index': 2, 'fret': 0}
    ]

    print(verifyValidCombination(result))
