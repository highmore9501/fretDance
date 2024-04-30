import json
from src.midi.midiToNote import calculate_frame
from numpy import array, linalg, cross, random
from typing import Dict

from ..hand.LeftFinger import PRESSSTATE
from ..hand.RightHand import caculateRightHandFingers
from ..utils.utils import get_position_by_fret


def leftHand2Animation(recorder: str, animation: str, tempo_changes, ticks_per_beat, FPS: float) -> None:
    """
    :params recorder: the path of the recorder file
    :params animation: the path of the file store information for animation
    :params BPM: the BPM of the music
    :params FPS: the FPS of the animation"""
    from src.blender.blenderRecords import LEFT_FINGER_POSITIONS
    finger_position_p0 = array(LEFT_FINGER_POSITIONS["P0"])
    finger_position_p1 = array(LEFT_FINGER_POSITIONS["P1"])
    finger_position_p2 = array(LEFT_FINGER_POSITIONS["P2"])

    # 计算finger_position_p0,finger_position_p1,finger_position_p2三点组成的平面上的法线值
    normal = cross(finger_position_p0 - finger_position_p1,
                   finger_position_p2 - finger_position_p1)
    normal = normal / linalg.norm(normal)

    handDicts = None
    data_for_animation = []

    with open(recorder, "r") as f:
        handDicts = json.load(f)

    for i in range(len(handDicts)):
        item = handDicts[i]
        next_tick = None
        if i != len(handDicts) - 1:
            next_item = handDicts[i + 1]
            next_tick = next_item["real_tick"]
        real_tick = item["real_tick"]
        frame = calculate_frame(tempo_changes, ticks_per_beat, FPS, real_tick)

        # 计算左手的动画信息
        fingerInfos = animatedLeftHand(item, normal)
        data_for_animation.append({
            "frame": frame,
            "fingerInfos": fingerInfos
        })

        # 这里是计算左手按弦需要保持的时间
        if next_tick:
            next_frame = calculate_frame(
                tempo_changes, ticks_per_beat, FPS, next_tick)
            if frame + 2 < next_frame:
                data_for_animation.append({
                    "frame": next_frame-3,
                    "fingerInfos": fingerInfos
                })

    with open(animation, "w") as f:
        json.dump(data_for_animation, f)


def animatedLeftHand(item: object, normal: array):
    leftHand = item["leftHand"]
    fingerInfos = {}
    hand_fret = 1
    max_finger_string_index = 0
    index_finger_string_number = 0

    # 用于统计每个手指都在哪根弦上的dict
    finger_string_numbers = {
        1: 0,
        2: 0,
        3: 0,
        4: 0
    }

    for data in leftHand:
        fingerIndex = data["fingerIndex"]
        stringIndex = data["fingerInfo"]["stringIndex"]
        fret = data["fingerInfo"]["fret"]
        press = data["fingerInfo"]["press"]

        min_press_fingerIndex = 4
        # skip open string. 空弦音跳过
        if fingerIndex == -1:
            continue

        # 计算最大的弦数，方便后面计算手的位置
        max_finger_string_index = max(max_finger_string_index, stringIndex)

        # 这里是计算当前手型的把位
        if fingerIndex < min_press_fingerIndex:
            min_press_fingerIndex = fingerIndex
            hand_fret = max(fret - fingerIndex + 1, 1)

        # 不按弦的手指会稍微移动，以避免和按弦的手指挤在一起
        if press == PRESSSTATE['Open']:
            if stringIndex > 2:
                stringIndex -= 0.5
            else:
                stringIndex += 0.5

        # 如果手指有横按的情况，并且遍历到的stringIndex比之前计算过的要大，那么需要重新计算手指的位置
        need_recaculate = finger_string_numbers[fingerIndex] < stringIndex and 5 > press > 1

        if press < 2 or press == 5 or need_recaculate:
            finger_string_numbers[fingerIndex] = stringIndex
            finger_position = twiceLerpFingers(fret, stringIndex)
        else:
            continue

        # 如果手指没有按下，那么手指位置会稍微上移
        if press == PRESSSTATE['Open']:
            finger_position -= normal * 0.003

        if fingerIndex == 1:
            position_value_name = "I_L"
        elif fingerIndex == 2:
            position_value_name = "M_L"
        elif fingerIndex == 3:
            position_value_name = "R_L"
        elif fingerIndex == 4:
            position_value_name = "P_L"

        fingerInfos[position_value_name] = finger_position.tolist()

    # 判断当前应该使用哪种手型来计算
    index_finger_string_number = finger_string_numbers[1]
    differences = [
        string - index_finger_string_number for string in finger_string_numbers.values()]
    hand_state = max(differences, key=abs)

    hand_position = twiceLerp(
        hand_state=hand_state,
        value="H_L",
        valueType="position",
        fret=hand_fret,
        stringIndex=max_finger_string_index)

    # 来一个随机大小为0.0005的随机移动
    random_move = random.rand(3) * 0.001
    hand_position += random_move

    fingerInfos["H_L"] = hand_position.tolist()

    hand_IK_pivot_position = twiceLerp(
        hand_state=hand_state,
        value="HP_L",
        valueType="position",
        fret=hand_fret,
        stringIndex=index_finger_string_number)
    fingerInfos["HP_L"] = hand_IK_pivot_position.tolist()

    hand_rotation_y = twiceLerp(
        hand_state=hand_state,
        value="H_rotation_Y_L",
        valueType="rotation",
        fret=hand_fret,
        stringIndex=index_finger_string_number)
    fingerInfos["H_rotation_Y_L"] = hand_rotation_y.tolist()

    hand_rotation_x = twiceLerp(
        hand_state=hand_state,
        value="H_rotation_X_L",
        valueType="rotation",
        fret=hand_fret,
        stringIndex=index_finger_string_number)
    fingerInfos["H_rotation_X_L"] = hand_rotation_x.tolist()

    thumb_position = twiceLerp(
        hand_state=hand_state,
        value="T_L",
        valueType="position",
        fret=hand_fret,
        stringIndex=index_finger_string_number)
    fingerInfos["T_L"] = thumb_position.tolist()

    thumb_IK_pivot_position = twiceLerp(
        hand_state=hand_state,
        value="TP_L",
        valueType="position",
        fret=hand_fret,
        stringIndex=index_finger_string_number)
    fingerInfos["TP_L"] = thumb_IK_pivot_position.tolist()

    return fingerInfos


