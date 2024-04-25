import copy
from typing import List, Dict, Tuple
from ..guitar.Guitar import Guitar
from numpy import array
import numpy as np
from .fretDistanceDict import FRET_DISTANCE_DICT
from ..blender.blenderRecords import RIGHT_HAND_POSITIONS, RIGHT_HAND_DIRECTIONS, LEFT_FINGER_POSITIONS, OUTER_LEFT_HAND_POSITIONS, NORMAL_LEFT_HAND_ROTATIONS, INNER_LEFT_HAND_POSITIONS, NORMAL_LEFT_HAND_POSITIONS, OUTER_LEFT_HAND_ROTATIONS, INNER_LEFT_HAND_ROTATIONS, RIGHT_PIVOT_POSITIONS
import itertools
from ..hand.RightHand import RightHand
from ..hand.LeftHand import LeftHand

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
            # 低音弦的超高把位是无法按的
            if guitarStringIndex > 2 and fret > 12:
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


def stringIndexIsUsed(index: int, notePositions: List[dict]) -> bool:
    for position in notePositions:
        if position["index"] == index:
            return True
    return False


def print_strikethrough(text):
    return f"\033[9m{text}\033[0m"


def twiceLerpFingers(fret: int, stringIndex: int) -> Dict:
    p0 = array(LEFT_FINGER_POSITIONS["P0"])
    p1 = array(LEFT_FINGER_POSITIONS["P1"])
    p2 = array(LEFT_FINGER_POSITIONS["P2"])
    p3 = array(LEFT_FINGER_POSITIONS["P3"])

    fret_query_string = "0-"+str(fret)
    fret_value = FRET_DISTANCE_DICT[fret_query_string]

    p0_fret = FRET_DISTANCE_DICT["0-1"]
    p2_fret = FRET_DISTANCE_DICT["0-12"]
    fret_value = (fret_value - p0_fret) / (p2_fret - p0_fret)

    p_fret_0 = p0 + (p2 - p0) * fret_value
    p_fret_1 = p1 + (p3 - p1) * fret_value

    p_final = p_fret_0 + (p_fret_1 - p_fret_0) * stringIndex / 5

    return p_final


def twiceLerp(hand_state: str, value: str, valueType: str, fret: int, stringIndex: int | float) -> array:
    DATA_DICT = None
    if valueType == 'position':
        if hand_state == "OUTER":
            DATA_DICT = OUTER_LEFT_HAND_POSITIONS
        elif hand_state == "INNER":
            DATA_DICT = INNER_LEFT_HAND_POSITIONS
        else:
            DATA_DICT = NORMAL_LEFT_HAND_POSITIONS
    if valueType == 'rotation':
        if hand_state == "OUTER":
            DATA_DICT = OUTER_LEFT_HAND_ROTATIONS
        elif hand_state == "INNER":
            DATA_DICT = INNER_LEFT_HAND_ROTATIONS
        else:
            DATA_DICT = NORMAL_LEFT_HAND_ROTATIONS

    # p0和p1实际上并不是空品，而是1品;而p2和p3是12品
    p0 = array(DATA_DICT["P0"][value])
    p1 = array(DATA_DICT["P1"][value])
    p2 = array(DATA_DICT["P2"][value])
    p3 = array(DATA_DICT["P3"][value])

    fret_query_string = "0-"+str(fret)
    fret_value = FRET_DISTANCE_DICT[fret_query_string]

    p0_fret = FRET_DISTANCE_DICT["0-1"]
    p2_fret = FRET_DISTANCE_DICT["0-12"]
    fret_value = (fret_value - p0_fret) / (p2_fret - p0_fret)

    p_fret_0 = p0 + (p2 - p0) * fret_value
    p_fret_1 = p1 + (p3 - p1) * fret_value
    p_final = p_fret_0 + (p_fret_1 - p_fret_0) * stringIndex / 5

    return p_final


