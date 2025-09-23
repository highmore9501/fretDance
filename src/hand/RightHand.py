from typing import List, Dict, Union, Any
import itertools
from numpy import array, linalg
import numpy as np
import json
from src.utils.caculateCrossPoint import get_cross_point
from src.utils.utils import getStringTouchPosition, slerp

RIGHT_FINGERS = {
    "p": 0,
    "i": 1,
    "m": 2,
    "a": 3
}


class RightHand():
    def __init__(self, usedFingers: List[str], rightFingerPositions: List[int], preUsedFingers: List[str], isArpeggio: bool = False, is_playing_bass: bool = False):
        self.usedFingers = usedFingers
        self.rightFingerPositions = rightFingerPositions
        self.preUsedFingers = preUsedFingers  # 之所以还要有上一个手型的手指列表，是为了计算diff时，考虑更多一点
        self.isArpeggio = isArpeggio
        self.is_playing_bass = is_playing_bass

    def validateRightHand(self, usedFingers: list[str] = [], rightFingerPositions: list[int] = []) -> bool:

        if len(rightFingerPositions) == 0:
            rightFingerPositions = self.rightFingerPositions
        if len(usedFingers) == 0:
            usedFingers = self.usedFingers

        return self.validateRightHandByFingerPositions(usedFingers, rightFingerPositions, False)

    def caculateDiff(self, otherRightHand: "RightHand") -> float:
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

    def validateRightHandByFingerPositions(self, usedFingers: list[str], rightFingerPositions: List[int], repeated_fingers_checked: bool) -> bool:
        for i in range(len(rightFingerPositions) - 1):
            # 检测手指的位置是否从左到右递减，如果手指分布不符合科学，判断为错误;bass因为要考虑到会有im指交替拨低音弦的情况，需要另外考虑
            if rightFingerPositions[i] < rightFingerPositions[i+1] and not self.is_playing_bass:
                return False
            if rightFingerPositions[i] < rightFingerPositions[i+1]+1:
                return False

        # 如果没有p指，而且其它手指已经预检测掉了重复和可能性，那么就直接返回True
        if 'p' not in usedFingers and repeated_fingers_checked:
            return True

        usedString = []
        used_p_strings = []
        for finger in usedFingers:
            current_string = rightFingerPositions[RIGHT_FINGERS[finger]]
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


def finger_string_map_generator(allFingers: List[str], touchedStrings: List[int], unusedFingers: List[str], allStrings: List[int], prev_finger_string_map: List[Dict[str, Any]] = []):
    if touchedStrings == []:
        for result in rest_finger_string_map_generator(unusedFingers, allStrings, prev_finger_string_map):
            yield result

    for current_finger, touchedString in itertools.product(allFingers, touchedStrings):
        current_pairing_is_legal = True
        current_finger_index = RIGHT_FINGERS[current_finger]

        # 检测当前配对组合是否和之前生成的配对组合有冲突
        for pairing in prev_finger_string_map:
            prev_finger = pairing['finger']
            prev_string = pairing['string']
            prev_index = RIGHT_FINGERS[prev_finger]
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


def rest_finger_string_map_generator(unusedFingers: List[str], allStrings: List[int], prev_finger_string_map: List[Dict[Any, Any]] = []):
    """
    这个方法是将剩余的不拨弦的手指与弦进行配对
    """

    if unusedFingers == []:
        yield []
        return

    # 这里每次配对以后，不再移除已经配对的弦，因为不演奏的手指可以放在任一根弦上
    for current_finger, cur_string in itertools.product(unusedFingers, allStrings):
        current_pairing_is_legal = True
        current_finger_index = RIGHT_FINGERS[current_finger]

        # 检测当前配对组合是否和之前生成的配对组合有冲突
        for pairing in prev_finger_string_map:
            prev_finger = pairing['finger']
            prev_string = pairing['string']
            prev_index = RIGHT_FINGERS[prev_finger]
            if (current_finger_index > prev_index and cur_string > prev_string + 1) or (current_finger_index < prev_index and cur_string < prev_string-1):
                current_pairing_is_legal = False

        if current_pairing_is_legal:
            next_allFingers = unusedFingers[:]
            next_allFingers.remove(current_finger)

            current_pairing = [
                {"finger": current_finger, "string": cur_string}]

            updated_finger_string_map = prev_finger_string_map + current_pairing
            for result in rest_finger_string_map_generator(next_allFingers, allStrings, updated_finger_string_map):
                yield current_pairing + result


