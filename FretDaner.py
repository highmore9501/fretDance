import itertools
import json
from typing import List
from tqdm import tqdm

from src.HandPoseRecorder import HandPoseRecordPool, HandPoseRecorder, RightHandRecorder
from src.animate.animate import leftHand2Animation, rightHand2Animation, ElectronicRightHand2Animation, addPitchwheel, animated_guitar_string
from src.guitar.Guitar import Guitar
from src.guitar.GuitarString import createGuitarStrings
from src.guitar.MusicNote import MusicNote
from src.hand.LeftFinger import LeftFinger
from src.hand.LeftHand import LeftHand
from src.hand.RightHand import RightHand, generatePossibleRightHands
from src.midi.midiToNote import calculate_frame, get_tempo_changes, midiToGuitarNotes, processedNotes
from src.utils.utils import convertChordTofingerPositions, convertNotesToChord


def generateLeftHandRecoder(guitarNote, guitar: Guitar, handPoseRecordPool: HandPoseRecordPool, current_recoreder_num: int, previous_recoreder_num: int):
    notes = guitarNote.get("notes", False)
    if notes == False:
        return current_recoreder_num, previous_recoreder_num
    real_tick = guitarNote["real_tick"]
    min_note = guitar.guitarStrings[-1].getBaseNote()
    max_note = guitar.guitarStrings[0].getBaseNote() + 22
    notes = processedNotes(notes, min_note, max_note)

    # calculate all possible chords, including the position information of notes on the guitar. 计算所有可能的和弦,包含音符在吉它上的位置信息。
    chords = convertNotesToChord(notes, guitar)

    # init current record list. 记录池先更新初始化当前记录列表。
    handPoseRecordPool.readyForRecord()
    fingerPositionsList = []
    handPoseRecordCount = 0

    # calculate all possible fingerings, including the position information of fingers on the guitar. 计算所有可能的按法，包含手指在吉它上的位置信息。
    for chord in chords:
        possibleFingerPositions = convertChordTofingerPositions(chord)
        if len(possibleFingerPositions) == 0:
            continue
        fingerPositionsList += possibleFingerPositions

    if len(fingerPositionsList) == 0:
        print(
            f"当前时间是{real_tick}，当前notes是{notes},没有找到合适的按法。这是所有的chords：{chords}。")

    for handPoseRecord, fingerPositions in itertools.product(handPoseRecordPool.preHandPoseRecordPool, fingerPositionsList):
        oldhand = handPoseRecord.currentHandPose()

        # Iterate through the list of fingerings, generate a new LeftHand object based on the fingering. 遍历按法列表，根据按法生成新的LeftHand对象。
        all_fingers, entropy = oldhand.generateNextHands(
            guitar, fingerPositions, notes)

        if all_fingers is not None:
            new_entropy = handPoseRecord.currentEntropy + entropy
            insert_index = handPoseRecordPool.check_insert_index(new_entropy)
            # 当新手型符合插入记录器条件时
            if insert_index != -1:
                newHandPoseRecord = HandPoseRecorder()
                new_hand = LeftHand(all_fingers)

                newHandPoseRecord.handPoseList = handPoseRecord.handPoseList + \
                    [new_hand]
                newHandPoseRecord.currentEntropy = handPoseRecord.currentEntropy + entropy
                newHandPoseRecord.entropys = handPoseRecord.entropys + \
                    [new_entropy]
                newHandPoseRecord.real_ticks = handPoseRecord.real_ticks + \
                    [real_tick]

                handPoseRecordPool.insert_new_hand_pose_recorder(
                    newHandPoseRecord, insert_index)
                handPoseRecordCount += 1

    previous_recoreder_num = current_recoreder_num
    current_recoreder_num = len(handPoseRecordPool.curHandPoseRecordPool)

    if current_recoreder_num < previous_recoreder_num:
        print(
            f"当前record数量是{current_recoreder_num}，上一次record数量是{previous_recoreder_num}，这一轮操作一共append了{handPoseRecordCount}个record。")
        print(f"此时的real_tick是{real_tick},此时的notes是：{notes},对应的音符是：")
        for note in notes:
            musice_note = MusicNote(note)
            print(musice_note.key)

    return current_recoreder_num, previous_recoreder_num


