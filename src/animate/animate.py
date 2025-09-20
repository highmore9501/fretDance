import json
import numpy as np
from numpy import array, linalg, cross
from ..hand.LeftFinger import PRESSSTATE
from ..hand.RightHand import caculateRightHandFingers, calculateRightPick
from ..utils.utils import lerp_by_fret, slerp
from typing import Any


def leftHand2Animation(avatar: str, recorder: str, animation_json_path: str, FPS: float, max_string_index: int, disable_barre: bool = True) -> None:
    """
    :params recorder: the path of the recorder file
    :params animation_json_path: the path of the file store information for animation
    :params BPM: the BPM of the music
    :params FPS: the FPS of the animation"""
    json_file = f'asset\\controller_infos\\{avatar}.json'
    with open(json_file, "r") as f:
        avatar_data = json.load(f)
    finger_position_p0 = array(avatar_data['LEFT_FINGER_POSITIONS']["P0"])
    finger_position_p1 = array(avatar_data['LEFT_FINGER_POSITIONS']["P1"])
    finger_position_p2 = array(avatar_data['LEFT_FINGER_POSITIONS']["P2"])

    # 这是人物按下弦需要的时间，还是挺快的
    press_duration = FPS / 16
    # 这个就是两个不同姿势之间切换时需要的帧数
    elapsed_frame = press_duration * 3
    # 这是手指从按弦变成松开需要的帧数
    finger_return_to_rest_frame = press_duration * 1.2

    # p0和p1的距离
    p0_p1_distance = linalg.norm(finger_position_p0 - finger_position_p1)
    # 按弦接下的距离直接取p0和p1距离的1/5
    press_distance = p0_p1_distance / 5

    # 计算finger_position_p0,finger_position_p1,finger_position_p2三点组成的平面上的法线值
    normal = cross(finger_position_p0 - finger_position_p1,
                   finger_position_p2 - finger_position_p1)
    normal = normal / linalg.norm(normal)

    data_for_animation = []

    with open(recorder, "r") as f:
        handDicts = json.load(f)

    # 初始化状态
    init_state = None

    for i in range(len(handDicts)):
        item = handDicts[i]
        frame = item["frame"]
        pitchwheel = item.get("pitchwheel", 0)

        # 计算当前帧的动画信息（beat状态）
        current_finger_infos = animatedLeftHand(
            avatar_data, item, normal, max_string_index, pitchwheel, rest_finger_distance=press_distance, disable_barre=disable_barre)

        # 获取需要抬指的手指索引集合
        finger_index_set_need_to_change = set()

        # 初始化下一帧信息
        next_frame = None
        next_finger_infos = None

        # 如果不是最后一帧，获取下一帧信息
        if i != len(handDicts) - 1:
            next_frame = handDicts[i + 1]["frame"]
            next_pitchwheel = handDicts[i + 1].get("pitchwheel", 0)
            next_finger_infos = animatedLeftHand(
                avatar_data, handDicts[i + 1], normal, max_string_index, next_pitchwheel, rest_finger_distance=press_distance, disable_barre=disable_barre)

            # 对比当前手势和下一个手势，找出来姿势切换时需要抬指的手指
            current_hand = item["leftHand"]
            current_finger_dict = {
                finger['fingerIndex']: finger['fingerInfo'] for finger in current_hand}

            next_hand = handDicts[i + 1]["leftHand"]
            next_finger_dict = {
                finger['fingerIndex']: finger['fingerInfo'] for finger in next_hand}

            for finger_index in range(1, 5):
                current_finger = current_finger_dict.get(finger_index)
                next_finger = next_finger_dict.get(finger_index)
                # 如果一个手指当前是按弦状态，而下一个状态换弦了，就需要有抬指的动作（换品可以不抬指直接滑过去）
                if current_finger and next_finger and \
                   current_finger['press'] != 0 and \
                   current_finger['stringIndex'] != next_finger['stringIndex']:
                    finger_index_set_need_to_change.add(finger_index)

        # 第一帧需要添加初始状态
        if i == 0:
            # 创建初始状态（所有手指处于休息状态）
            init_state = create_init_state(
                avatar_data, item, normal, max_string_index, pitchwheel, press_distance, disable_barre)
            data_for_animation.append({
                "frame": 0,
                "fingerInfos": init_state,
                "pitchwheel": 0
            })

        # 添加当前帧（beat状态）
        data_for_animation.append({
            "frame": frame,
            "fingerInfos": current_finger_infos,
            "pitchwheel": pitchwheel
        })

        # 插入中间帧
        frames_to_insert = interpolate_left_hand_frames(
            current_frame=frame,
            next_frame=next_frame,
            current_beat_state=current_finger_infos,
            next_ready_state=next_finger_infos,
            finger_index_set_need_to_change=finger_index_set_need_to_change,
            normal=normal,
            press_distance=press_distance,
            press_duration=press_duration,
            action_duration=elapsed_frame,
            rest_duration=finger_return_to_rest_frame,
            is_first_action=(i == 0),
            init_state=init_state,
            pitchwheel=pitchwheel,
            next_pitchwheel=handDicts[i +
                                      1].get("pitchwheel", 0) if i != len(handDicts) - 1 else 0
        )

        # 将插值帧添加到动画数据中
        for frame_data in frames_to_insert:
            data_for_animation.append(frame_data)

    with open(animation_json_path, "w") as f:
        json.dump(data_for_animation, f)


