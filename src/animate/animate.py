import json
from src.midi.midiToNote import calculate_frame
from numpy import array, linalg, cross, random

from ..hand.LeftFinger import PRESSSTATE
from ..hand.RightHand import caculateRightHandFingers, calculateRightPick
from ..utils.utils import get_position_by_fret


def leftHand2Animation(avatar: str, recorder: str, animation: str, tempo_changes, ticks_per_beat, FPS: float, max_string_index: int) -> None:
    """
    :params recorder: the path of the recorder file
    :params animation: the path of the file store information for animation
    :params BPM: the BPM of the music
    :params FPS: the FPS of the animation"""
    json_file = f'asset\controller_infos\{avatar}.json'
    with open(json_file, "r") as f:
        base_data = json.load(f)
    finger_position_p0 = array(base_data['LEFT_FINGER_POSITIONS']["P0"])
    finger_position_p1 = array(base_data['LEFT_FINGER_POSITIONS']["P1"])
    finger_position_p2 = array(base_data['LEFT_FINGER_POSITIONS']["P2"])

    # 这里是计算左手按弦需要保持的时间
    elapsed_frame = int(FPS / 8)

    # 计算finger_position_p0,finger_position_p1,finger_position_p2三点组成的平面上的法线值
    normal = cross(finger_position_p0 - finger_position_p1,
                   finger_position_p2 - finger_position_p1)
    normal = normal / linalg.norm(normal)

    data_for_animation = []

    with open(recorder, "r") as f:
        handDicts = json.load(f)

    for i in range(len(handDicts)):
        item = handDicts[i]
        frame = item["frame"]
        if i != len(handDicts) - 1:
            next_frame = handDicts[i + 1]["frame"]
            if next_frame > frame + elapsed_frame:
                hold_pose_frame = next_frame - elapsed_frame

        # 计算左手的动画信息
        fingerInfos = animatedLeftHand(
            base_data, item, normal, max_string_index)
        data_for_animation.append({
            "frame": frame,
            "fingerInfos": fingerInfos
        })

        # 右手会保持当前动作直到下个动作到来前两帧
        if hold_pose_frame:
            data_for_animation.append({
                "frame": hold_pose_frame,
                "fingerInfos": fingerInfos
            })

    with open(animation, "w") as f:
        json.dump(data_for_animation, f)


def animatedLeftHand(base_data: object, item: object, normal: array, max_string_index: int):
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

    for hand_data in leftHand:
        fingerIndex = hand_data["fingerIndex"]
        stringIndex = hand_data["fingerInfo"]["stringIndex"]
        fret = hand_data["fingerInfo"]["fret"]
        press = hand_data["fingerInfo"]["press"]

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
            finger_position = twiceLerpFingers(
                base_data, fret, stringIndex, max_string_index)
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
        base_data=base_data,
        hand_state=hand_state,
        value="H_L",
        valueType="position",
        fret=hand_fret,
        stringIndex=max_finger_string_index,
        max_string_index=max_string_index
    )

    # 来一个随机大小为0.0005的随机移动
    random_move = random.rand(3) * 0.001
    hand_position += random_move

    fingerInfos["H_L"] = hand_position.tolist()

    hand_IK_pivot_position = twiceLerp(
        base_data=base_data,
        hand_state=hand_state,
        value="HP_L",
        valueType="position",
        fret=hand_fret,
        stringIndex=index_finger_string_number,
        max_string_index=max_string_index
    )
    fingerInfos["HP_L"] = hand_IK_pivot_position.tolist()

    hand_rotation_y = twiceLerp(
        base_data=base_data,
        hand_state=hand_state,
        value="H_rotation_L",
        valueType="rotation",
        fret=hand_fret,
        stringIndex=index_finger_string_number,
        max_string_index=max_string_index
    )
    fingerInfos["H_rotation_L"] = hand_rotation_y.tolist()

    thumb_position = twiceLerp(
        base_data=base_data,
        hand_state=hand_state,
        value="T_L",
        valueType="position",
        fret=hand_fret,
        stringIndex=index_finger_string_number,
        max_string_index=max_string_index
    )
    fingerInfos["T_L"] = thumb_position.tolist()

    thumb_IK_pivot_position = twiceLerp(
        base_data=base_data,
        hand_state=hand_state,
        value="TP_L",
        valueType="position",
        fret=hand_fret,
        stringIndex=index_finger_string_number,
        max_string_index=max_string_index
    )
    fingerInfos["TP_L"] = thumb_IK_pivot_position.tolist()

    return fingerInfos