def rightHand2Animation(recorder: str, animation: str, tempo_changes: list, ticks_per_beat: int, FPS: float) -> None:
    data_for_animation = []
    with open(recorder, "r") as f:
        handDicts = json.load(f)

        for data in handDicts:
            real_tick = data["real_tick"]
            frame = calculate_frame(
                tempo_changes, ticks_per_beat, FPS, real_tick)
            right_hand = data["rightHand"]
            usedFingers = right_hand["usedFingers"]
            rightFingerPositions = right_hand["rightFingerPositions"]
            rightHandPosition = right_hand["rightHandPosition"]
            afterPlayedRightFingerPositions = right_hand["afterPlayedRightFingerPositions"]

            ready = caculateRightHandFingers(
                rightFingerPositions, usedFingers, rightHandPosition, isAfterPlayed=False)

            played = caculateRightHandFingers(
                afterPlayedRightFingerPositions, usedFingers, rightHandPosition, isAfterPlayed=True)

            data_for_animation.append({
                "frame": frame,
                "fingerInfos": ready,
            })

            elapsed_frame = 3 if usedFingers == [] else 1
            data_for_animation.append({
                "frame": frame + elapsed_frame,
                "fingerInfos": played,
            })

    with open(animation, "w") as f:
        json.dump(data_for_animation, f)


def twiceLerpFingers(fret: int, stringIndex: int) -> Dict:
    from ..blender.blenderRecords import LEFT_FINGER_POSITIONS
    p0 = array(LEFT_FINGER_POSITIONS["P0"])
    p1 = array(LEFT_FINGER_POSITIONS["P1"])
    p2 = array(LEFT_FINGER_POSITIONS["P2"])
    p3 = array(LEFT_FINGER_POSITIONS["P3"])

    p_fret_0 = get_position_by_fret(fret, p0, p2)
    p_fret_1 = get_position_by_fret(fret, p1, p3)

    p_final = p_fret_0 + (p_fret_1 - p_fret_0) * stringIndex / 5

    return p_final


def twiceLerp(hand_state: int, value: str, valueType: str, fret: int, stringIndex: int | float) -> array:
    data_dict = None
    from ..blender.blenderRecords import OUTER_LEFT_HAND_POSITIONS, INNER_LEFT_HAND_POSITIONS, NORMAL_LEFT_HAND_POSITIONS, OUTER_LEFT_HAND_ROTATIONS, INNER_LEFT_HAND_ROTATIONS, NORMAL_LEFT_HAND_ROTATIONS

    if valueType == "position":
        data_dict = NORMAL_LEFT_HAND_POSITIONS
    elif valueType == "rotation":
        data_dict = NORMAL_LEFT_HAND_ROTATIONS
    else:
        print("valueType error")

    p0 = array(data_dict["P0"][value])
    p1 = array(data_dict["P1"][value])
    p2 = array(data_dict["P2"][value])
    p3 = array(data_dict["P3"][value])

    if hand_state == 0:
        p_fret_0 = get_position_by_fret(fret, p0, p2)
        p_fret_1 = get_position_by_fret(fret, p1, p3)
        p_final = p_fret_0 + (p_fret_1 - p_fret_0) * stringIndex / 5
    elif hand_state > 0:
        if valueType == "position":
            outer_data_dict = OUTER_LEFT_HAND_POSITIONS
        else:
            outer_data_dict = OUTER_LEFT_HAND_ROTATIONS

        out_p0 = array(outer_data_dict["P0"][value])
        out_p2 = array(outer_data_dict["P2"][value])

        real_p0 = p0 + (out_p0 - p0) * hand_state/5
        real_p2 = p2 + (out_p2 - p2) * hand_state/5

        p_fret_0 = get_position_by_fret(fret, real_p0, real_p2)
        p_fret_1 = get_position_by_fret(fret, p1, p3)
        p_final = p_fret_0 + (p_fret_1 - p_fret_0) * stringIndex / 5
    else:
        if valueType == "position":
            inner_data_dict = INNER_LEFT_HAND_POSITIONS
        else:
            inner_data_dict = INNER_LEFT_HAND_ROTATIONS

        inner_p1 = array(inner_data_dict["P1"][value])
        inner_p3 = array(inner_data_dict["P3"][value])

        real_P1 = p1 + (inner_p1 - p1) * abs(hand_state)/5
        real_P3 = p3 + (inner_p3 - p3) * abs(hand_state)/5

        p_fret_0 = get_position_by_fret(fret, p0, p2)
        p_fret_1 = get_position_by_fret(fret, real_P1, real_P3)
        p_final = p_fret_0 + (p_fret_1 - p_fret_0) * stringIndex / 5

    return p_final
