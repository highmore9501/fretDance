from typing import List, Dict
import itertools
import numpy as np

rightFingers = {
    "p": 0,
    "i": 1,
    "m": 2,
    "a": 3
}

handPositionToFingerPositions = {
    0: {"p": (1, 2), "i": (0, 1), "m": (0, 1), "a": (0, 1)},
    1: {"p": (2, 4), "i": (0, 2), "m": (0, 1), "a": (0, 1)},
    2: {"p": (3, 5), "i": (1, 3), "m": (0, 2), "a": (0, 2)},
    3: {"p": (4, 5), "i": (3, 5), "m": (2, 4), "a": (2, 4)}
}


class RightHand():
    def __init__(self, usedFingers: List[str], rightFingerPositions: List[int], isArpeggio: bool = False):
        self.usedFingers = usedFingers
        self.rightFingerPositions = rightFingerPositions
        # 手掌的位置由右手中指的位置来决定
        self.rightHandPosition = self.caculateHandPosition()
        self.isArpeggio = isArpeggio
        self.afterPlayed()

    def caculateHandPosition(self, rightFingerPositions=None) -> int:
        if rightFingerPositions == None:
            rightFingerPositions = self.rightFingerPositions

        results = [2, 1, 0, 3]
        for hand_position in results:
            for finger in ['p', 'i', 'm', 'a']:
                min_pos, max_pos = handPositionToFingerPositions[hand_position][finger]
                if not min_pos <= rightFingerPositions[rightFingers[finger]] <= max_pos:
                    break
            else:
                return hand_position
        return -1  # 返回-1表示没有找到满足条件的hand_position

    def validateRightHand(self, usedFingers=None, rightFingerPositions=None) -> bool:
        if rightFingerPositions == None:
            rightFingerPositions = self.rightFingerPositions
        if usedFingers == None:
            usedFingers = self.usedFingers

        usedString = []
        rightHandPosition = self.caculateHandPosition(rightFingerPositions)

        if rightHandPosition == -1:
            return False
        for finger in usedFingers:
            usedString.append(rightFingerPositions[rightFingers[finger]])
            # 检测是否有pima以外的手指
            if finger not in rightFingers:
                return False

        # 不能有重复的弦被拨动，除非是用P指
        if len(usedString) != len(set(usedString)):
            return False

        for i in range(3):
            # 检测手指的位置是否从左到右递减
            if rightFingerPositions[i] < rightFingerPositions[i+1]:
                return False

        return True

    def caculateDiff(self, otherRightHand: "RightHand") -> int:
        diff = 0
        # 计算手指改变所在弦位置的情况，每有移动一根弦距就加1单位的diff
        for i in range(4):
            diff += abs(self.rightFingerPositions[i] -
                        otherRightHand.rightFingerPositions[i])

        # 检测两只手的usedFingers相同的元素个数有多少
        common_elements = set(self.usedFingers).intersection(
            set(otherRightHand.usedFingers))
        same_finger_count = len(common_elements)

        # 检测重复使用的手指中有没有P指
        if 0 in common_elements:
            diff += 1
            same_finger_count -= 1

        # 其它重复使用的手指按3单位diff来算，也就是不鼓励除P指以外的手指重复使用
        diff += 3 * same_finger_count

        # 不考虑手掌移动，因为手掌是由身体来带动的，它的移动比手指移动要来得轻松
        return diff

    def afterPlayed(self):
        self.afterPlayedRightFingerPositions = self.rightFingerPositions.copy()

        # 根据ima手指的位置来调整手掌的位置
        if "i" in self.usedFingers:
            if "m" not in self.usedFingers and self.afterPlayedRightFingerPositions[2] < self.rightFingerPositions[1]-1:
                self.afterPlayedRightFingerPositions[2] = self.rightFingerPositions[1]-1
            if "a" not in self.usedFingers and self.afterPlayedRightFingerPositions[3] < self.rightFingerPositions[1]-2:
                self.afterPlayedRightFingerPositions[3] = self.rightFingerPositions[1]-2
            if "p" not in self.usedFingers and self.afterPlayedRightFingerPositions[0] > self.rightFingerPositions[1]+2:
                self.afterPlayedRightFingerPositions[0] = self.rightFingerPositions[1]+2
        elif "m" in self.usedFingers:
            if "a" not in self.usedFingers and self.afterPlayedRightFingerPositions[3] < self.rightFingerPositions[2]-1:
                self.afterPlayedRightFingerPositions[3] = self.rightFingerPositions[2]-1
            if "i" not in self.usedFingers and self.afterPlayedRightFingerPositions[1] > self.rightFingerPositions[2]+1:
                self.afterPlayedRightFingerPositions[1] = self.rightFingerPositions[2]+1
            if "p" not in self.usedFingers and self.afterPlayedRightFingerPositions[0] > self.  rightFingerPositions[2]+3:
                self.afterPlayedRightFingerPositions[0] = self.rightFingerPositions[2]+3
        elif "a" in self.usedFingers:
            if "i" not in self.usedFingers and self.afterPlayedRightFingerPositions[1] > self.rightFingerPositions[3]+2:
                self.afterPlayedRightFingerPositions[1] = self.rightFingerPositions[3]+2
            if "m" not in self.usedFingers and self.afterPlayedRightFingerPositions[2] > self.rightFingerPositions[3]+1:
                self.afterPlayedRightFingerPositions[2] = self.rightFingerPositions[3]+1
            if "p" not in self.usedFingers and self.afterPlayedRightFingerPositions[0] > self.rightFingerPositions[3]+4:
                self.afterPlayedRightFingerPositions[0] = self.rightFingerPositions[3]+4
        elif "p" in self.usedFingers:
            if "i" not in self.usedFingers and self.afterPlayedRightFingerPositions[1] < self.rightFingerPositions[0]-2:
                self.afterPlayedRightFingerPositions[1] = self.rightFingerPositions[0]-2
            if "m" not in self.usedFingers and self.afterPlayedRightFingerPositions[2] < self.rightFingerPositions[0]-3:
                self.afterPlayedRightFingerPositions[2] = self.rightFingerPositions[0]-3
            if "a" not in self.usedFingers and self.afterPlayedRightFingerPositions[3] < self.rightFingerPositions[0]-4:
                self.afterPlayedRightFingerPositions[3] = self.rightFingerPositions[0]-4

    def output(self):
        print("RightHand: ", self.usedFingers, self.rightFingerPositions)


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
    # 如果usedString内有重复元素
    if len(usedStrings) != len(set(usedStrings)):
        print(f"{usedStrings}内有重复元素")
    # usedStrings元素去重
    usedStrings = list(set(usedStrings))
    if len(usedStrings) > 4:
        usedFingers = []
        rightFingerPositions = [5, 3, 3, 2]
        newRightHand = RightHand(
            usedFingers, rightFingerPositions, isArpeggio=True)
        possibleRightHands.append(newRightHand)
    else:
        for result in finger_string_generator(allFingers, allstrings, usedStrings):
            result = process_p_fingers(result)
            if result == None:
                continue
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


# 这里把p指的重复演奏进行处理，只留下可能的情况，并只留一个p指数据
def process_p_fingers(result):
    p_fingers = [f for f in result if f['finger'] == 'p']
    strings = [f['string'] for f in p_fingers]
    if abs(strings[0] - strings[1]) != 1:
        return None
    min_string = min(strings)
    result.remove({'finger': 'p', 'string': min_string})
    return result


def get_usedFingers(finger_list: List[object], usedStrings: List[int]):
    return [item['finger'] for item in finger_list if item['string'] in usedStrings]


def caculateRightHandFingers(positions: list, usedRightFingers: list, rightHandPosition: int, isAfterPlayed: bool = False) -> Dict:
    from src.blender.blenderRecords import RIGHT_HAND_POSITIONS, RIGHT_HAND_DIRECTIONS, RIGHT_PIVOT_POSITIONS
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