def create_init_state(avatar_data, item, normal, max_string_index, pitchwheel, press_distance, disable_barre):
    """创建初始状态（所有手指处于休息位置）"""
    # 复制当前状态作为基础
    init_finger_infos = animatedLeftHand(
        avatar_data, item, normal, max_string_index, pitchwheel, rest_finger_distance=press_distance, disable_barre=disable_barre)

    # 将所有手指移动到休息位置
    left_finger_index_dict = {
        1: "I_L",
        2: "M_L",
        3: "R_L",
        4: "P_L"
    }

    for finger_index in range(1, 5):
        controller_name = left_finger_index_dict[finger_index]
        current_position = array(init_finger_infos[controller_name])
        # 手指休息时比按弦时抬高一些
        if finger_index == 4:  # 小拇指抬得更高
            new_position = current_position - 2 * normal * press_distance
        else:
            new_position = current_position - normal * press_distance
        init_finger_infos[controller_name] = new_position.tolist()

    # 休息状态的手可以往后一点点位置
    current_H_position = array(init_finger_infos["H_L"])
    random_vector = np.random.rand(3)
    random_vector = random_vector / np.linalg.norm(random_vector)
    current_H_position += random_vector * press_distance * 0.5
    init_finger_infos["H_L"] = current_H_position.tolist()

    return init_finger_infos


def interpolate_left_hand_frames(current_frame, next_frame, current_beat_state, next_ready_state,
                                 finger_index_set_need_to_change, normal, press_distance, press_duration, action_duration, rest_duration,
                                 is_first_action, init_state, pitchwheel, next_pitchwheel):
    """根据通用插帧逻辑生成左手动画帧"""
    frames_to_insert = []

    # 处理第一个动作的特殊情况
    if is_first_action:
        # 在当前帧前action_duration的位置插入当前动作的预备状态
        ready_time = current_frame - action_duration - press_duration
        if ready_time >= 0:
            frames_to_insert.append({
                "frame": ready_time,
                "fingerInfos": init_state,
                "pitchwheel": pitchwheel
            })

    # 如果没有下一个动作帧，仅插入当前动作的beat状态，以示保持
    if next_frame is None:
        rest_time = current_frame + rest_duration
        # 创建rest状态（抬指状态）
        rest_state = create_rest_state(
            current_beat_state, press_distance, finger_index_set_need_to_change, normal)
        frames_to_insert.append({
            "frame": rest_time,
            "fingerInfos": current_beat_state,
            "pitchwheel": pitchwheel
        })
        return frames_to_insert

    # 获取当前和下一个动作帧的时间戳
    current_time = current_frame
    next_time = next_frame
    T = next_time - current_time  # 可用时间

    # 情况1: 时间足够插入所有状态（保持结束、回弹结束、预备状态）
    if T >= rest_duration + action_duration+press_duration:
        # 创建rest状态（抬指状态）
        rest_state = create_rest_state(
            current_beat_state, press_distance, finger_index_set_need_to_change, normal)

        rest_start_time = next_time - press_duration - action_duration-rest_duration
        rest_end_time = next_time - press_duration - action_duration
        ready_time = next_time - press_duration

        # 插入beat状态持续结束时的帧
        frames_to_insert.append({
            "frame": rest_start_time,
            "fingerInfos": current_beat_state,
            "pitchwheel": pitchwheel
        })

        # 插入进入到rest状态的帧，注意rest不用保持，也就是达到rest状态以后就可以开始移动了
        frames_to_insert.append({
            "frame": rest_end_time,
            "fingerInfos": rest_state,
            "pitchwheel": pitchwheel
        })

        # 插入下一个动作的ready帧
        frames_to_insert.append({
            "frame": ready_time,
            "fingerInfos": next_ready_state,
            "pitchwheel": next_pitchwheel
        })

    # 情况2: 时间不够插入所有状态，但足够插入预备状态和移动过程，所以可以去掉保持beat状态的帧，也就是按完立马开始抬指
    elif T >= action_duration+press_duration:
        ready_time = next_time - press_duration
        rest_end_time = next_time - press_duration - action_duration

        # 创建rest状态（抬指状态）
        rest_state = create_rest_state(
            current_beat_state, press_distance, finger_index_set_need_to_change, normal)
        frames_to_insert.append({
            "frame": rest_end_time,
            "fingerInfos": rest_state,
            "pitchwheel": pitchwheel
        })
        frames_to_insert.append({
            "frame": ready_time,
            "fingerInfos": next_ready_state,
            "pitchwheel": next_pitchwheel
        })
    elif T >= press_duration:
        # 时间只够插入预备状态，所以还是要填入预备状态的
        ready_time = next_time - press_duration

        frames_to_insert.append({
            "frame": ready_time,
            "fingerInfos": next_ready_state,
            "pitchwheel": next_pitchwheel
        })
    # 情况3: 时间连插入预备状态都不够，只保留当前动作帧
    else:
        print(f'当前动作帧{current_frame}与下一帧{next_frame}之间时间不足，没有插入任何中间状态！')

    return frames_to_insert


