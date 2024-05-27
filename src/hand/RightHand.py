from typing import List, Dict, Union
import itertools
from numpy import array, linalg
import json

rightFingers = {
    "p": 0,
    "i": 1,
    "m": 2,
    "a": 3
}


class RightHand():
    def __init__(self, usedFingers: List[str], rightFingerPositions: List[int], preUsedFingers: List[str], isArpeggio: bool = False):
        self.usedFingers = usedFingers
        self.rightFingerPositions = rightFingerPositions
        self.preUsedFingers = preUsedFingers
        self.isArpeggio = isArpeggio

    def validateRightHand(self, usedFingers=None, rightFingerPositions=None) -> bool:

        if rightFingerPositions == None:
            rightFingerPositions = self.rightFingerPositions
        if usedFingers == None:
            usedFingers = self.usedFingers

        return validateRightHandByFingerPositions(usedFingers, rightFingerPositions, False)

    def caculateDiff(self, otherRightHand: "RightHand") -> int:
        # 重复使用同一根手指的惩罚机制
        repeat_punish = 10
        diff = 0
        # 计算手指改变所在弦位置的情况，每有移动一根弦距就加1单位的diff
        for i in range(4):
            diff += abs(self.rightFingerPositions[i] -
                        otherRightHand.rightFingerPositions[i])

        # 检测两只手的usedFingers相同的元素个数有多少
        common_elements = list(set(self.usedFingers).intersection(
            set(otherRightHand.usedFingers)))
        pre_common_elements = list(set(self.preUsedFingers).intersection(
            set(otherRightHand.usedFingers)))
        same_finger_count = len(common_elements)
        pre_same_finger_count = len(pre_common_elements)

        # 检测重复使用的手指中有没有P指，如果有的话按加repeat_punish来计算重复指惩罚
        if 'p' in common_elements:
            diff += repeat_punish
            same_finger_count -= 1

        if 'p' in pre_common_elements:
            diff += 0.5 * repeat_punish
            pre_same_finger_count -= 1

        # 其它重复使用的手指按双倍repeat_punish来算，也就是非常不鼓励除P指以外的手指重复使用
        diff += 2 * repeat_punish * \
            (same_finger_count + 0.5 * pre_same_finger_count)

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


def finger_string_map_generator(allFingers: List[str], touchedStrings: List[int], unusedFingers: List[str], allStrings: List[int], prev_finger_string_map: List[Dict[str, Union[str, int]]] = None):
    if prev_finger_string_map is None:
        prev_finger_string_map = []

    if touchedStrings == []:
        for result in finger_string_map_generator2(unusedFingers, allStrings, prev_finger_string_map):
            yield result

    for current_finger, touchedString in itertools.product(allFingers, touchedStrings):
        current_pairing_is_legal = True
        current_finger_index = rightFingers[current_finger]

        # 检测当前配对组合是否和之前生成的配对组合有冲突
        for pairing in prev_finger_string_map:
            prev_finger = pairing['finger']
            prev_string = pairing['string']
            prev_index = rightFingers[prev_finger]
            # 这里注意，finger是从pima递增的，但现实中它们拨的弦序号是递减的，所以判断合理性时要留意这一点
            if (current_finger_index > prev_index and touchedString >= prev_string) or (current_finger_index < prev_index and touchedString <= prev_string) or (current_finger_index == prev_index and abs(prev_string-touchedString) > 1):
                current_pairing_is_legal = False

        if current_pairing_is_legal:
            next_allFingers = allFingers[:]
            next_allFingers.remove(current_finger)

            next_touchedStrings = touchedStrings[:]
            next_touchedStrings.remove(touchedString)

            next_unusedFingers = unusedFingers[:]
            next_unusedFingers.remove(current_finger)

            current_pairing = [
                {"finger": current_finger, "string": touchedString}]

            next_finger_string_map = prev_finger_string_map + current_pairing

            for result in finger_string_map_generator(next_allFingers, next_touchedStrings, next_unusedFingers, allStrings, next_finger_string_map):
                yield current_pairing + result


def finger_string_map_generator2(unusedFingers: List[str], allStrings: List[int], prev_finger_string_map: List[Dict[str, Union[str, int]]] = None):
    if prev_finger_string_map == None:
        prev_finger_string_map = []

    if unusedFingers == []:
        yield []
        return

    # 这里每次配对以后，不再移除已经配对的弦，因为不演奏的手指可以放在任一根弦上
    for current_finger, cur_string in itertools.product(unusedFingers, allStrings):
        current_pairing_is_legal = True
        current_finger_index = rightFingers[current_finger]

        # 检测当前配对组合是否和之前生成的配对组合有冲突
        for pairing in prev_finger_string_map:
            prev_finger = pairing['finger']
            prev_string = pairing['string']
            prev_index = rightFingers[prev_finger]
            if (current_finger_index > prev_index and cur_string > prev_string+1) or (current_finger_index < prev_index and cur_string < prev_string-1):
                current_pairing_is_legal = False

        if current_pairing_is_legal:
            next_allFingers = unusedFingers[:]
            next_allFingers.remove(current_finger)

            current_pairing = [
                {"finger": current_finger, "string": cur_string}]

            updated_finger_string_map = prev_finger_string_map + current_pairing
            for result in finger_string_map_generator2(next_allFingers, allStrings, updated_finger_string_map):
                yield current_pairing + result


