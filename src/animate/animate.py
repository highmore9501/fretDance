import json
from typing import Dict
from numpy import array, linalg, cross
from ..utils.utils import twiceLerp
from ..blender.blenderRecords import NORMAL_P1, NORMAL_P2, NORMAL_P0, NORMAL_P3, INNER_P0, INNER_P1, INNER_P2, INNER_P3, OUTER_P0, OUTER_P1, OUTER_P2, OUTER_P3


def hand2Animation(recorder: str, animation: str, BPM: float, FPS: float) -> None:
    """
    :params recorder: the path of the recorder file
    :params animation: the path of the file store information for animation
    :params BPM: the BPM of the music
    :params FPS: the FPS of the animation
    :params state: the state of Four key States in blender files each include hand_ik_position, hand_ik_pivot, hand_local_rotation, finger_position"""

    finger_position_p0 = array(NORMAL_P0["I_L"]["position"])
    finger_position_p1 = array(NORMAL_P3["I_L"]["position"])
    finger_position_p2 = array(NORMAL_P2["I_L"]["position"])
    finger_position_p3 = array(NORMAL_P3["I_L"]["position"])

    # 计算finger_position_p0,finger_position_p1,finger_position_p2三点组成的平面上的法线值
    normal = cross(finger_position_p0 - finger_position_p1,
                   finger_position_p2 - finger_position_p1)
    normal = normal / linalg.norm(normal)

    handDicts = None
    data_for_animation = []
    with open(recorder, "r") as f:
        handDicts = json.load(f)

    for item in handDicts:
        beat = item["beat"]
        time = beat / BPM * 60
        frame = time * FPS

        leftHand = item["leftHand"]
        fingerInfos = {}
        barre = 0
        index_finger_string_number = 0

        # 先遍历当前所有手指，找到第一指和第二指所在的弦位置
        index_finger_string_number = 0
        index_finger_fret_number = 0
        middle_finger_string_number = 0
        middle_finger_fret_number = 0
        for data in leftHand:
            fingerIndex = data["fingerIndex"]
            if fingerIndex == 1:
                index_finger_string_number = data["fingerInfo"]["stringIndex"]
                index_finger_fret_number = data["fingerInfo"]["fret"]
            if fingerIndex == 2:
                middle_finger_string_number = data["fingerInfo"]["stringIndex"]
                middle_finger_fret_number = data["fingerInfo"]["fret"]
        # 判断当前应该使用哪种手型来计算
        hand_state = None
        if index_finger_fret_number == middle_finger_fret_number and index_finger_fret_number != 0:
            if index_finger_string_number < middle_finger_string_number:
                hand_state = "INNER"
            else:
                hand_state = "OUTER"
        else:
            hand_state = "NORMAL"

        for data in leftHand:
            min_press_fingerIndex = 4
            fingerIndex = data["fingerIndex"]
            # skip open string. 空弦音跳过
            if fingerIndex == -1:
                continue
            stringIndex = data["fingerInfo"]["stringIndex"]
            fret = data["fingerInfo"]["fret"]
            press = data["fingerInfo"]["press"]

            # 这里是计算当前手型的把位，如果当前手型没有任何手指是按下的，那么把位不会变
            if press != 0 and fingerIndex < min_press_fingerIndex:
                min_press_fingerIndex = fingerIndex
                barre = max(fret - fingerIndex, 0)

            finger_position = twiceLerp(
                hand_state=hand_state,
                value="I_L",
                valueType="position",
                fret=fret,
                stringIndex=stringIndex)
            finger_IK_pivot_position = twiceLerp(
                hand_state=hand_state,
                value="IP_L",
                valueType="position",
                fret=fret,
                stringIndex=stringIndex)
            if fingerIndex == 1:
                position_value_name = "I_L"
                ik_position_value_name = "IP_L"
                rotation_value_name = "I_rotation_L"
            elif fingerIndex == 2:
                position_value_name = "M_L"
                ik_position_value_name = "MP_L"
                rotation_value_name = "M_rotation_L"
            elif fingerIndex == 3:
                position_value_name = "R_L"
                ik_position_value_name = "RP_L"
                rotation_value_name = "R_rotation_L"
            elif fingerIndex == 4:
                position_value_name = "P_L"
                ik_position_value_name = "PP_L"
                rotation_value_name = "P_rotation_L"

            finger_rotation = twiceLerp(
                hand_state=hand_state,
                value=rotation_value_name,
                valueType="rotation",
                fret=fret,
                stringIndex=stringIndex)

            # 如果手指没有按下，那么手指位置会稍微上移
            if press == 0:
                finger_position += normal * 0.02

            fingerInfos[position_value_name] = finger_position.tolist()
            fingerInfos[ik_position_value_name] = finger_IK_pivot_position.tolist()
            fingerInfos[rotation_value_name] = finger_rotation.tolist()

        hand_position = twiceLerp(
            hand_state=hand_state,
            value="H_L",
            valueType="position",
            fret=barre,
            stringIndex=index_finger_string_number)

        fingerInfos["H_L"] = hand_position.tolist()

        hand_IK_pivot_position = twiceLerp(
            hand_state=hand_state,
            value="HP_L",
            valueType="position",
            fret=barre,
            stringIndex=index_finger_string_number)
        fingerInfos["HP_L"] = hand_IK_pivot_position.tolist()

        hand_rotation_y = twiceLerp(
            hand_state=hand_state,
            value="H_rotation_Y_L",
            valueType="rotation",
            fret=barre,
            stringIndex=index_finger_string_number)
        fingerInfos["H_rotation_Y_L"] = hand_rotation_y.tolist()

        thumb_position = twiceLerp(
            hand_state=hand_state,
            value="T_L",
            valueType="position",
            fret=barre,
            stringIndex=index_finger_string_number)
        fingerInfos["T_L"] = thumb_position.tolist()

        thumb_IK_pivot_position = twiceLerp(
            hand_state=hand_state,
            value="TP_L",
            valueType="position",
            fret=barre,
            stringIndex=index_finger_string_number
        )
        fingerInfos["TP_L"] = thumb_IK_pivot_position.tolist()

        thumb_rotation = twiceLerp(
            hand_state=hand_state,
            value="T_rotation_L",
            valueType="rotation",
            fret=barre,
            stringIndex=index_finger_string_number)
        fingerInfos["T_rotation_L"] = thumb_rotation.tolist()

        data_for_animation.append({
            "frame": frame,
            "fingerInfos": fingerInfos
        })

    with open(animation, "w") as f:
        json.dump(data_for_animation, f)