def rightHand2Animation(avatar: str, recorder: str, animation: str, FPS: int) -> None:
    data_for_animation = []
    # 这里是计算按弦需要保持的时间
    elapsed_frame = int(FPS / 15)
    with open(recorder, "r") as f:
        handDicts = json.load(f)
        hand_count = len(handDicts)

        for i in range(hand_count):
            data = handDicts[i]
            frame = data['frame']
            right_hand = data["rightHand"]
            if i != hand_count-1:
                next_frame = handDicts[i + 1]['frame']

            usedFingers = right_hand["usedFingers"]
            rightFingerPositions = right_hand["rightFingerPositions"]
            rightHandPosition = right_hand["rightHandPosition"]

            ready = caculateRightHandFingers(avatar,
                                             rightFingerPositions, usedFingers, rightHandPosition, isAfterPlayed=False)

            played = caculateRightHandFingers(avatar,
                                              rightFingerPositions, usedFingers, rightHandPosition, isAfterPlayed=True)
            # 触弦帧
            data_for_animation.append({
                "frame": frame,
                "fingerInfos": ready,
            })
            # 拨弦帧
            time_multiplier = 2 if usedFingers == [] else 1
            played_frame = frame + elapsed_frame * time_multiplier
            data_for_animation.append({
                "frame": played_frame,
                "fingerInfos": played,
            })
            # 拨弦后维持动作帧
            if next_frame:
                if next_frame - played_frame > elapsed_frame:
                    hold_pose_frame = next_frame - elapsed_frame
                    data_for_animation.append({
                        "frame": hold_pose_frame,
                        "fingerInfos": played,
                    })

    with open(animation, "w") as f:
        json.dump(data_for_animation, f)


def ElectronicRightHand2Animation(avatar: str, right_hand_recorder_file: str, right_hand_animation_file: str, FPS: int) -> None:
    pick_down = True
    data_for_animation = []
    # 这里是计算按弦需要保持的时间
    elapsed_frame = int(FPS / 15)

    with open(right_hand_recorder_file, "r") as f:
        handDicts = json.load(f)

        for i in range(len(handDicts)):
            data = handDicts[i]
            frame = data['frame']
            if i != len(handDicts)-1:
                next_frame = handDicts[i + 1]['frame']
                if next_frame > frame + elapsed_frame:
                    hold_pose_frame = next_frame - elapsed_frame

            strings = data["strings"]
            isArpeggio = True if len(strings) > 3 else False
            min_string = min(strings)
            max_string = max(strings)

            ready = calculateRightPick(
                avatar, max_string, pick_down, isArpeggio, isAfterPlayed=False)

            played = calculateRightPick(
                avatar, min_string, pick_down, isArpeggio, isAfterPlayed=True)

            data_for_animation.append({
                "frame": frame,
                "fingerInfos": ready
            })

            time_multiplier = 2 if len(strings) > 2 else 1
            data_for_animation.append({
                "frame": frame + elapsed_frame * time_multiplier,
                "fingerInfos": played
            })
            # 右手需要保持当前动作直到下个动作的到来之前
            if hold_pose_frame:
                data_for_animation.append({
                    "frame": hold_pose_frame,
                    "fingerInfos": played
                })

            pick_down = not pick_down

    with open(right_hand_animation_file, "w") as f:
        json.dump(data_for_animation, f, indent=4)


def twiceLerpFingers(base_data: object, fret: int, stringIndex: int, max_string_index: int) -> array:
    p0 = array(base_data['LEFT_FINGER_POSITIONS']["P0"])
    p1 = array(base_data['LEFT_FINGER_POSITIONS']["P1"])
    p2 = array(base_data['LEFT_FINGER_POSITIONS']["P2"])
    p3 = array(base_data['LEFT_FINGER_POSITIONS']["P3"])

    p_fret_0 = get_position_by_fret(fret, p0, p2)
    p_fret_1 = get_position_by_fret(fret, p1, p3)

    p_final = p_fret_0 + (p_fret_1 - p_fret_0) * stringIndex / max_string_index

    return p_final