def create_rest_state(beat_state, press_distance, finger_index_set_need_to_change, normal):
    """创建手指抬高的休息状态"""
    # 复制当前状态
    rest_state = beat_state.copy()

    left_finger_index_dict = {
        1: "I_L",
        2: "M_L",
        3: "R_L",
        4: "P_L"
    }

    # 抬高需要改变的手指
    for rest_finger_index in list(finger_index_set_need_to_change):
        controller_name = left_finger_index_dict[rest_finger_index]
        current_position = array(rest_state[controller_name])
        # 小拇指休息时比其它手指抬得要高一点
        if rest_finger_index == 4:
            new_position = current_position - 2 * normal * press_distance
        else:
            new_position = current_position - normal * press_distance
        rest_state[controller_name] = new_position.tolist()

    # rest状态的手随机动一点
    current_H_Position = array(rest_state['H_L'])
    random_vector = np.random.rand(3)
    random_vector = random_vector / np.linalg.norm(random_vector)
    current_H_Position += random_vector * press_distance * 0.25
    rest_state['H_L'] = current_H_Position.tolist()

    return rest_state


def addPitchwheel(left_hand_recorder_file: str, pitch_wheel_map: list):
    with open(left_hand_recorder_file, "r") as f:
        data = json.load(f)
        total_itmes = len(data)

        new_data = []

        for i in range(total_itmes):
            new_item = data[i]
            new_item['pitchwheel'] = 0
            new_data.append(new_item)

            if i != total_itmes - 1:
                recorder_tick = data[i]["real_tick"]
                next_tick = data[i + 1]["real_tick"]

                for pitch_wheel_item in pitch_wheel_map:
                    tick = pitch_wheel_item['real_tick']
                    if recorder_tick <= tick <= next_tick:
                        insert_item = new_item.copy()
                        insert_item['real_tick'] = tick
                        insert_item['frame'] = pitch_wheel_item['frame']
                        insert_item['pitchwheel'] = pitch_wheel_item['pitchwheel']
                        new_data.append(insert_item)

        with open(left_hand_recorder_file, "w") as f:
            json.dump(new_data, f, indent=4)