def update_recorder_pool(total_steps: int, guitar: Guitar, handPoseRecordPool: HandPoseRecordPool, notes_map, current_recoreder_num, previous_recoreder_num):
    with tqdm(total=total_steps, desc="Processing", ncols=100, unit="step") as progress:
        for i in range(0, total_steps):
            guitarNote = notes_map[i]
            current_recoreder_num, previous_recoreder_num = generateLeftHandRecoder(
                guitarNote, guitar, handPoseRecordPool, current_recoreder_num, previous_recoreder_num)
            progress.update(1)


def generateRightHandRecoder(item, rightHandRecordPool, current_recoreder_num, previous_recoreder_num, max_string_index):
    real_tick = item["real_tick"]
    leftHand = item["leftHand"]
    touchedStrings = []

    for finger in leftHand:
        if finger["fingerIndex"] == -1 or 5 > finger["fingerInfo"]["press"] > 0:
            touchedStrings.append(finger["fingerInfo"]["stringIndex"])

    if touchedStrings == []:
        return
    rightHandRecordPool.readyForRecord()

    # usedStrings元素去重
    touchedStrings = list(set(touchedStrings))
    # usedStrings进行从高到低的排序
    touchedStrings.sort(reverse=True)

    # 这个重复p的写法是确保p指可能弹两根弦，但如果是四弦bass或者只有一个单音的情况下，就不允许用p指弹两根弦
    allow_double_p = max_string_index > 3 and len(touchedStrings) > 1
    allFingers = ["p", "p", "i", "m",
                  "a"] if allow_double_p else ["p", "i", "m", "a"]
    allstrings = list(range(max_string_index + 1))

    possibleCombinations = generatePossibleRightHands(
        touchedStrings, allFingers, allstrings)

    if len(possibleCombinations) == 0:
        print(f"当前要拨动的弦是{touchedStrings}，没有找到合适的右手拨法。")

    for combination, handRecorder in itertools.product(possibleCombinations, rightHandRecordPool.preHandPoseRecordPool):
        lastHand = handRecorder.currentHandPose()
        usedFingers = combination['usedFingers']
        rightFingerPositions = combination['rightFingerPositions']
        rightHand = RightHand(
            usedFingers, rightFingerPositions, lastHand.usedFingers, usedFingers == [])

        entropy = lastHand.caculateDiff(rightHand)
        new_entropy = handRecorder.currentEntropy + entropy
        insert_index = rightHandRecordPool.check_insert_index(
            new_entropy)
        if insert_index != -1:
            newRecorder = RightHandRecorder()
            newRecorder.handPoseList = handRecorder.handPoseList + \
                [rightHand]
            newRecorder.currentEntropy = handRecorder.currentEntropy + entropy
            newRecorder.entropys = handRecorder.entropys + [new_entropy]
            newRecorder.real_ticks = handRecorder.real_ticks + [real_tick]

            rightHandRecordPool.insert_new_hand_pose_recorder(
                newRecorder, insert_index)

    previous_recoreder_num = current_recoreder_num
    current_recoreder_num = len(
        rightHandRecordPool.curHandPoseRecordPool)

    if current_recoreder_num < previous_recoreder_num:
        print(
            f"当前record数量是{current_recoreder_num}，上一次record数量是{previous_recoreder_num}")


def update_right_hand_recorder_pool(left_hand_recorder_file, rightHandRecordPool, current_recoreder_num, previous_recoreder_num, max_string_index):
    with open(left_hand_recorder_file, "r") as f:
        data = json.load(f)
        total_steps = len(data)
        current_recoreder_num = 0
        previous_recoreder_num = current_recoreder_num

        with tqdm(total=total_steps, desc="Processing", ncols=100, unit="step") as progress:
            for i in range(total_steps):
                item = data[i]
                generateRightHandRecoder(
                    item, rightHandRecordPool, current_recoreder_num, previous_recoreder_num, max_string_index)
                progress.update(1)


