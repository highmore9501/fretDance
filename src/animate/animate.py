import json
from numpy import array, linalg, cross
from ..utils.utils import twiceLerp
from ..blender.blenderRecords import NORMAL_P2, NORMAL_P0, NORMAL_P3
from ..hand.LeftFinger import PRESSSTATE


def hand2Animation(recorder: str, animation: str, FPS: float) -> None:
    """
    :params recorder: the path of the recorder file
    :params animation: the path of the file store information for animation
    :params BPM: the BPM of the music
    :params FPS: the FPS of the animation"""

    finger_position_p0 = array(NORMAL_P0["I_L"]["position"])
    finger_position_p1 = array(NORMAL_P3["I_L"]["position"])
    finger_position_p2 = array(NORMAL_P2["I_L"]["position"])

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
        next_time = None
        if i != len(handDicts) - 1:
            next_item = handDicts[i + 1]
            next_time = next_item["real_time"]
        real_time = item["real_time"]
        frame = real_time * FPS

        leftHand = item["leftHand"]
        fingerInfos = {}
        barre = 1
        max_finger_string_index = 0
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
            if press == PRESSSTATE['Open']:
                stringIndex -= 0.5

            max_finger_string_index = max(max_finger_string_index, stringIndex)

            # 这里是计算当前手型的把位，如果当前手型没有任何手指是按下的，那么把位不会变
            if press != 0 and fingerIndex < min_press_fingerIndex:
                min_press_fingerIndex = fingerIndex
                barre = max(fret - fingerIndex+1, 1)

            if fingerIndex == 1:
                position_value_name = "I_L"
            elif fingerIndex == 2:
                position_value_name = "M_L"
            elif fingerIndex == 3:
                position_value_name = "R_L"
            elif fingerIndex == 4:
                position_value_name = "P_L"

            finger_position = twiceLerp(
                hand_state=hand_state,
                value=position_value_name,
                valueType="position",
                fret=fret,
                stringIndex=stringIndex)

            # 如果手指没有按下，那么手指位置会稍微上移
            if press == PRESSSTATE['Open']:
                finger_position -= normal * 0.007

            fingerInfos[position_value_name] = finger_position.tolist()

        hand_position = twiceLerp(
            hand_state=hand_state,
            value="H_L",
            valueType="position",
            fret=barre,
            stringIndex=max_finger_string_index)

        fingerInfos["H_L"] = hand_position.tolist()

        hand_IK_pivot_position = twiceLerp(
            hand_state=hand_state,
            value="HP_L",
            valueType="position",
            fret=barre,
            stringIndex=index_finger_string_number)
        fingerInfos["HP_L"] = hand_IK_pivot_position.tolist()

        thumb_ik_pivot_bone_position = twiceLerp(
            hand_state=hand_state,
            value="Thumb_IK_pivot_L",
            valueType="position",
            fret=barre,
            stringIndex=index_finger_string_number)
        fingerInfos["Thumb_IK_pivot_L"] = thumb_ik_pivot_bone_position.tolist()

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
            stringIndex=index_finger_string_number)
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

        if next_time:
            next_frame = next_time * FPS
            if frame + 2 < next_frame:
                data_for_animation.append({
                    "frame": next_frame-2,
                    "fingerInfos": fingerInfos
                })

    with open(animation, "w") as f:
        json.dump(data_for_animation, f)