def animatedLeftHand(avatar_data: object, item: Any, normal: np.ndarray, max_string_index: int, pitchwheel: int, rest_finger_distance, disable_barre: bool = False):
    leftHand = item["leftHand"]
    hand_fret = item["hand_position"]
    use_barre = item.get("use_barre", False) and not disable_barre

    fingerInfos = {}
    barre_finger_string_index = 0
    index_finger_string_number = 0

    # 用于统计每个手指都在哪根弦上的dict
    finger_string_numbers = {
        1: 0,
        2: 0,
        3: 0,
        4: 0
    }

    # --开始计算手指信息--
    for finger_data in leftHand:
        fingerIndex = finger_data["fingerIndex"]
        stringIndex = finger_data["fingerInfo"]["stringIndex"]
        fret = finger_data["fingerInfo"]["fret"]
        press = finger_data["fingerInfo"]["press"]

        # skip open string. 空弦音跳过
        if fingerIndex == -1:
            continue

        # 不按弦的手指会稍微移动，以避免和按弦的手指挤在一起
        if press == PRESSSTATE['Open']:
            if stringIndex > 2:
                stringIndex -= 0.5
            else:
                stringIndex += 0.5

        # 按弦的手指考虑是否有pitchWheel，以进行对应的移动
        if press == PRESSSTATE['Pressed'] and pitchwheel != 0:
            pitch_move = pitchwheel / 8192
            if stringIndex > 2:
                stringIndex -= pitch_move
            else:
                stringIndex += pitch_move

        # 手指的横按与非横按使用两套不同的计算方式
        if use_barre and fingerIndex == 1:
            finger_position = twiceLerpBarreFingers(
                avatar_data, fret, stringIndex, max_string_index)
            position_value_name = "I_L"
            barre_finger_string_index = stringIndex
        else:
            finger_string_numbers[fingerIndex] = stringIndex
            finger_position = twiceLerpFingers(
                avatar_data, fret, stringIndex, max_string_index)
            # 如果手指没有按下，那么手指位置会稍微上移
            if press == PRESSSTATE['Open']:
                # 小拇指就是抬得高一些
                if fingerIndex == 4:
                    finger_position -= 2 * normal * rest_finger_distance
                else:
                    finger_position -= normal * rest_finger_distance

            if fingerIndex == 1:
                position_value_name = "I_L"
            elif fingerIndex == 2:
                position_value_name = "M_L"
            elif fingerIndex == 3:
                position_value_name = "R_L"
            elif fingerIndex == 4:
                position_value_name = "P_L"
            else:
                position_value_name = "None"

        fingerInfos[position_value_name] = finger_position.tolist()

    # 判断当前应该使用哪种手型来计算
    index_finger_string_number = finger_string_numbers[1]
    pinky_finger_string_number = finger_string_numbers[4]
    hand_state = pinky_finger_string_number - index_finger_string_number

    # --计算手位置--
    if use_barre:
        hand_position = twiceLerpBarreHand(
            avatar_data=avatar_data,
            value="H_L",
            valueType="position",
            fret=hand_fret,
            stringIndex=barre_finger_string_index,
            max_string_index=max_string_index
        )
    else:
        hand_position = twiceLerp(
            avatar_data=avatar_data,
            hand_state=hand_state,
            value="H_L",
            valueType="position",
            fret=hand_fret,
            stringIndex=index_finger_string_number,
            max_string_index=max_string_index
        )

    fingerInfos["H_L"] = hand_position.tolist()

    # --计算手臂IK，手旋转，大拇指位置，IK--
    if use_barre:
        hand_IK_pivot_position = twiceLerpBarreHand(
            avatar_data=avatar_data,
            value="HP_L",
            valueType="position",
            fret=hand_fret,
            stringIndex=barre_finger_string_index,
            max_string_index=max_string_index
        )
        hand_rotation_l = twiceLerpBarreHand(
            avatar_data=avatar_data,
            value="H_rotation_L",
            valueType="rotation",
            fret=hand_fret,
            stringIndex=barre_finger_string_index,
            max_string_index=max_string_index
        )
        thumb_position = twiceLerpBarreHand(
            avatar_data=avatar_data,
            value="T_L",
            valueType="position",
            fret=hand_fret,
            stringIndex=barre_finger_string_index,
            max_string_index=max_string_index
        )
        thumb_IK_pivot_position = twiceLerpBarreHand(
            avatar_data=avatar_data,
            value="TP_L",
            valueType="position",
            fret=hand_fret,
            stringIndex=barre_finger_string_index,
            max_string_index=max_string_index
        )
    else:
        hand_IK_pivot_position = twiceLerp(
            avatar_data=avatar_data,
            hand_state=hand_state,
            value="HP_L",
            valueType="position",
            fret=hand_fret,
            stringIndex=index_finger_string_number,
            max_string_index=max_string_index
        )
        hand_rotation_l = twiceLerp(
            avatar_data=avatar_data,
            hand_state=hand_state,
            value="H_rotation_L",
            valueType="rotation",
            fret=hand_fret,
            stringIndex=index_finger_string_number,
            max_string_index=max_string_index
        )
        thumb_position = twiceLerp(
            avatar_data=avatar_data,
            hand_state=hand_state,
            value="T_L",
            valueType="position",
            fret=hand_fret,
            stringIndex=index_finger_string_number,
            max_string_index=max_string_index
        )
        thumb_IK_pivot_position = twiceLerp(
            avatar_data=avatar_data,
            hand_state=hand_state,
            value="TP_L",
            valueType="position",
            fret=hand_fret,
            stringIndex=index_finger_string_number,
            max_string_index=max_string_index
        )

    fingerInfos["HP_L"] = hand_IK_pivot_position.tolist()
    fingerInfos["H_rotation_L"] = hand_rotation_l.tolist()
    fingerInfos["T_L"] = thumb_position.tolist()
    fingerInfos["TP_L"] = thumb_IK_pivot_position.tolist()

    return fingerInfos


