from typing import List, Dict
import itertools
from numpy import array, random
import json

rightFingers = {
    "p": 0,
    "i": 1,
    "m": 2,
    "a": 3
}

# 右手在吉它上摆放有四个位置，在这四个位置上，每个手指可以接触到的弦的范围如下表所示，其中2就是常规的起始手型
handPositionToFingerPositions = {
    0: {"p": (1, 2), "i": (0, 1), "m": (0, 1), "a": (0, 1)},
    1: {"p": (2, 4), "i": (0, 2), "m": (0, 2), "a": (0, 2)},
    2: {"p": (3, 5), "i": (1, 3), "m": (0, 2), "a": (0, 2)},
    3: {"p": (4, 5), "i": (3, 5), "m": (2, 4), "a": (2, 4)}
}


class RightHand():
    def __init__(self, usedFingers: List[str], rightFingerPositions: List[int], isArpeggio: bool = False):
        self.usedFingers = usedFingers
        self.rightFingerPositions = rightFingerPositions
        self.isArpeggio = isArpeggio

    def validateRightHand(self, usedFingers=None, rightFingerPositions=None) -> bool:

        if rightFingerPositions == None:
            rightFingerPositions = self.rightFingerPositions
        if usedFingers == None:
            usedFingers = self.usedFingers

        return validateRightHandByFingerPositions(usedFingers, rightFingerPositions, False)

    def caculateDiff(self, otherRightHand: "RightHand") -> int:
        # 重复使用同一根手指的惩罚机制
        repeat_punish = 5
        diff = 0
        # 计算手指改变所在弦位置的情况，每有移动一根弦距就加1单位的diff
        for i in range(4):
            diff += abs(self.rightFingerPositions[i] -
                        otherRightHand.rightFingerPositions[i])

        # 检测两只手的usedFingers相同的元素个数有多少
        common_elements = list(set(self.usedFingers).intersection(
            set(otherRightHand.usedFingers)))
        same_finger_count = len(common_elements)

        # 检测重复使用的手指中有没有P指，如果有的话按加repeat_punish来计算重复指惩罚
        if 'p' in common_elements:
            diff += repeat_punish
            same_finger_count -= 1

        # 其它重复使用的手指按双倍repeat_punish来算，也就是非常不鼓励除P指以外的手指重复使用
        diff += 2 * repeat_punish * same_finger_count

        # 不考虑手掌移动，因为手掌是由身体来带动的，它的移动比手指移动要来得轻松
        return diff

    def output(self):
        print("RightHand: ", self.usedFingers, self.rightFingerPositions)


def validateRightHandByFingerPositions(usedFingers, rightFingerPositions: List[int], repeated_fingers_checked: bool) -> bool:
    for i in range(len(rightFingerPositions) - 1):
        # 检测手指的位置是否从左到右递减，如果手指分布不符合科学，判断为错误
        if rightFingerPositions[i] < rightFingerPositions[i+1]:
            return False

    # 如果没有p指，而且其它手指已经预检测掉了重复和可能性，那么就直接返回True
    if 'p' not in usedFingers and repeated_fingers_checked:
        return True

    usedString = []
    used_p_strings = []
    for finger in usedFingers:
        current_string = rightFingerPositions[rightFingers[finger]]
        if finger == 'p':
            used_p_strings.append(current_string)
        elif not repeated_fingers_checked:
            # 如果没有预检测过其它手指是否重复触弦，通过下面的方式来检测
            if current_string not in usedString:
                usedString.append(current_string)
            else:
                return False

    # 如果p指只有1根弦或者没有触弦，那么就直接返回True
    if len(used_p_strings) < 2:
        return True

    # 如果p指触的两根弦并不相邻，那么就直接返回False
    if abs(used_p_strings[0] - used_p_strings[1]) > 1:
        return False

    # 如果p指双拨的弦最高超过了3，那么就直接返回False
    if min(used_p_strings) < 3:
        return False

    return True