def generatePossibleRightHands(touchedStrings: List[int], allFingers: List[str], allStrings: List[int]):
    possibleCombinations = []

    if len(touchedStrings) > 4:
        usedFingers = []
        rightFingerPositions = [5, 4, 3, 2]
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


def sort_fingers(finger_list: List[Any]):
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


def get_usedFingers(finger_list: List[Any], usedStrings: List[int]):
    return [item['finger'] for item in finger_list if item['string'] in usedStrings]


def new_finger_position_method(avatar_data: Any, rightFingerPositions: List[int], isArpeggio: bool, isAfterPlayed: bool, hand_position: float, used_right_fingers: List[str],  max_string_index: int) -> Dict:
    """
    新的定位方法基本上是这样的：
    如果是扫弦，那么直接读取扫弦状态的基准状态，然后结束。
    如果不是扫弦，那么读取h0和h3状态，然后用hand_position计算出插值状态下所有的控件位置。
    接下来，使用计算出来的手掌位置和手指位置，计算出所有在拨弦手指的触弦点。而未使用的手指，需要保留在休息位置，就直接使用上一步计算出来的位置就行了。
    计算出来拨弦手指的触弦点以后，根据当前是否拨弦结束，来决定手指实际应该停留的位置。
    如果拨弦指是IMA指，那么预备点和结束点以及触弦点，都是在手掌->手指的直线上。
    如果拨弦指大拇指指，需要额外读取一个拨弦方向，然后计算出来预备点，结束点的位置。
    """
    result = {}

    # 根据手掌的位置先计算所有确定手掌和手臂位置的点
    h0 = array(avatar_data['RIGHT_HAND_POSITIONS']['Normal_P0_H_R'])
    h3 = array(avatar_data['RIGHT_HAND_POSITIONS']['Normal_P3_H_R'])
    P0 = array(avatar_data['LEFT_FINGER_POSITIONS']['P0'])
    P1 = array(avatar_data['LEFT_FINGER_POSITIONS']['P1'])
    # 大拇指的移动方向以及其它手指的移动方向，一开始设置为None
    t_move = None
    f_move = None
    # 定义手指运动的距离，是P0和P1之间的距离的8分之1，相当于0.725的弦距
    fingerMoveDistanceWhilePlay = np.linalg.norm(P0 - P1) / 8

    if isArpeggio:
        if isAfterPlayed:
            H_R = array(avatar_data['RIGHT_HAND_POSITIONS']['Normal_Pend_H_R'])
            H_rotation_R = array(
                avatar_data['ROTATIONS']['H_rotation_R']['Normal']['Pend'])
            HP_R = array(
                avatar_data['RIGHT_HAND_POSITIONS']['Normal_Pend_HP_R'])
            TP_R = array(avatar_data['RIGHT_HAND_POSITIONS']['tpend'])
            T_R = array(avatar_data['RIGHT_HAND_POSITIONS']['pend'])
            I_R = array(avatar_data['RIGHT_HAND_POSITIONS']['iend'])
            M_R = array(avatar_data['RIGHT_HAND_POSITIONS']['mend'])
            R_R = array(avatar_data['RIGHT_HAND_POSITIONS']['aend'])
            P_R = array(avatar_data['RIGHT_HAND_POSITIONS']['chend'])
        else:
            H_rotation_R = array(
                avatar_data['ROTATIONS']['H_rotation_R']['Normal']['P0'])
            H_R = array(avatar_data['RIGHT_HAND_POSITIONS']['Normal_P0_H_R'])
            HP_R = array(avatar_data['RIGHT_HAND_POSITIONS']['Normal_P0_HP_R'])
            TP_R = array(avatar_data['RIGHT_HAND_POSITIONS']['tp0'])
            T_R = array(avatar_data['RIGHT_HAND_POSITIONS']['p0'])
            I_R = array(avatar_data['RIGHT_HAND_POSITIONS']['i0'])
            M_R = array(avatar_data['RIGHT_HAND_POSITIONS']['m0'])
            R_R = array(avatar_data['RIGHT_HAND_POSITIONS']['a0'])
            P_R = array(avatar_data['RIGHT_HAND_POSITIONS']['ch0'])
    else:
        H_R = h0 + hand_position * (h3 - h0) / 3

        h_rotation_0 = array(
            avatar_data['ROTATIONS']['H_rotation_R']['Normal']['P0'])
        h_rotation_3 = array(
            avatar_data['ROTATIONS']['H_rotation_R']['Normal']['P3'])

        if len(h_rotation_0) == 3:
            H_rotation_R = h_rotation_0 + hand_position * \
                (h_rotation_3 - h_rotation_0) / 3
        elif len(h_rotation_0) == 4:
            hand_weight = hand_position / 3
            H_rotation_R = slerp(h_rotation_0, h_rotation_3, hand_weight)
        else:
            raise Exception("Unknown hand rotation type")

        hp_0 = array(avatar_data['RIGHT_HAND_POSITIONS']['Normal_P0_HP_R'])
        hp_3 = array(avatar_data['RIGHT_HAND_POSITIONS']['Normal_P3_HP_R'])
        HP_R = hp_0 + hand_position * (hp_3 - hp_0) / 3

        tp_0 = array(avatar_data['RIGHT_HAND_POSITIONS']['tp0'])
        tp_3 = array(avatar_data['RIGHT_HAND_POSITIONS']['tp3'])
        TP_R = tp_0 + hand_position * (tp_3 - tp_0) / 3

        N_quat_0 = array(avatar_data['RIGHT_HAND_LINES']
                         ['right_hand_normal_p0']['vector'])
        N_quat_3 = array(avatar_data['RIGHT_HAND_LINES']
                         ['right_hand_normal_p3']['vector'])
        N_quat = N_quat_0 + hand_position * (N_quat_3 - N_quat_0) / 3

        P0 = array(avatar_data['LEFT_FINGER_POSITIONS']['P0'])
        P1 = array(avatar_data['LEFT_FINGER_POSITIONS']['P1'])
        P2 = array(avatar_data['LEFT_FINGER_POSITIONS']['P2'])
        P3 = array(avatar_data['LEFT_FINGER_POSITIONS']['P3'])

        t0 = array(avatar_data['RIGHT_HAND_POSITIONS']['p0'])
        t3 = array(avatar_data['RIGHT_HAND_POSITIONS']['p3'])
        t_rest_postion = t0 + hand_position * (t3 - t0) / 3

        thumb_direction_0 = array(
            avatar_data['RIGHT_HAND_LINES']['right_thumb_direct_p0']['vector'])
        thumb_direction_3 = array(
            avatar_data['RIGHT_HAND_LINES']['right_thumb_direct_p3']['vector'])
        thumb_direction = thumb_direction_0 + hand_position * \
            (thumb_direction_3 - thumb_direction_0) / 3

        finger_direct_0 = array(
            avatar_data['RIGHT_HAND_LINES']['right_finger_direct_p0']['vector'])
        finger_direct_3 = array(
            avatar_data['RIGHT_HAND_LINES']['right_finger_direct_p3']['vector'])
        finger_direct = finger_direct_0 + hand_position * \
            (finger_direct_3 - finger_direct_0) / 3

        i0 = array(avatar_data['RIGHT_HAND_POSITIONS']['i0'])
        i3 = array(avatar_data['RIGHT_HAND_POSITIONS']['i3'])
        i_rest_position = i0 + hand_position * (i3 - i0) / 3

        m0 = array(avatar_data['RIGHT_HAND_POSITIONS']['m0'])
        m3 = array(avatar_data['RIGHT_HAND_POSITIONS']['m3'])
        m_rest_position = m0 + (m3 - m0) * hand_position / 3

        a0 = array(avatar_data['RIGHT_HAND_POSITIONS']['a0'])
        a3 = array(avatar_data['RIGHT_HAND_POSITIONS']['a3'])
        a_rest_position = a0 + (a3 - a0) * hand_position / 3

        ch0 = array(avatar_data['RIGHT_HAND_POSITIONS']['ch0'])
        ch3 = array(avatar_data['RIGHT_HAND_POSITIONS']['ch3'])
        ch_rest_position = ch0 + (ch3 - ch0) * hand_position / 3

        if "p" in used_right_fingers:
            p_current_string_index = rightFingerPositions[0]
            # t_target就是大拇指运动时的目标位置，和其它手指都是向掌心运动不同，大拇指是往弦上运动的
            t_target = t_rest_postion + thumb_direction
            t_touch_position = getStringTouchPosition(
                t_target, t_rest_postion, N_quat, P0, P1, P2, P3, p_current_string_index, max_string_index)
            # 读取大拇指拨弦的方向
            t_move = thumb_direction / np.linalg.norm(thumb_direction)
            if isAfterPlayed:
                T_R = t_touch_position + t_move * fingerMoveDistanceWhilePlay
            else:
                T_R = t_touch_position - t_move * fingerMoveDistanceWhilePlay
        else:
            T_R = t_rest_postion

        # 处理i, m, a三个手指的计算,有一个小`r`其实就是a指的英文ring
        finger_configs = [
            ('i', 1, i_rest_position),
            ('m', 2, m_rest_position),
            ('r', 3, a_rest_position)
        ]

        finger_results = {}

        # 处理ima三个手指的拨弦，它们的逻辑是相似的
        for finger_char, finger_idx, rest_pos in finger_configs:
            # 小拇指的英文缩写和吉他用语里的左手小拇指不一样，导致这个判断的写法会啰嗦一点
            if finger_char in used_right_fingers or finger_char == 'r' and 'a' in used_right_fingers:
                # 计算手指的拨弦方向，这里要注意因为在blender中方向线与手指运动的方式是相反的，所以这里要加负号
                f_move = -finger_direct / np.linalg.norm(finger_direct)
                current_string_index = rightFingerPositions[finger_idx]
                target = rest_pos + finger_direct
                touch_position = getStringTouchPosition(
                    target, rest_pos, N_quat, P0, P1, P2, P3, current_string_index, max_string_index)

                if isAfterPlayed:
                    finger_results[finger_char.upper() + '_R'] = touch_position + \
                        f_move * fingerMoveDistanceWhilePlay
                else:
                    finger_results[finger_char.upper() + '_R'] = touch_position - \
                        f_move * fingerMoveDistanceWhilePlay

            else:
                finger_results[finger_char.upper(
                ) + '_R'] = rest_pos

        # 然后分别赋值
        I_R = finger_results['I_R']
        M_R = finger_results['M_R']
        R_R = finger_results['R_R']

        # ch指是不参与演奏的，所以直接使用休息位置
        P_R = ch_rest_position

        # 给拨弦后的手掌添加一点移动，这个移动适用于所有不参与演奏的手指以及手掌自己
        h_move = f_move if f_move is not None else t_move
        if h_move is not None and isAfterPlayed:
            h_move = h_move * fingerMoveDistanceWhilePlay * 0.25
            H_R = H_R - h_move

            if "p" not in used_right_fingers:
                T_R -= h_move

            # 处理ima三个手指的拨弦，它们的逻辑是相似的
            for finger_char, finger_idx, rest_pos in finger_configs:
                # 小拇指的英文缩写和吉他用语里的左手小拇指不一样，导致这个判断的写法会啰嗦一点
                if finger_char not in used_right_fingers and (finger_char != 'r' or 'a' not in used_right_fingers):
                    finger_results[finger_char.upper(
                    ) + '_R'] -= h_move

    result.update({
        'H_R': H_R.tolist(),
        'H_rotation_R': H_rotation_R.tolist(),
        'HP_R': HP_R.tolist(),
        'TP_R': TP_R.tolist(),
        'T_R': T_R.tolist(),
        'I_R': I_R.tolist(),
        'M_R': M_R.tolist(),
        'R_R': R_R.tolist(),
        'P_R': P_R.tolist()
    })
    return result