def rightHand2Animation(avatar: str, recorder: str, animation: str, FPS: int, max_string_index: int) -> None:
    data_for_animation = []
    # 这里是计算按弦需要保持的时间
    elapsed_frame = int(FPS / 15)
    json_file = f'asset/controller_infos/{avatar}.json'
    with open(json_file, 'r') as f:
        avatar_data = json.load(f)
        if not avatar_data:
            raise Exception("avatar_data is empty")

    with open(recorder, "r") as f:
        handDicts = json.load(f)
        hand_count = len(handDicts)

        for i in range(hand_count):
            data = handDicts[i]
            frame = data['frame']
            right_hand = data["rightHand"]
            usedFingers = right_hand["usedFingers"]
            rightFingerPositions = right_hand["rightFingerPositions"]

            # 这个usedFingers为空，表示是扫弦，所以播放时间要长一些
            time_multiplier = 2 if usedFingers == [] else 1
            played_frame = frame + elapsed_frame * time_multiplier

            played_finished_frame = None
            if i != hand_count-1:
                next_frame = handDicts[i + 1]['frame']
                if next_frame > played_frame + 2*elapsed_frame:  # 这个2 * elapsed_frame 相当于留给手掌移动到下一个位置的时间
                    played_finished_frame = next_frame - 2 * elapsed_frame

            ready = caculateRightHandFingers(avatar_data,
                                             rightFingerPositions, usedFingers, max_string_index, isAfterPlayed=False)

            played = caculateRightHandFingers(avatar_data,
                                              rightFingerPositions, usedFingers, max_string_index, isAfterPlayed=True)

            # 右手拨弦分为四个阶段，准备拨弦，拨弦，拨弦后维持动作，返回准备状态。
            # 如果与下一个音符之间的间隔足够长，就需要把这些动作都记录下来

            # 触弦帧
            data_for_animation.append({
                "frame": frame,
                "fingerInfos": ready,
            })
            data_for_animation.append({
                "frame": played_frame,
                "fingerInfos": played,
            })
            # 拨弦后慢慢弹回来
            if played_finished_frame is not None:
                data_for_animation.append({
                    "frame": played_finished_frame,
                    "fingerInfos": ready,
                })

    with open(animation, "w") as f:
        json.dump(data_for_animation, f)