def caculateRightHandFingers(positions: list, usedRightFingers: list, rightHandPosition: int, isAfterPlayed: bool = False) -> Dict:
    fingerMoveDistanceWhilePlay = 0.0045
    result = {}

    isArpeggio = usedRightFingers == [] and isAfterPlayed

    hand_index = "h_end" if isArpeggio else f"h{rightHandPosition}"
    H_R = RIGHT_HAND_POSITIONS[hand_index]['position'].copy()
    # 来一个随机大小为0.0005的随机移动
    random_move = np.random.rand(3) * 0.001
    H_R[0] += random_move[0]
    H_R[1] += random_move[1]
    H_R[2] += random_move[2]
    result['H_R'] = H_R

    t_index = "p_end" if isArpeggio else f"p{positions[0]}"
    T_R = RIGHT_HAND_POSITIONS[t_index]['position'].copy()
    if isAfterPlayed and "p" in usedRightFingers:
        move = RIGHT_HAND_DIRECTIONS[f"T_line"]['direction']
        T_R[0] += move[0] * fingerMoveDistanceWhilePlay
        T_R[1] += move[1] * fingerMoveDistanceWhilePlay
        T_R[2] += move[2] * fingerMoveDistanceWhilePlay
    result['T_R'] = T_R

    i_index = "i_end" if isArpeggio else f"i{positions[1]}"
    I_R = RIGHT_HAND_POSITIONS[i_index]['position'].copy()
    if isAfterPlayed and "i" in usedRightFingers:
        move = RIGHT_HAND_DIRECTIONS[f"I_line"]['direction']
        I_R[0] += move[0] * fingerMoveDistanceWhilePlay
        I_R[1] += move[1] * fingerMoveDistanceWhilePlay
        I_R[2] += move[2] * fingerMoveDistanceWhilePlay
    result['I_R'] = I_R

    m_index = "m_end" if isArpeggio else f"m{positions[2]}"
    M_R = RIGHT_HAND_POSITIONS[m_index]['position'].copy()
    if isAfterPlayed and "m" in usedRightFingers:
        move = RIGHT_HAND_DIRECTIONS[f"M_line"]['direction']
        M_R[0] += move[0] * fingerMoveDistanceWhilePlay
        M_R[1] += move[1] * fingerMoveDistanceWhilePlay
        M_R[2] += move[2] * fingerMoveDistanceWhilePlay
    result['M_R'] = M_R

    r_index = "a_end" if isArpeggio else f"a{positions[3]}"
    R_R = RIGHT_HAND_POSITIONS[r_index]['position'].copy()
    if isAfterPlayed and "a" in usedRightFingers:
        move = RIGHT_HAND_DIRECTIONS[f"P_line"]['direction']
        R_R[0] += move[0] * fingerMoveDistanceWhilePlay
        R_R[1] += move[1] * fingerMoveDistanceWhilePlay
        R_R[2] += move[2] * fingerMoveDistanceWhilePlay
    result['R_R'] = R_R

    p_index = "ch_end" if isArpeggio else f"ch{positions[3]}"
    P_R = RIGHT_HAND_POSITIONS[p_index]['position']
    result['P_R'] = P_R

    result['TP_R'] = RIGHT_PIVOT_POSITIONS['TP_R']['position']
    result['HP_R'] = RIGHT_PIVOT_POSITIONS['HP_R']['position']

    return result


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


def finger_string_generator(allFingers: List[str], allStrings: List[int], usedStrings: List[int]):
    if usedStrings == []:
        for result in finger_string_generator2(allFingers, allStrings):
            yield result

    for finger, usedString in itertools.product(allFingers, usedStrings):
        newStrings = usedStrings.copy()
        newStrings.remove(usedString)
        newAllStrings = allStrings.copy()
        newAllStrings.remove(usedString)
        newAllFingers = allFingers.copy()
        newAllFingers.remove(finger)
        for result in finger_string_generator(newAllFingers, newAllStrings, newStrings):
            yield [{
                "finger": finger,
                "string": usedString
            }] + result


def finger_string_generator2(allFingers: List[str], allStrings: List[int]):
    if allFingers == []:
        yield []
        return

    for finger, string in itertools.product(allFingers, allStrings):
        newAllStrings = allStrings.copy()
        newAllStrings.remove(string)
        newAllFingers = allFingers.copy()
        newAllFingers.remove(finger)
        for result in finger_string_generator2(newAllFingers, newAllStrings):
            yield [{
                "finger": finger,
                "string": string
            }] + result


def generatePossibleRightHands(
        usedStrings: List[int], allFingers: List[str], allstrings: List[int]):
    possibleRightHands = []
    if len(usedStrings) > 3:
        usedFingers = []
        rightFingerPositions = [5, 3, 3, 2]
        newRightHand = RightHand(
            usedFingers, rightFingerPositions, isArpeggio=True)
        possibleRightHands.append(newRightHand)
    else:
        for result in finger_string_generator(allFingers, allstrings, usedStrings):
            rightFingerPositions = sort_fingers(result)
            usedFingers = get_usedFingers(result, usedStrings)
            newRightHand = RightHand(
                usedFingers, rightFingerPositions)
            if newRightHand.validateRightHand():
                possibleRightHands.append(newRightHand)

    return possibleRightHands


def sort_fingers(finger_list: List[object]):
    order = {'p': 0, 'i': 1, 'm': 2, 'a': 3}
    sorted_list = sorted(finger_list, key=lambda x: order[x['finger']])
    return [item['string'] for item in sorted_list]


def get_usedFingers(finger_list: List[object], usedStrings: List[int]):
    return [item['finger'] for item in finger_list if item['string'] in usedStrings]