def caculateRightHandFingers(avatar_data: dict, rightFingerPositions: List[int], usedRightFingers: List[str], max_string_index: int = 5, isAfterPlayed: bool = False) -> Dict:

    finger_indexs = {
        "p": 0,
        "i": 1,
        "m": 2,
        "a": 3
    }

    isArpeggio = usedRightFingers == []

    hand_position = 0

    if not isArpeggio:
        offsets = 0
        for usedfinger in usedRightFingers:
            current_finger_position = rightFingerPositions[finger_indexs[usedfinger]]
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
        h3是在{"p": 2, "i": 0, "m": 0, "a": 0}的位置上，它的average_offset是1, 同时h_position=3
        h0是在{"p": 5, "i": 4, "m": 3, "a": 2}的位置上，它的average_offset是6，同时h_position=0
        
        假定h_position都是线性分布，满足：
        h_position = m * average_offset + b
        
        根据上面这两个值，我们可以计算出来线性插值的斜率是：
        m = -0.6
        
        最终线性插值的计算公式是：
        h_position = -0.6 * average_offset + 3.6
        
        而这个时间手掌的实际位置是：
        H_R = h0 + h_position * (h3 - h0) / 3
        """
        hand_position = -0.6 * average_offset + 3.6

    result = new_finger_position_method(
        avatar_data, rightFingerPositions, isArpeggio, isAfterPlayed, hand_position, usedRightFingers, max_string_index)

    return result


def calculateRightPick(avatar: str, stringIndex: int, isArpeggio: bool, should_stay_at_lower_position: bool, guitar_max_string_index: int = 5) -> Dict:
    json_file = f'asset/controller_infos/{avatar}.json'
    with open(json_file, 'r') as f:
        data = json.load(f)

    result = {}

    if isArpeggio and should_stay_at_lower_position:
        T_R = data['RIGHT_HAND_POSITIONS']['pend']
        H_R = data['RIGHT_HAND_POSITIONS']['Normal_Pend_H_R']
        HP_R = data['RIGHT_HAND_POSITIONS']['Normal_Pend_HP_R']
        H_rotation_R = data['ROTATIONS']['H_rotation_R']['Normal']['Pend']
        result = {
            'T_R': T_R,
            'H_R': H_R,
            'HP_R': HP_R,
            'H_rotation_R': H_rotation_R
        }
    else:
        # 这里的后缀high和low分别表示高音和低音，它刚刚好和stringIndex顺序相反
        tr_high = data['RIGHT_HAND_POSITIONS']['p3']
        tr_low = data['RIGHT_HAND_POSITIONS']['p0']
        h_r_high = data['RIGHT_HAND_POSITIONS']['Normal_P3_H_R']
        h_r_low = data['RIGHT_HAND_POSITIONS']['Normal_P0_H_R']
        hp_r_high = data['RIGHT_HAND_POSITIONS']['Normal_P3_HP_R']
        hp_r_low = data['RIGHT_HAND_POSITIONS']['Normal_P0_HP_R']
        h_rotation_r_high = data['ROTATIONS']['H_rotation_R']['Normal']['P3']
        h_rotation_r_low = data['ROTATIONS']['H_rotation_R']['Normal']['P0']

        tr_diff = np.linalg.norm(np.array(tr_high) - np.array(tr_low))
        fingerMoveDistanceWhilePlay = tr_diff / 20

        move = data['RIGHT_HAND_LINES']["T_line"]['vector']
        # 因为相反，所以这里的权重应该是用1减一下
        thumb_weight = 1-(stringIndex / (guitar_max_string_index + 1))

        T_R = np.array(tr_high) * thumb_weight + \
            np.array(tr_low) * (1 - thumb_weight)
        H_R = np.array(h_r_high) * thumb_weight + \
            np.array(h_r_low) * (1 - thumb_weight)
        HP_R = np.array(hp_r_high) * thumb_weight + \
            np.array(hp_r_low) * (1 - thumb_weight)
        H_rotation_R = slerp(h_rotation_r_high, h_rotation_r_low, thumb_weight)

        # 如果当前pick位置在当前弦的位置之下，那么就是在低位置，否则就是在高位置
        multiplier = 1 if should_stay_at_lower_position else -1
        T_R += np.array(move) * fingerMoveDistanceWhilePlay * multiplier

        result = {
            'T_R': T_R.tolist(),
            'H_R': H_R.tolist(),
            'HP_R': HP_R.tolist(),
            'H_rotation_R': H_rotation_R.tolist(),
        }

    return result