def ElectronicRightHand2Animation(avatar: str, right_hand_recorder_file: str, right_hand_animation_file: str, FPS: int, guitar_max_string_index: int = 5) -> None:
    pick_position = 5.5
    data_for_animation = []
    # 这里是计算拨弦需要保持的时间
    elapsed_frame = FPS / 15.0

    with open(right_hand_recorder_file, "r") as f:
        handDicts = json.load(f)

        for i in range(len(handDicts)):
            data = handDicts[i]
            frame = data['frame']
            strings = data["strings"]
            isArpeggio = True if len(strings) > 3 else False
            min_string = min(strings)
            max_string = max(strings)
            time_multiplier = 2 if len(strings) > 2 else 1
            played_frame = frame + elapsed_frame * time_multiplier

            played_finished_frame = None
            if i < len(handDicts)-1:
                next_frame = handDicts[i + 1]['frame']
                if next_frame > played_frame + elapsed_frame:
                    played_finished_frame = played_frame + elapsed_frame

            # 如果pick当前的位置是在最低弦下面，那么以最低弦为演奏弦并且上扫弦
            # 如果pick当前的位置是在最高弦上面，那么以最高弦为演奏弦并且下扫弦
            pick_on_low_position = pick_position < min_string
            start_string = min_string if pick_on_low_position else max_string
            end_string = max_string if pick_on_low_position else min_string
            should_start_at_lower_position = pick_on_low_position
            should_end_at_lower_position = not pick_on_low_position

            ready = calculateRightPick(
                avatar, start_string, isArpeggio, should_start_at_lower_position, guitar_max_string_index)

            played = calculateRightPick(
                avatar, end_string, isArpeggio, should_end_at_lower_position, guitar_max_string_index)

            if isArpeggio and should_end_at_lower_position:
                pick_position = -0.5
            else:
                pick_position = end_string + 0.5 if should_end_at_lower_position else end_string - 0.5

            # pick拨弦分为三个阶段，准备拨弦，拨弦，拨弦后维持动作。它没有再返回准备状态的必要。
            data_for_animation.append({
                "frame": frame,
                "fingerInfos": ready
            })

            data_for_animation.append({
                "frame": played_frame,
                "fingerInfos": played
            })

            if played_finished_frame is not None:
                data_for_animation.append({
                    "frame": played_finished_frame,
                    "fingerInfos": played
                })

    with open(right_hand_animation_file, "w") as f:
        json.dump(data_for_animation, f, indent=4)


def twiceLerpFingers(avatar_data: Any, fret: float, stringIndex: int, max_string_index: int) -> np.ndarray:
    p0 = array(avatar_data['LEFT_FINGER_POSITIONS']["P0"])
    p1 = array(avatar_data['LEFT_FINGER_POSITIONS']["P1"])
    p2 = array(avatar_data['LEFT_FINGER_POSITIONS']["P2"])
    p3 = array(avatar_data['LEFT_FINGER_POSITIONS']["P3"])

    p_fret_0 = lerp_by_fret(fret, p0, p2)
    p_fret_1 = lerp_by_fret(fret, p1, p3)

    p_final = p_fret_0 + (p_fret_1 - p_fret_0) * stringIndex / max_string_index

    return p_final


def twiceLerpBarreFingers(avatar_data: Any, fret: float, finger_string_index: int, max_string_index: int) -> np.ndarray:
    barre_p0 = array(avatar_data['BARRE_LEFT_HAND_POSITIONS']["P0"]["I_L"])
    barre_p1 = array(avatar_data['BARRE_LEFT_HAND_POSITIONS']["P1"]["I_L"])
    barre_p2 = array(avatar_data['BARRE_LEFT_HAND_POSITIONS']["P2"]["I_L"])
    barre_p3 = array(avatar_data['BARRE_LEFT_HAND_POSITIONS']["P3"]["I_L"])

    p_fret_0 = lerp_by_fret(fret, barre_p0, barre_p2)
    p_fret_1 = lerp_by_fret(fret, barre_p1, barre_p3)

    # 使用clamp后的值进行计算
    p_final = p_fret_0 + (p_fret_1 - p_fret_0) * \
        (finger_string_index - 2) / (max_string_index - 2)

    return p_final