def generatePossibleRightHands(touchedStrings: List[int], allFingers: List[str], allStrings: List[int]):
    possibleCombinations = []

    if len(touchedStrings) > 4:
        usedFingers = []
        rightFingerPositions = [5, 3, 3, 2]
        possibleCombinations.append({
            'usedFingers': usedFingers,
            'rightFingerPositions': rightFingerPositions
        })
    else:
        unused_fingers = allFingers[:]
        for result in finger_string_map_generator(allFingers, touchedStrings, unused_fingers, allStrings):
            # 输出的结果必须是每个手指都有对应的位置，否则说明配对不合法
            if result == None or len(result) < len(allFingers):
                continue
            rightFingerPositions = sort_fingers(result)
            usedFingers = get_usedFingers(result, touchedStrings)
            possibleCombinations.append({
                'usedFingers': usedFingers,
                'rightFingerPositions': rightFingerPositions
            })
    return possibleCombinations


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


def caculateRightHandFingers(avatar: str, positions: List[int], usedRightFingers: List[str], isAfterPlayed: bool = False) -> Dict:
    json_file = f'asset\controller_infos\{avatar}.json'
    with open(json_file, 'r') as f:
        data = json.load(f)
    fingerMoveDistanceWhilePlay = 0.003
    result = {}

    default_position = {
        "h": 2, "p": 4, "i": 2, "m": 1, "a": 0
    }
    finger_indexs = {
        "p": 0,
        "i": 1,
        "m": 2,
        "a": 3
    }

    H_default = array(data['RIGHT_HAND_POSITIONS']
                      [f'h{default_position["h"]}'])
    T_defalut = array(data['RIGHT_HAND_POSITIONS']
                      [f'p{default_position["p"]}'])
    I_default = array(data['RIGHT_HAND_POSITIONS']
                      [f'i{default_position["i"]}'])
    M_default = array(data['RIGHT_HAND_POSITIONS']
                      [f'm{default_position["m"]}'])
    R_default = array(data['RIGHT_HAND_POSITIONS']
                      [f'a{default_position["a"]}'])
    # ch指是总是和a指在同一弦上
    P_default = array(data['RIGHT_HAND_POSITIONS']
                      [f'ch{default_position["a"]}'])

    isArpeggio = usedRightFingers == []

    # 如果是扫弦，只计算h的位置，然后根据相对位置计算出其它手指的位置
    if isArpeggio:
        if isAfterPlayed:
            H_R = array(data['RIGHT_HAND_POSITIONS']['h_end'])
            H_rotation_R = array(
                data['ROTATIONS']['H_rotation_R']['Normal']['P3'])
            HP_R = array(data['RIGHT_HAND_POSITIONS']['P3_HP_R'])
            TP_R = array(data['RIGHT_HAND_POSITIONS']['P3_TP_R'])
        else:
            H_rotation_R = array(
                data['ROTATIONS']['H_rotation_R']['Normal']['P0'])
            H_R = array(data['RIGHT_HAND_POSITIONS']['h0'])
            HP_R = array(data['RIGHT_HAND_POSITIONS']['P0_HP_R'])
            TP_R = array(data['RIGHT_HAND_POSITIONS']['P0_TP_R'])

        T_R = array(H_R) + T_defalut - H_default
        I_R = array(H_R) + I_default - H_default
        M_R = array(H_R) + M_default - H_default
        R_R = array(H_R) + R_default - H_default
    else:
        offsets = 0
        for usedfinger in usedRightFingers:
            current_finger_position = positions[finger_indexs[usedfinger]]
            mutilplier = 3 if usedfinger == 'p' else 1
            offsets += current_finger_position * mutilplier

        total_finger_weights = len(
            usedRightFingers) if 'p' not in usedRightFingers else len(usedRightFingers) + 3
        average_offset = offsets / total_finger_weights
        """
        这一段解释一下：
        我只在blender里调整了h0和h3的两个位置，然后通过这两个位置的average_offset来计算其它手指的位置。 
        所谓 average_offset， 是计量了所有需要弹奏的手指的位置的平均值，然后通过这个平均值来决定手掌的位置，最后面再决定那些没有参与演奏的手指的位置。
        在计算 average_offset时，p指是特殊处理了的，它的权重是3，因为p指是决定手掌位置最重要的手指。 
              
        h0和h3两个极端手型，这两个组合包含了各个手指实际上能触碰的最高和最低弦：
        h0是在{"p": 2, "i": 0, "m": 0, "a": 0}的位置上，它的average_offset是1, 同时h_position=0
        h3是在{"p": 5, "i": 4, "m": 3, "a": 2}的位置上，它的average_offset是6，同时h_position=3
        
        假定h_position都是线性分布，满足：
        h_position = m * average_offset + b
        
        根据上面这两个值，我们可以计算出来线性插值的斜率是：
        m = (3 - 0) / (6 - 1)  = 0.6
        
        最终线性插值的计算公式是：
        h_position = 0.6 * average_offset - 0.6
        
        而这个时间手掌的实际位置是：
        H_R = h0 + h_position * (h3 - h0) / 3
        """
        hand_position = 0.6 * average_offset - 0.6

        h0 = array(data['RIGHT_HAND_POSITIONS']['h0'])
        h3 = array(data['RIGHT_HAND_POSITIONS']['h3'])
        H_R = h0 + hand_position * (h3 - h0) / 3

        h_rotation_0 = array(
            data['ROTATIONS']['H_rotation_R']['Normal']['P0'])
        h_rotation_3 = array(
            data['ROTATIONS']['H_rotation_R']['Normal']['P3'])
        H_rotation_R = h_rotation_0 + hand_position * \
            (h_rotation_3 - h_rotation_0) / 3

        hp_0 = array(data['RIGHT_HAND_POSITIONS']['P0_HP_R'])
        hp_3 = array(data['RIGHT_HAND_POSITIONS']['P3_HP_R'])
        HP_R = hp_0 + hand_position * (hp_3 - hp_0) / 3

        tp_0 = array(data['RIGHT_HAND_POSITIONS']['P0_TP_R'])
        tp_3 = array(data['RIGHT_HAND_POSITIONS']['P3_TP_R'])
        TP_R = tp_0 + hand_position * (tp_3 - tp_0) / 3

        t_index = f"p{positions[0]}"
        T_R = array(data['RIGHT_HAND_POSITIONS'][t_index]
                    ) if "p" in usedRightFingers else H_R + T_defalut - H_default
        if isAfterPlayed and "p" in usedRightFingers:
            move = array(data['RIGHT_HAND_LINES']["T_line"])
            T_R += move * fingerMoveDistanceWhilePlay * 1.2

        # 注意，因为ima指运动方向与p指相反，所以这里的移动方向是相反的
        i_index = f"i{positions[1]}"
        I_R = array(data['RIGHT_HAND_POSITIONS'][i_index]
                    ) if "i" in usedRightFingers else H_R + I_default - H_default
        if isAfterPlayed and "i" in usedRightFingers:
            move = (I_R - H_R) / linalg.norm(I_R - H_R)
            I_R -= move * fingerMoveDistanceWhilePlay

        m_index = f"m{positions[2]}"
        M_R = array(data['RIGHT_HAND_POSITIONS'][m_index]
                    ) if "m" in usedRightFingers else H_R + M_default - H_default
        if isAfterPlayed and "m" in usedRightFingers:
            move = (M_R - H_R) / linalg.norm(M_R - H_R)
            M_R -= move * fingerMoveDistanceWhilePlay

        r_index = f"a{positions[3]}"
        R_R = array(data['RIGHT_HAND_POSITIONS'][r_index]
                    ) if "a" in usedRightFingers else H_R + R_default - H_default
        if isAfterPlayed and "a" in usedRightFingers:
            move = (R_R - H_R) / linalg.norm(R_R - H_R)
            R_R -= move * fingerMoveDistanceWhilePlay

    # ch指是不动的，根据相对位置计算出ch的位置
    P_R = H_R + P_default - H_default

    result.update({
        'H_R': H_R.tolist(),
        'H_rotation_R': H_rotation_R.tolist(),
        'HP_R': HP_R.tolist(),
        'TP_R': TP_R.tolist(),
        'T_R': T_R.tolist(),
        'I_R': I_R.tolist(),
        'R_R': R_R.tolist(),
        'M_R': M_R.tolist(),
        'P_R': P_R.tolist()
    })

    return result