def leftHand2ElectronicRightHand(left_hand_recorder_file, right_hand_recorder_file):
    result = []
    with open(left_hand_recorder_file, "r") as f:
        data = json.load(f)
        total_steps = len(data)

        with tqdm(total=total_steps, desc="Processing", ncols=100, unit="step") as progress:
            for i in range(total_steps):
                item = data[i]
                pitchwheel = item.get("pitchwheel", 0)
                if pitchwheel != 0:
                    continue
                leftHand = item["leftHand"]
                frame = item["frame"]
                strings = []
                for finger in leftHand:
                    if finger["fingerIndex"] == -1 or 0 < finger["fingerInfo"]["press"] < 5:
                        strings.append(finger["fingerInfo"]['stringIndex'])

                if len(strings) > len(set(strings)):
                    strings = list(set(strings))

                result.append({
                    'frame': frame,
                    'strings': strings,
                })

                progress.update(1)

    with open(right_hand_recorder_file, "w") as f:
        json.dump(result, f, indent=4)


def main(avatar: str, midiFilePath: str, track_number: int, channel_number: int, FPS: int, guitar_string_notes: List[str], octave_down_checkbox: bool, capo_number: int) -> str:
    filename = midiFilePath.split("/")[-1].split(".")[0]
    notes_map_file = f"output/{filename}_{track_number}_notes_map.json"
    messages_file = f"output/{filename}_{track_number}_messages.json"
    left_hand_recorder_file = f"output/{filename}_{track_number}_lefthand_recorder.json"
    left_hand_animation_file = f"output/{avatar}_{filename}_{track_number}_lefthand_animation.json"
    right_hand_recorder_file = f"output/{filename}_{track_number}_righthand_recorder.json"
    right_hand_animation_file = f"output/{avatar}_{filename}_{track_number}_righthand_animation.json"
    guitar_string_recorder_file = f"output/{filename}_{track_number}_guitar_string_recorder.json"

    tempo_changes, ticks_per_beat = get_tempo_changes(midiFilePath)
    notes_map, pitch_wheel_map, messages = midiToGuitarNotes(
        midiFilePath, useTrack=track_number, useChannel=channel_number, octave_down_checkbox=octave_down_checkbox, capo_number=capo_number)
    with open(notes_map_file, "w") as f:
        json.dump(notes_map, f, indent=4)
    with open(messages_file, "w") as f:
        json.dump(messages, f, indent=4)

    print(f'全曲的速度变化是:')
    for track, tempo, tick in tempo_changes:
        print(f'在{track}轨，tick为{tick}时，速度变为{tempo}')

    print(f'\n全曲的每拍tick数是:{ticks_per_beat}\n')

    total_tick = notes_map[-1]['real_tick']
    total_frame = calculate_frame(
        tempo_changes, ticks_per_beat, FPS, total_tick)
    total_time = total_frame/FPS
    print(
        f'如果以{FPS}的fps做成动画，一共是{total_tick} ticks, 合计{total_frame}帧, 约{total_time}秒')

    guitar_string_list = createGuitarStrings(guitar_string_notes)
    max_string_index = len(guitar_string_list) - 1
    # 初始化吉它
    guitar = Guitar(guitar_string_list)
    # 设定各手指状态
    leftFingers = [
        LeftFinger(1, guitar_string_list[2], 1),
        LeftFinger(2, guitar_string_list[2], 2),
        LeftFinger(3, guitar_string_list[2], 3),
        LeftFinger(4, guitar_string_list[2], 4)
    ]
    # 初始化左手
    initLeftHand = LeftHand(leftFingers)
    # 初始化第一个记录器
    handPoseRecord = HandPoseRecorder()
    handPoseRecord.addHandPose(initLeftHand, 0, 0)
    # 初始化记录池
    handPoseRecordPool = HandPoseRecordPool(100)
    handPoseRecordPool.insert_new_hand_pose_recorder(handPoseRecord, 0)

    current_recoreder_num = 0
    previous_recoreder_num = 0

    total_steps = len(notes_map)
    current_recoreder_num = 0
    previous_recoreder_num = current_recoreder_num

    print('开始生成左手按弦数据')

    update_recorder_pool(total_steps, guitar, handPoseRecordPool, notes_map, current_recoreder_num,
                         previous_recoreder_num)

    # after all iterations, read the best solution in the recorder pool. 全部遍历完以后，读取记录池中的最优解。
    bestHandPoseRecord = handPoseRecordPool.curHandPoseRecordPool[0]
    bestEntropy = bestHandPoseRecord.currentEntropy
    print(f"最小消耗熵为：{bestEntropy}")
    bestHandPoseRecord.save(left_hand_recorder_file,
                            tempo_changes, ticks_per_beat, FPS)
    print(f"总音符数应该为{total_steps}")
    print(f"实际输出音符数为{len(bestHandPoseRecord.handPoseList)}")

    # 如果有各种推弦动作，添加推弦动作
    if len(pitch_wheel_map) > 0:
        for item in pitch_wheel_map:
            frame = calculate_frame(
                tempo_changes, ticks_per_beat, FPS, item['real_tick'])
            item['frame'] = frame
        addPitchwheel(left_hand_recorder_file, pitch_wheel_map)

    leftHand2Animation(avatar, left_hand_recorder_file,
                       left_hand_animation_file, tempo_changes, ticks_per_beat, FPS, max_string_index)

    # 下面是处理右手的部分，右手要视情况分电吉他与古典吉他两种情况处理。
    print('开始生成右手演奏数据')
    if avatar.endswith("_E"):
        leftHand2ElectronicRightHand(
            left_hand_recorder_file, right_hand_recorder_file)
        ElectronicRightHand2Animation(
            avatar, right_hand_recorder_file, right_hand_animation_file, FPS)
    else:
        initRightHand = RightHand(
            usedFingers=[], rightFingerPositions=[max_string_index, 2, 1, 0], preUsedFingers=[])

        initRightHandRecorder = RightHandRecorder()
        initRightHandRecorder.addHandPose(initRightHand, 0, 0)

        rightHandRecordPool = HandPoseRecordPool(100)
        rightHandRecordPool.insert_new_hand_pose_recorder(
            initRightHandRecorder, 0)

        update_right_hand_recorder_pool(
            left_hand_recorder_file, rightHandRecordPool, current_recoreder_num, previous_recoreder_num, max_string_index)

        # after all iterations, read the best solution in the record pool. 全部遍历完以后，读取记录池中的最优解。
        bestHandPoseRecord = rightHandRecordPool.curHandPoseRecordPool[0]
        bestEntropy = bestHandPoseRecord.currentEntropy
        print(f"最小消耗熵为：{bestEntropy}")
        bestHandPoseRecord.save(right_hand_recorder_file,
                                tempo_changes, ticks_per_beat, FPS)

        rightHand2Animation(avatar, right_hand_recorder_file,
                            right_hand_animation_file, FPS)

    print('开始生成吉他弦动画数据')
    animated_guitar_string(left_hand_recorder_file,
                           guitar_string_recorder_file, FPS)

    finall_info = f'全部执行完毕:\nrecorder文件被保存到了:{left_hand_recorder_file} 和 {right_hand_recorder_file}\n动画文件被保存到了:{left_hand_animation_file} 和 {right_hand_animation_file}\n吉它弦动画文件被保存到了:{guitar_string_recorder_file}'

    print(finall_info)

    return finall_info


if __name__ == "__main__":
    avatar = 'asuka'
    # 设定midi文件路径
    midiFilePath = "asset/midi/Sunburst.mid"
    # 设定blender里的FPS
    FPS = 30
    # 设定各弦音高
    guitar_string_notes = ["d", "b", "G", "D", "A", "D1"]
    main(avatar, midiFilePath, FPS, guitar_string_notes)