def twiceLerp(avatar_data: Any, hand_state: int, value: str, valueType: str, fret: float, stringIndex: int | float, max_string_index: int) -> np.ndarray:
    data_dict = None

    """
    这个函数实现了两层插值计算：
    1. 首先在相同手型内，根据品格(fret)进行插值计算 (1品到12品之间)
    2. 然后根据hand_state的值，计算出一个hand_weight参数，它代表当前手型在Outer/Inner手型与Normal手型之间的权重。
    3. 根据食指所在的弦索引，计算出一个string_weight参数，它代表同一品格，但是在P01-P03手型之间的权重。
    
    hand_state的含义：
    - hand_state = 0: 说明食指与小拇指在同一根弦上，意味着可以使用Normal手型进行计算。这时候会先用P0和P2、P1和P3进行品格插值;再将品格插值得到的两个结果使用弦索引进行插值，得到最终结果。
    - hand_state > 0: 说明小拇指的弦索引比食指的弦索引大。这时候可以先计算出该品格上的P02_normal和P13_normal两个Normal手型，再计算出该品格上的P02_Outer手型。先用P02上的两个手型用hand_weight进行插值，再用P02插值的结果与P13的结果用string_weight进行插值，得到最终结果。
    - hand_state < 0: 说明小拇指的弦索引比食指的弦索引小。这时候可以先计算出该品格上的P02_normal和P13_normal两个Normal手型，再计算出该品格上的P13_Inner手型。先用P02上的两个手型用hand_weight进行插值，再用P02插值结果与P13的结果用string_weight进行插值，得到最终结果。
    
    参数：
    - avatar_data: 模型数据字典

    - hand_state > 0: 在Outer和Normal手型之间插值，插值权重为 hand_weight
    - hand_state < 0: 在Normal和Inner手型之间插值，插值权重为 hand_weight   
    """
    normal_rotation_is_quaternion = False
    # 这个值其实相当于食指的索引除以最大弦的索引，它与hand_state一起，可以表达出当前手型的食指和小拇指的弦索引，并且可以在三种不同手型中进行插值计算
    string_weight = stringIndex / max_string_index
    hand_weight = abs(hand_state/max_string_index)

    if valueType == "position":
        data_dict = avatar_data['NORMAL_LEFT_HAND_POSITIONS']
        p0 = array(data_dict["P0"][value])
        p1 = array(data_dict["P1"][value])
        p2 = array(data_dict["P2"][value])
        p3 = array(data_dict["P3"][value])
    else:
        data_dict = avatar_data["ROTATIONS"]['H_rotation_L']["Normal"]
        p0 = array(data_dict["P0"])
        p1 = array(data_dict["P1"])
        p2 = array(data_dict["P2"])
        p3 = array(data_dict["P3"])

        # 检查是否为四元数（长度为4）或欧拉角（长度为3）
        normal_rotation_is_quaternion = len(p0) == 4

    p_normal_fret_02 = lerp_by_fret(fret, p0, p2)
    p_normal_fret_13 = lerp_by_fret(fret, p1, p3)

    if hand_state == 0:
        if normal_rotation_is_quaternion:
            p_final = slerp(p_normal_fret_02, p_normal_fret_13, string_weight)
        else:
            # 其它情况无论是位置还是旋转值，都使用常规的线性插值
            p_final = p_normal_fret_02 + \
                (p_normal_fret_13 - p_normal_fret_02) * string_weight
    elif hand_state > 0:
        outer_rotation_is_quaternion = False
        if valueType == "position":
            outer_data_dict = avatar_data['OUTER_LEFT_HAND_POSITIONS']
            out_p0 = array(outer_data_dict["P0"][value])
            out_p2 = array(outer_data_dict["P2"][value])
        else:
            outer_data_dict = avatar_data["ROTATIONS"]['H_rotation_L']["Outer"]
            out_p0 = array(outer_data_dict["P0"])
            out_p2 = array(outer_data_dict["P2"])
            # 检查是否为四元数
            outer_rotation_is_quaternion = len(out_p0) == 4

        # 这个变量的后缀0，表示的是在0-2两个位置中进行品格插值以后，得到的结果，当然直接后缀写成零不太优雅，但姑且先这样写
        p_outer = lerp_by_fret(fret, out_p0, out_p2)

        if outer_rotation_is_quaternion:
            # 四元数插值
            p_normal = slerp(p_normal_fret_02, p_normal_fret_13, string_weight)
            p_final = slerp(p_normal, p_outer, hand_weight)
        else:
            p_normal = p_normal_fret_02 + \
                (p_normal_fret_13 - p_normal_fret_02) * string_weight
            p_final = p_normal + \
                (p_outer - p_normal) * hand_weight
    else:
        inner_rotation_is_quaternion = False
        if valueType == "position":
            inner_data_dict = avatar_data['INNER_LEFT_HAND_POSITIONS']
            inner_p1 = array(inner_data_dict["P1"][value])
            inner_p3 = array(inner_data_dict["P3"][value])
        else:
            inner_data_dict = avatar_data["ROTATIONS"]['H_rotation_L']["Inner"]
            inner_p1 = array(inner_data_dict["P1"])
            inner_p3 = array(inner_data_dict["P3"])

            # 检查是否为四元数
            inner_rotation_is_quaternion = len(inner_p1) == 4
        # 这个后缀1，是在1-3位置之间进行品格插值以后得到的结果，后缀姑且先写1
        p_inner = lerp_by_fret(fret, inner_p1, inner_p3)

        if inner_rotation_is_quaternion:
            # 四元数插值
            p_normal = slerp(p_normal_fret_02, p_normal_fret_13, string_weight)
            p_final = slerp(p_normal, p_inner, hand_weight)
        else:
            # 标准线性插值
            p_normal = p_normal_fret_02 + \
                (p_normal_fret_13 - p_normal_fret_02) * string_weight
            p_final = p_normal + \
                (p_inner - p_normal) * hand_weight

    return p_final


