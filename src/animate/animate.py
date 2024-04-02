import json
from typing import Dict
from numpy import array, linalg, cross
from ..utils.utils import twiceLerp, lerp


def hand2Animation(recorder: str, animation: str, BPM: float, FPS: float, state_0: Dict[str, array], state_1: Dict[str, array], state_2: Dict[str, array], state_3: Dict[str, array], neck_positions: Dict[str, array]) -> None:
    """
    :params recorder: the path of the recorder file
    :params animation: the path of the file store information for animation
    :params BPM: the BPM of the music
    :params FPS: the FPS of the animation
    :params state: the state of Four key States in blender files each include hand_ik_position, hand_ik_pivot, hand_local_rotation, finger_position
    """
    hand_ik_position_p0 = state_0["hand_ik_position"]
    hand_ik_position_p1 = state_1["hand_ik_position"]
    hand_ik_position_p2 = state_2["hand_ik_position"]
    hand_ik_position_p3 = state_3["hand_ik_position"]

    hand_ik_pivot_p0 = state_0["hand_ik_pivot"]
    hand_ik_pivot_p1 = state_1["hand_ik_pivot"]
    hand_ik_pivot_p2 = state_2["hand_ik_pivot"]
    hand_ik_pivot_p3 = state_3["hand_ik_pivot"]

    hand_local_rotation_p0 = state_0["hand_local_rotation"]
    hand_local_rotation_p1 = state_1["hand_local_rotation"]
    hand_local_rotation_p2 = state_2["hand_local_rotation"]
    hand_local_rotation_p3 = state_3["hand_local_rotation"]

    finger_position_p0 = state_0["finger_position"]
    finger_position_p1 = state_1["finger_position"]
    finger_position_p2 = state_2["finger_position"]
    finger_position_p3 = state_3["finger_position"]

    neck_position_0 = neck_positions["start"]
    neck_position_12 = neck_positions["end"]

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
        fingerList = []
        barre = 0
        index_finger_string_number = 0
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

            # 记录食指位置主要是为了推算手掌的位置
            if fingerIndex == 1:
                index_finger_string_number = stringIndex

            finger_position = twiceLerp(
                finger_position_p0,
                finger_position_p1,
                finger_position_p2,
                finger_position_p3,
                fret,
                stringIndex)
            # 如果手指没有按下，那么手指位置会稍微上移
            if press == 0:
                finger_position += normal * 0.02

            fingerList.append({
                "fingerIndex": fingerIndex,
                "finger_ik_position": finger_position.tolist()
            })

        hand_ik_position = twiceLerp(
            hand_ik_position_p0,
            hand_ik_position_p1,
            hand_ik_position_p2,
            hand_ik_position_p3,
            barre,
            index_finger_string_number)

        hand_ik_pivot = twiceLerp(
            hand_ik_pivot_p0,
            hand_ik_pivot_p1,
            hand_ik_pivot_p2,
            hand_ik_pivot_p3,
            barre,
            index_finger_string_number)

        hand_local_rotation = twiceLerp(
            hand_local_rotation_p0,
            hand_local_rotation_p1,
            hand_local_rotation_p2,
            hand_local_rotation_p3,
            barre,
            index_finger_string_number)

        thumb_ik_position = lerp(neck_position_0, neck_position_12, barre)

        data_for_animation.append({
            "frame": frame,
            "hand_ik_position": hand_ik_position.tolist(),
            "hand_ik_pivot": hand_ik_pivot.tolist(),
            "hand_local_rotation": hand_local_rotation.tolist(),
            "thumb_ik_position": thumb_ik_position.tolist(),
            "fingerList": fingerList
        })

    with open(animation, "w") as f:
        json.dump(data_for_animation, f)