def finger_string_map_generator(allFingers: List[str], touchedStrings: List[int], unusedFingers: List[str], allStrings: List[int]):
    if touchedStrings == []:
        for result in finger_string_map_generator2(unusedFingers, allStrings):
            yield result

    if allFingers == []:
        yield []
        return

    for usedFinger, touchedString in itertools.product(allFingers, touchedStrings):
        # next_allFinger是所有序号高于usedFingers的手指的列表
        usedFinger_index = allFingers.index(usedFinger)
        next_allFingers = allFingers[usedFinger_index + 1:]

        next_touchedStrings = touchedStrings[:]
        next_touchedStrings.remove(touchedString)

        next_unusedFingers = unusedFingers[:]
        next_unusedFingers.remove(usedFinger)
        next_unusedStrings = allStrings[:]
        next_unusedStrings.remove(touchedString)
        for result in finger_string_map_generator(next_allFingers, next_touchedStrings, next_unusedFingers, next_unusedStrings):
            yield [{
                "finger": usedFinger,
                "string": touchedString
            }] + result


def finger_string_map_generator2(unusedFingers: List[str], allStrings: List[int]):
    if unusedFingers == [] or allStrings == []:
        yield []
        return

    # 这里每次配对以后，不再移除已经配对的弦，因为不演奏的手指可以放在同一根弦上
    for finger, string in itertools.product(unusedFingers, allStrings):
        newAllFingers = unusedFingers[:]
        newAllFingers.remove(finger)
        for result in finger_string_map_generator2(newAllFingers, allStrings):
            yield [{
                "finger": finger,
                "string": string
            }] + result


def generatePossibleRightHands(
        touchedStrings: List[int], allFingers: List[str], allStrings: List[int]):
    possibleRightHands = []

    if len(touchedStrings) > 4:
        usedFingers = []
        rightFingerPositions = [5, 3, 3, 2]
        newRightHand = RightHand(
            usedFingers, rightFingerPositions, isArpeggio=True)
        possibleRightHands.append(newRightHand)
    else:
        unused_fingers = allFingers[:]
        for result in finger_string_map_generator(allFingers, touchedStrings, unused_fingers, allStrings):
            # 输出的结果必须是每个手指都有对应的位置，否则说明配对不合法
            if result == None or len(result) < len(allFingers):
                continue
            rightFingerPositions = sort_fingers(result)
            usedFingers = get_usedFingers(result, touchedStrings)
            # result到这里是可能存在p指重复的，需要在下面的方法里进行检测看重复是否合理
            if validateRightHandByFingerPositions(usedFingers, rightFingerPositions, repeated_fingers_checked=True):
                newRightHand = RightHand(
                    usedFingers, rightFingerPositions)
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