def twiceLerpBarreHand(
    avatar_data,
    value,
    valueType,
    fret,
    stringIndex,
    max_string_index
):
    data_dict = None
    barre_rotation_is_quaternion = False
    string_weight = (stringIndex-2) / (max_string_index-2)

    if valueType == "position":
        data_dict = avatar_data['BARRE_LEFT_HAND_POSITIONS']
        p0 = array(data_dict["P0"][value])
        p1 = array(data_dict["P1"][value])
        p2 = array(data_dict["P2"][value])
        p3 = array(data_dict["P3"][value])
        if p0 is None or p1 is None or p2 is None or p3 is None or \
                not p0.size or not p1.size or not p2.size or not p3.size:
            raise ValueError(f"Invalid position data:{value}")
    elif valueType == "rotation":
        data_dict = avatar_data["ROTATIONS"]['H_rotation_L']["Barre"]
        p0 = array(data_dict["P0"])
        p1 = array(data_dict["P1"])
        p2 = array(data_dict["P2"])
        p3 = array(data_dict["P3"])

        # 检查是否为四元数（长度为4）或欧拉角（长度为3）
        barre_rotation_is_quaternion = len(p0) == 4
    else:
        raise ValueError("Invalid value type")

    p_fret_02 = lerp_by_fret(fret, p0, p2)
    p_fret_13 = lerp_by_fret(fret, p1, p3)
    if barre_rotation_is_quaternion:
        p_final = slerp(p_fret_02, p_fret_13, string_weight)
    else:
        p_final = p_fret_02 + (p_fret_13 - p_fret_02) * \
            (stringIndex-2) / (max_string_index-2)

    return p_final


def animated_guitar_string(left_recorder: str, string_recorder: str, FPS: int) -> None:
    elapsed_frame = FPS / 8.0
    with open(left_recorder, "r") as f:
        handDicts = json.load(f)

    data_for_animation = []

    for i in range(len(handDicts)):
        item = handDicts[i]
        frame = item["frame"]
        leftHand = item["leftHand"]
        string_last_frame = None
        if i != len(handDicts) - 1:
            next_frame = handDicts[i + 1]["frame"]
            if next_frame < frame + elapsed_frame:
                string_last_frame = next_frame
            else:
                string_last_frame = frame + elapsed_frame
        else:
            string_last_frame = frame + elapsed_frame

        for finger_data in leftHand:
            fingerIndex = finger_data["fingerIndex"]

            fingerInfo = finger_data["fingerInfo"]
            press = fingerInfo["press"]
            if (press == 0 or press == 5) and fingerIndex != -1:
                continue

            stringIndex = fingerInfo["stringIndex"]

            fret = 0 if fingerIndex == -1 else fingerInfo["fret"]

            ready = {
                "frame": frame-1,
                "stringIndex": stringIndex,
                "fret": fret,
                "influence": 0.0
            }

            start = {
                "frame": frame,
                "stringIndex": stringIndex,
                "fret": fret,
                "influence": 0.5
            }

            end = {
                "frame": string_last_frame,
                "stringIndex": stringIndex,
                "fret": fret,
                "influence": 0.0
            }
            data_for_animation.append(ready)
            data_for_animation.append(start)
            data_for_animation.append(end)

            if string_last_frame and string_last_frame - frame > 2:
                middle = {
                    "frame": (string_last_frame+frame)/2,
                    "stringIndex": stringIndex,
                    "fret": fret,
                    "influence": 1
                }
                data_for_animation.append(middle)

    with open(string_recorder, "w") as f:
        json.dump(data_for_animation, f, indent=4)