def calculateRightPick(avatar: str, stringIndex: int, isArpeggio: bool, should_stay_at_lower_position: bool) -> Dict:
    json_file = f'asset\controller_infos\{avatar}.json'
    fingerMoveDistanceWhilePlay = 0.009
    with open(json_file, 'r') as f:
        data = json.load(f)

    result = {}
    thumb_index = "p_end" if isArpeggio else f"p{stringIndex}"
    T_R = data['RIGHT_HAND_POSITIONS'][thumb_index][:]
    # 只要当前不是在演奏琶音，都需要移动拨片位置。情况有以下几种：
    # 1. pick是在高位置，而且是已经演奏完毕，此时pick的位置是在T_R的下方
    # 2. pick是在低位置，而且还没有开始演奏，此时Pick的位置是在T_R的下方
    # 3. pick是在低位置，而且是已经演奏完毕，此时pick的位置是在T_R的上方
    # 4. pick是在高位置，而且还没有开始演奏，此时Pick的位置是在T_R的上方
    if not isArpeggio:
        move = data['RIGHT_HAND_LINES']["T_line"]
        # 如果当前pick位置在当前弦的位置之下，那么就是在低位置，否则就是在高位置
        multiplier = 1 if should_stay_at_lower_position else -1
        T_R[0] += move[0] * fingerMoveDistanceWhilePlay * multiplier
        T_R[1] += move[1] * fingerMoveDistanceWhilePlay * multiplier
        T_R[2] += move[2] * fingerMoveDistanceWhilePlay * multiplier
    result['T_R'] = T_R

    return result