def twiceLerp(base_data: object, hand_state: int, value: str, valueType: str, fret: int, stringIndex: int | float, max_string_index: int) -> array:
    data_dict = None

    if valueType == "position":
        data_dict = base_data['NORMAL_LEFT_HAND_POSITIONS']
        p0 = array(data_dict["P0"][value])
        p1 = array(data_dict["P1"][value])
        p2 = array(data_dict["P2"][value])
        p3 = array(data_dict["P3"][value])
    elif valueType == "rotation":
        data_dict = base_data["ROTATIONS"]['H_rotation_L']["Normal"]
        p0 = array(data_dict["P0"])
        p1 = array(data_dict["P1"])
        p2 = array(data_dict["P2"])
        p3 = array(data_dict["P3"])
    else:
        print("valueType error")

    """
    当手型不为Normal，也就是hand_state不为0时，需要进行同一个品格上Normal和另一种手型之间的插值计算，另一个手型判断的依据是:
        - 手型如果hand_state大于0就是0弦的Outer，如果hand_state小于0就是5弦的Inner
    
    不同于原有的两步插值计算，这个新的三步插值计算的顺序是:
        - 先用Outer/Inner的的手型与对应的Normal手型进行插值计算，插值的依据就是hand_state的绝对值。越倾向于0就越接近Normal手型，越倾向于5就接近其它手型
        - 用上一步计算得到的结果替换掉原本Normal手型对应的值，比如Inner会代替原来的P1和P3，Outer会代替原来的P0和P2
        - 用上一步计算得到的结果和原来没替换掉的另外两个P值一起，通过string_index和fret值，进行两次插值计算，从而得到最终的结果
    
    当然还有另外一种计算的可能性，就是：
        - 先用Normal的4个P值，先通过string_index和fret值进行两次插值计算，
        - 然后再用插值计算的结果，以及hand_state的大小，与对应的Outer或者Inner值进行插值计算
    
    第二种可能性的话，非Normal手型的权重会更大，但是没有测试过这种写法的效果，因为暂时第一种写法在动画上的表现还不错
    """
    if hand_state == 0:
        p_fret_0 = get_position_by_fret(fret, p0, p2)
        p_fret_1 = get_position_by_fret(fret, p1, p3)
        p_final = p_fret_0 + (p_fret_1 - p_fret_0) * \
            stringIndex / max_string_index
    elif hand_state > 0:
        if valueType == "position":
            outer_data_dict = base_data['OUTER_LEFT_HAND_POSITIONS']
            out_p0 = array(outer_data_dict["P0"][value])
            out_p2 = array(outer_data_dict["P2"][value])
        else:
            outer_data_dict = base_data["ROTATIONS"]['H_rotation_L']["Outer"]
            out_p0 = array(outer_data_dict["P0"])
            out_p2 = array(outer_data_dict["P2"])

        real_p0 = p0 + (out_p0 - p0) * hand_state/max_string_index
        real_p2 = p2 + (out_p2 - p2) * hand_state/max_string_index

        p_fret_0 = get_position_by_fret(fret, real_p0, real_p2)
        p_fret_1 = get_position_by_fret(fret, p1, p3)
        p_final = p_fret_0 + (p_fret_1 - p_fret_0) * \
            stringIndex / max_string_index
    else:
        if valueType == "position":
            inner_data_dict = base_data['INNER_LEFT_HAND_POSITIONS']
            inner_p1 = array(inner_data_dict["P1"][value])
            inner_p3 = array(inner_data_dict["P3"][value])
        else:
            inner_data_dict = base_data["ROTATIONS"]['H_rotation_L']["Inner"]
            inner_p1 = array(inner_data_dict["P1"])
            inner_p3 = array(inner_data_dict["P3"])

        real_P1 = p1 + (inner_p1 - p1) * abs(hand_state)/max_string_index
        real_P3 = p3 + (inner_p3 - p3) * abs(hand_state)/max_string_index

        p_fret_0 = get_position_by_fret(fret, p0, p2)
        p_fret_1 = get_position_by_fret(fret, real_P1, real_P3)
        p_final = p_fret_0 + (p_fret_1 - p_fret_0) * \
            stringIndex / max_string_index

    return p_final