def caculateRightHandFingers(avatar: str, positions: list, usedRightFingers: list, isAfterPlayed: bool = False) -> Dict:
    json_file = f'asset\controller_infos\{avatar}.json'
    with open(json_file, 'r') as f:
        data = json.load(f)
    fingerMoveDistanceWhilePlay = 0.006
    result = {}

    isArpeggio = usedRightFingers == [] and isAfterPlayed

    # 目前HP_R和TP_R两个值假定它们是全程固定的，所以暂时没有测量它们

    if isArpeggio:
        if isAfterPlayed:
            H_R = data['RIGHT_HAND_POSITIONS']['h_end']
            H_rotation_R = data['ROTATIONS']['H_rotation_R']['Normal']['P3']
        else:
            H_rotation_R = data['ROTATIONS']['H_rotation_R']['Normal']['P0']
            H_R = data['RIGHT_HAND_POSITIONS']['h0']

        result['H_R'] = H_R
        result['H_rotation_R'] = H_rotation_R
    else:
        average_posisition = 0.5 * (positions[0] + positions[-1])
        hand_position = average_posisition - 0.5
        h0 = array(data['RIGHT_HAND_POSITIONS']['h0'])
        h3 = array(data['RIGHT_HAND_POSITIONS']['h3'])
        H_R = h0 + hand_position * (h3 - h0) / 3
        # 来一个随机大小为0.001的随机移动
        random_move = random.rand(3) * 0.001
        H_R += random_move
        result['H_R'] = H_R.tolist()

        h_rotation_0 = array(
            data['ROTATIONS']['H_rotation_R']['Normal']['P0'])
        h_rotation_3 = array(
            data['ROTATIONS']['H_rotation_R']['Normal']['P3'])
        H_rotation_R = h_rotation_0 + hand_position * \
            (h_rotation_3 - h_rotation_0) / 3
        result['H_rotation_R'] = H_rotation_R.tolist()

    t_index = "p_end" if isArpeggio else f"p{positions[0]}"
    T_R = array(data['RIGHT_HAND_POSITIONS'][t_index])
    if isAfterPlayed and "p" in usedRightFingers:
        move = array(data['RIGHT_HAND_LINES']["T_line"])
        T_R += move * fingerMoveDistanceWhilePlay * 1.2
    result['T_R'] = T_R.tolist()

    # 注意，因为ima指运动方向与p指相反，所以这里的移动方向是相反的
    i_index = "i_end" if isArpeggio else f"i{positions[1]}"
    I_R = array(data['RIGHT_HAND_POSITIONS'][i_index])
    if isAfterPlayed and "i" in usedRightFingers:
        move = array(data['RIGHT_HAND_LINES']["I_line"])
        I_R -= move * fingerMoveDistanceWhilePlay
    result['I_R'] = I_R.tolist()

    m_index = "m_end" if isArpeggio else f"m{positions[2]}"
    M_R = array(data['RIGHT_HAND_POSITIONS'][m_index])
    if isAfterPlayed and "m" in usedRightFingers:
        move = array(data['RIGHT_HAND_LINES']["M_line"])
        M_R -= move * fingerMoveDistanceWhilePlay
    result['M_R'] = M_R.tolist()

    r_index = "a_end" if isArpeggio else f"a{positions[3]}"
    R_R = array(data['RIGHT_HAND_POSITIONS'][r_index])
    if isAfterPlayed and "a" in usedRightFingers:
        move = array(data['RIGHT_HAND_LINES']["R_line"])
        R_R -= move * fingerMoveDistanceWhilePlay
    result['R_R'] = R_R.tolist()

    # ch指是不动的
    p_index = "ch_end" if isArpeggio else f"ch{positions[3]}"
    P_R = data['RIGHT_HAND_POSITIONS'][p_index]
    result['P_R'] = P_R

    return result


def calculateRightPick(avatar: str, stringIndex: int, pick_down: bool, isArpeggio: bool, isAfterPlayed: bool = False) -> Dict:
    json_file = f'asset\controller_infos\{avatar}.json'
    fingerMoveDistanceWhilePlay = 0.009
    with open(json_file, 'r') as f:
        data = json.load(f)

    result = {}
    thumb_index = "p_end" if isArpeggio else f"p{stringIndex}"
    T_R = data['RIGHT_HAND_POSITIONS'][thumb_index][:]
    move = data['RIGHT_HAND_LINES']["T_line"]
    # 如果当前音符是下拨，并且音符已经演奏完毕，或者当前音符是上拨，并且音符还没有演奏完毕，那么拨片的位置就是在弦的下方
    pick_on_low_position = (pick_down and isAfterPlayed) or (
        not pick_down and not isAfterPlayed)
    multiplier = 1 if pick_on_low_position else -1
    # 如果是琶音，而且此时已经是在低位置，那么不需要再移动拨片，其它情况都要移动拨片
    if not (isArpeggio and pick_on_low_position):
        T_R[0] += move[0] * fingerMoveDistanceWhilePlay * multiplier
        T_R[1] += move[1] * fingerMoveDistanceWhilePlay * multiplier
        T_R[2] += move[2] * fingerMoveDistanceWhilePlay * multiplier
    result['T_R'] = T_R

    return result
