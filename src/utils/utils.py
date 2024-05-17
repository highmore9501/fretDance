from typing import List, Dict, Tuple
from ..guitar.Guitar import Guitar
import numpy as np
import itertools


def convertNotesToChord(notes: List[int], guitar: Guitar) -> List[Dict[str, int]]:
    """
    convert notes to a list of possible positions on the guitar. 将音符转换为吉他上的可能位置列表
    :param notes: notes. 多个音符
    :param guitar: guitar. 吉他
    :return: a list of possible positions on the guitar. 一个吉他上的可能位置列表
    """
    all_harm_notes = guitar.harm_notes
    notePositions = []
    result = []

    for note in notes:
        possiblePositions = []
        # 从低到高开始计算在每根弦上的位置
        for guitarString in guitar.guitarStrings:
            guitarStringIndex = guitarString._stringIndex
            harm_notes = list(
                filter(lambda x: x["index"] == guitarStringIndex, all_harm_notes))
            harm_frets = [harm_note["fret"]
                          for harm_note in harm_notes if harm_note["note"] == note]
            normal_fret = guitarString.getFretByNote(note)
            has_normal_fret = normal_fret is not False
            if len(harm_frets) == 0 and not has_normal_fret:
                continue
            # 低音弦的超高把位是无法按的
            if guitarStringIndex > 2 and normal_fret > 16 and not has_normal_fret:
                continue
            # 如果当前音符在当前弦上有位置，那么记录下来
            if len(harm_frets) > 0:
                for fret in harm_frets:
                    possiblePositions.append({
                        "index": guitarStringIndex,
                        "fret": fret
                    })
            if has_normal_fret:
                possiblePositions.append({
                    "index": guitarStringIndex,
                    "fret": normal_fret
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


def convertChordTofingerPositions(chord: List[Tuple[Dict[str, int]]]) -> List[List[Dict[str, int]]]:
    """
    convert chord to a list of possible hands. 将和弦转换为可能的手型列表
    :param chord: chord. 和弦
    :return: a list of possible hands. 一个可能的手型列表
    """
    result = []
    fingerList = [1, 2, 3, 4]

    for combination in generate_combinations_iter(chord, fingerList):
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
    # 去掉combination里不包含手指的元素
    combination = list(filter(lambda x: "finger" in x, combination))

    if len(combination) < 2:
        return True

    # 将combinations按照finger排序
    combination = sorted(combination, key=lambda x: x["finger"])

    # if finger is smaller and fret is bigger, return false. 如果finger值小的手指，而Fret值反而大，返回false。
    for i in range(len(combination) - 1):
        if "finger" in combination[i+1] and "finger" in combination[i] and combination[i]["finger"] > combination[i + 1]["finger"] and combination[i]["fret"] < combination[i + 1]["fret"]:
            return False
        if "finger" in combination[i+1] and "finger" in combination[i] and combination[i]["finger"] < combination[i + 1]["finger"] and combination[i]["fret"] > combination[i + 1]["fret"]:
            return False
        # 如果出现非食指的跨弦横按，返回false
        if "finger" in combination[i+1] and "finger" in combination[i] and combination[i]["finger"] == combination[i + 1]["finger"] and combination[i]["fret"] == combination[i + 1]["fret"]:
            if combination[i]["finger"] != 1 and abs(combination[i]["index"]-combination[i+1]["index"]) > 1:
                return False

    # 将List转化成对象
    fingerFretDict = {}
    for note in combination:
        if note["finger"] in fingerFretDict:
            # 如果同一个手指按了不同的品，返回false
            if fingerFretDict[note["finger"]]["fret"] != note["fret"]:
                return False
            else:
                fingerFretDict[note["finger"]] = {
                    "fret": note["fret"],
                    "string": note["index"]
                }

    # 如果中指和无名指都在按弦而且两者相差大于1，返回false
    if "2" in fingerFretDict and "3" in fingerFretDict and fingerFretDict["3"]["fret"]-1 > fingerFretDict["2"]["fret"]:
        return False
    # 如果食指和中指都在按弦而且两者相差大于1，返回false
    if "1" in fingerFretDict and "2" in fingerFretDict and fingerFretDict["2"]["fret"]-1 > fingerFretDict["1"]["fret"]:
        return False
    # 如果食指和无名指都在按弦而且两者相差大于1，返回false
    if "3" in fingerFretDict and "4" in fingerFretDict and fingerFretDict["4"]["fret"]-1 > fingerFretDict["3"]["fret"] and abs(fingerFretDict["4"]["string"]-fingerFretDict["3"]["string"]) > 1:
        return False

    # if no above situation, return true. 以上情况都没有发生，返回true.
    return True


def rotate_vector(euler_angles: list):
    vector = np.array([1, 0, 0])
    # 旋转值已经是弧度，无需转换
    a = euler_angles[0]
    b = euler_angles[1]
    c = euler_angles[2]

    # 创建旋转矩阵
    Rx = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)],
                   [0, np.sin(a), np.cos(a)]])
    Ry = np.array([[np.cos(b), 0, np.sin(b)], [
        0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    Rz = np.array([[np.cos(c), -np.sin(c), 0],
                   [np.sin(c), np.cos(c), 0], [0, 0, 1]])

    # 修改旋转矩阵的计算顺序
    R = np.dot(Rx, np.dot(Ry, Rz))

    # 将旋转矩阵应用到向量上
    rotated_vector = np.dot(R, vector)

    return rotated_vector


def get_position_by_fret(fret: float, value_1: np.array, value_12: np.array) -> np.array:
    base_ratio = 2**(1/12)
    value_0 = (2 * value_12 - base_ratio *
               (2 * value_12 - value_1)) / (2 - base_ratio)

    return fret_position(value_0, value_12, fret)


def fret_position(string_start, string_middle, fret_number):
    string_end = 2 * string_middle - string_start
    end_to_start = string_end - string_start

    end_to_fret = end_to_start * 0.5**(fret_number/12)
    fret_position = string_end - end_to_fret
    return fret_position
