from .LeftFinger import LeftFinger, PRESSSTATE
from ..guitar.Guitar import Guitar
from typing import List


class LeftHand():
    """
    params:
    LeftFingers: List of LeftFinger. 手指列表
    maxFingerDistance: Maximum distance between two adjacent fingers. 两只相邻手指所能打开的最大距离，单位是cm
    """

    def __init__(self, LeftFingers: List[LeftFinger], use_barre: bool = False, maxFingerDistance: float = 5.73, ) -> None:
        self.fingers = LeftFingers
        self._maxFingerDistance = maxFingerDistance
        self.fingerDistanceTofretboard = 0.025
        self.handPosition = self.calculateHandPosition()
        self.reArrangeFingers()
        self.useBarre = use_barre

    @property
    def getMaxFingerDistance(self) -> float:
        return self._maxFingerDistance

    def allOpen(self) -> None:
        """
        set all fingers to open. 将所有手指设置为抬起
        """
        for finger in self.fingers:
            finger.press = PRESSSTATE["Open"]

    def reArrangeFingers(self) -> None:
        """
        rearrange the fingers. 将所有fret为0的手指设置为抬起，并重新计算它所在的fret
        """
        for finger in self.fingers:
            if finger._fingerIndex != 0 and finger.fret == 0:
                finger.press = PRESSSTATE["Open"]
                finger.fret = self.handPosition + finger._fingerIndex - 1

    def output(self, showOpenFinger: bool = False) -> None:
        """
        print current hand. 输出当前手型
        """
        for finger in self.fingers:
            finger.output()
        # 计算所有手指的最小fret值
        minFret = 24
        minFretIsSetted = False
        for finger in self.fingers:
            if finger.fret < minFret and finger.fret != 0:
                minFret = finger.fret
                minFretIsSetted = True

        if minFret < 4:
            baseFret = 0
        elif minFret < 6:
            baseFret = 3
        elif minFret < 8:
            baseFret = 5
        elif minFret < 10:
            baseFret = 7
        elif minFret < 13:
            baseFret = 9
        elif minFretIsSetted:
            baseFret = 12
        else:
            baseFret = 0

        print(baseFret)

        for stringIndex in range(6):
            txt = ""
            allnoteInStringIndex = []
            for finger in self.fingers:
                if finger.stringIndex == stringIndex:
                    allnoteInStringIndex.append(finger)
            # 如果这根弦上没有手指
            if len(allnoteInStringIndex) == 0:
                txt += "|" + 8 * " --" + str(stringIndex)
            else:
                pressedFinger = []
                openFinger = []
                hasOpenStringNote = False
                for finger in allnoteInStringIndex:
                    # 也就是index为-1的手指存在，说明本弦是空弦音
                    if finger._fingerIndex == -1:
                        hasOpenStringNote = True
                    # 根据在这根弦上的手指的按弦状态，将手指分为按下和抬起两类
                    press = finger.press
                    if press != PRESSSTATE["Open"]:
                        pressedFinger.append(finger)
                    else:
                        openFinger.append(finger)

                # 如果是空弦音，就以0起头
                if hasOpenStringNote:
                    txt += "0"
                else:
                    txt += "|"

                for characterIndex in range(1, 9):
                    characterIndexInPressedFinger = False
                    characterIndexInOpenFinger = False
                    # 这里只是输出谱面用0表示空弦音，实际定义上，空弦音的手指索引为-1
                    fingerIndex = 0
                    for finger in pressedFinger:
                        if finger.fret - baseFret == characterIndex:
                            characterIndexInPressedFinger = True
                            fingerIndex = finger._fingerIndex

                    openFingersInFret = []
                    for finger in openFinger:
                        if finger.fret - baseFret == characterIndex:
                            characterIndexInOpenFinger = True
                            openFingersInFret.append(finger._fingerIndex)

                    if characterIndexInPressedFinger:
                        txt += f" -{str(fingerIndex)}"
                    elif characterIndexInOpenFinger and showOpenFinger:
                        if len(openFingersInFret) == 1:
                            strikethrough_text = print_strikethrough(
                                str(openFingersInFret[0]))
                            txt += f" 0{strikethrough_text}"
                        elif len(openFingersInFret) == 2:
                            strikethrough_text = print_strikethrough(
                                str(openFingersInFret[0]) + str(openFingersInFret[1]))
                            txt += f" {strikethrough_text}"
                        elif len(openFingersInFret) == 3:
                            strikethrough_text = print_strikethrough(
                                str(openFingersInFret[0]) + str(openFingersInFret[1])+str(openFingersInFret[2]))
                            text += strikethrough_text
                    else:
                        txt += " --"

                txt += str(stringIndex)

            print(txt)
        print(f'把位：{self.handPosition}')
        print("-------------------------------")

    def verifyValid(self, all_fingers=None) -> bool:
        """
        verify if the hand is valid. 验证手型是否合法
        """
        if all_fingers == None:
            all_fingers = self.fingers

        if len(all_fingers) == 0:
            return False

        for finger in all_fingers:
            if finger._fingerIndex == -1:
                continue
            # 最高的把位限制，四指在0弦上最多按到22品，在1弦上最多按到21品，其它弦和其它手指依此类推
            if finger.fret > 22 - (4 - finger._fingerIndex) - finger.stringIndex:
                return False

        sortedFingers = sorted(all_fingers, key=lambda x: x._fingerIndex)
        # 如果在低把位，不能出现小拇指或者无名指延展两个品格的情况
        if self.handPosition < 10 and (sortedFingers[-1].fret - sortedFingers[-2].fret > 1 or sortedFingers[-2].fret - sortedFingers[-3].fret > 1):
            return False

        bigger_fret_counter = 0
        for i in range(len(sortedFingers)-1):
            if abs(sortedFingers[i].fret - sortedFingers[i+1].fret) > 1:
                bigger_fret_counter += 1
            minIndexFingerIsHigher = sortedFingers[i]._fingerIndex < sortedFingers[i +
                                                                                   1]._fingerIndex and sortedFingers[i].fret > sortedFingers[i+1].fret
            if minIndexFingerIsHigher:
                return False

            maxIndexFingerIsLower = sortedFingers[i]._fingerIndex > sortedFingers[i +
                                                                                  1]._fingerIndex and sortedFingers[i].fret < sortedFingers[i+1].fret
            if maxIndexFingerIsLower:
                return False

            bothFingerIsNotZero = sortedFingers[i].fret != 0 and sortedFingers[i+1].fret != 0
            fingerDistanceIsTooLarge = abs(sortedFingers[i].fret - sortedFingers[i+1].fret) > 2 * abs(
                sortedFingers[i]._fingerIndex - sortedFingers[i+1]._fingerIndex)
            if fingerDistanceIsTooLarge and bothFingerIsNotZero:
                return False

            fingerIndexLargeThanFret = sortedFingers[i]._fingerIndex > sortedFingers[i].fret + 1
            if fingerIndexLargeThanFret:
                return False

            minFingerIsOuter = sortedFingers[i].fret == sortedFingers[i +
                                                                      1].fret and sortedFingers[i].stringIndex < sortedFingers[i+1].stringIndex
            if minFingerIsOuter:
                return False

        if bigger_fret_counter > 1:
            return False

        return True

    def calculateHandPosition(self) -> int:
        """
        calculate the hand position. 计算手型的位置
        :return: hand position, which means the fret number of index finger. 手的位置，也就是食指所在的品格
        """
        handPosition = 1
        for finger in self.fingers:
            if finger._fingerIndex == 1 and finger.fret > 1:
                handPosition = finger.fret

        return handPosition

    def generateNextHands(self, guitar: Guitar, fingerPositions: List[tuple[str, int]]) -> tuple['LeftHand', float]:
        """
        :parma guitar: Guitar. 吉他
        :param chord: List of notes, including fret and string index and index of finger which pressed it. 音符列表，包括品格，弦的索引和按下它的手指的索引
        :return: List of next hands and their entropy. 下一个手型和它们的熵的列表
        """
        # 初始化空弦数据，按弦数据，横按数据，休息数据
        empty_fingers = []
        empty_string_index_set = set()

        used_finger_index_set = set()
        used_finger_fret_set = set()
        used_string_index_set = set()

        pressed_fingers = []
        pressed_finger_dict = {}

        barre_fingers = []
        barre_finger_dict = {}
        need_barre = False
        keep_barre = False
        use_barre = False

        keep_fingers = []

        rest_finger_index_set = set()
        rest_fingers = []
        # 1~4 号手指的触弦数，下标 0 不用
        finger_touch_string_counter = [0] * 5

        # 用于计算下一个手型把位的值，一开始它是统计的最低手指所按的品，统计完以后再根据情况来计算
        newHandPosition = 0

        # --第一次循环，处理空弦音，并且计算各个手指的触弦总数,更新最高和最低按弦索引，更新使用的手指索引--
        for fingerPosition in fingerPositions:
            fret = fingerPosition['fret']
            finger_index = fingerPosition.get('finger', -1)
            string_index = fingerPosition['index']
            # --生成空弦音的手指--
            if finger_index == -1:
                empty_finger = LeftFinger(
                    -1, guitar.guitarStrings[string_index], 0, "Open")
                empty_fingers.append(empty_finger)
                empty_string_index_set.add(string_index)
            # 统计按弦手指的触弦总数
            else:
                finger_touch_string_counter[finger_index] += 1
                # 添加按弦品格数据
                used_finger_fret_set.add(fret)
                # 如果这个手指同时按了多个弦，那么就使用这些弦里最低一根的弦的索引
                if finger_touch_string_counter[finger_index] > 1:
                    # 首次发现某个手指同时按了多个弦，需要把它从按弦手指列表中移除，因为会添加到横按列表中
                    if finger_touch_string_counter[finger_index] == 2:
                        old_fret, old_string_index = pressed_finger_dict[finger_index]
                        del pressed_finger_dict[finger_index]
                    else:
                        old_fret, old_string_index = barre_finger_dict[finger_index]

                    string_index = max(string_index, old_string_index)
                    barre_finger_dict[finger_index] = (fret, string_index)
                else:
                    pressed_finger_dict[finger_index] = (fret, string_index)
                used_finger_index_set.add(finger_index)
                used_string_index_set.add(string_index)

        # 生成按弦手指
        for pressed_finger_index in pressed_finger_dict:
            pressed_fret, pressed_string_index = pressed_finger_dict[pressed_finger_index]

            pressed_finger = LeftFinger(
                pressed_finger_index, guitar.guitarStrings[pressed_string_index], pressed_fret, "Pressed")

            pressed_fingers.append(pressed_finger)

        # 生成横按手指
        for barre_finger_index in barre_finger_dict:
            barre_fret, barre_string_index = barre_finger_dict[barre_finger_index]
            touch_count = finger_touch_string_counter[barre_finger_index]

            if touch_count > 1 and barre_finger_index == 1:
                press_state = "Barre"
                need_barre = True
                # 横按所按的弦，要比其它手指至少低一根弦，否则动画会很难看
                barre_string_index = max(
                    barre_string_index, max(used_string_index_set)+1)
                barre_string_index = min(barre_string_index, 5)
            elif touch_count == 2 and barre_finger_index == 4:
                press_state = "Partial_barre_2_strings"
            elif touch_count == 3 and barre_finger_index == 4:
                press_state = "Partial_barre_3_strings"
            else:
                press_state = "Pressed"

            barre_finger = LeftFinger(
                barre_finger_index, guitar.guitarStrings[barre_string_index], barre_fret, press_state)

            barre_fingers.append(barre_finger)

        # --处理未参与演奏的手指，看它们是横按还是否保留或者休息,在最后面生成保留指--
        if used_finger_index_set and used_finger_fret_set:
            newHandPosition = max(
                1, min(used_finger_fret_set)-(min(used_finger_index_set) - 1))
        else:
            # 如果没有按弦手指，使用当前手的位置或者默认位置
            newHandPosition = self.handPosition

        for old_finger_index in range(1, 5):
            # 跳过已按的指
            if old_finger_index in used_finger_index_set:
                continue
            # 发生了换把没必要处理保留指，把手指移动到休息位置
            if newHandPosition != self.handPosition:
                rest_finger_index_set.add(old_finger_index)
                continue

            # 读取手指在前一个手型里的位置信息
            same_finger = [
                finger for finger in self.fingers if finger._fingerIndex == old_finger_index][0]
            old_fret = same_finger.fret
            old_string_index = same_finger.stringIndex

            # 检测旧位置是否在现在横按的情况下可用
            finger_can_keep = True
            for barre_finger_index in barre_finger_dict:
                barre_fret, barre_string_index = barre_finger_dict[barre_finger_index]
                if old_fret <= barre_fret and old_string_index <= barre_string_index:
                    finger_can_keep = False
                    break

            # 如果旧位置与当前横按冲突，结束检测，将旧位置的手指索引添加到休息指索引列中
            if not finger_can_keep:
                rest_finger_index_set.add(old_finger_index)
                continue

            # 检测旧位置是否与当前按的位置有重合
            for pressed_finger_index in pressed_finger_dict:
                pressed_fret, pressed_string_index = pressed_finger_dict[pressed_finger_index]
                if old_fret == pressed_fret and old_string_index == pressed_string_index:
                    finger_can_keep = False
                    break

            # 如果有重合，结束检测，直接将旧位置的手指索引添加休息指索引列中
            if not finger_can_keep:
                rest_finger_index_set.add(old_finger_index)
                continue

            # 能运行到这里的都是保留指，直接用原状态生成新的保留指
            press_state = next(k for k, v in PRESSSTATE.items()
                               if v == same_finger.press)

            if same_finger.press == PRESSSTATE["Barre"]:
                keep_barre = True
                # 如果上一个保留横按的横按指的弦低于当前按弦的弦，那么需要横按指往低移动
                # 具体来讲，比如一个原来是横按123弦的保留指，结果现在要演奏的音出现了4弦，那么横按指应该至少移动到5弦才会让动画看起来正常
                old_string_index = max(
                    old_string_index, max(used_string_index_set)+1)
                old_string_index = min(old_string_index, 5)

            # 小指不使用保留指，因为动画里横按时小指的状态太难处理
            if old_finger_index == 4:
                press_state = "Open"

            old_string = guitar.guitarStrings[old_string_index]
            keep_finger = LeftFinger(
                old_finger_index, old_string, old_fret, press_state)
            keep_fingers.append(keep_finger)
            used_string_index_set.add(old_string_index)

        # --现在来处理所有空闲指，判断它们应该放在哪里休息--
        # 这一段还没考虑如果空闲指与其它手指冲突的处理
        for rest_finger_index in list(rest_finger_index_set):
            # 这是默认休息的弦索引，其实就是所有已经按弦弦索引的中位点
            if used_string_index_set:
                defalut_rest_string_index = int((min(
                    used_string_index_set)+max(used_string_index_set))/2) if newHandPosition < 17 else 0
            else:
                defalut_rest_string_index = 2
            # 这里是默认放置休息的品位
            defalut_rest_fret = newHandPosition + rest_finger_index - 1
            rest_string = guitar.guitarStrings[defalut_rest_string_index]

            press_state = "Open"

            rest_finger = LeftFinger(
                rest_finger_index, rest_string, defalut_rest_fret, press_state)

            rest_fingers.append(rest_finger)

        all_fingers = pressed_fingers + barre_fingers + \
            empty_fingers + rest_fingers + keep_fingers

        if not self.verifyValid(all_fingers):
            return None, None, None

        diff = self.caculateDiff(
            all_fingers, newHandPosition, guitar)

        use_barre = need_barre or keep_barre
        return all_fingers, diff, use_barre

    def caculateDiff(self, all_fingers, newHandPosition, guitar: Guitar) -> float:
        entropy = 0
        hand_position_diff = abs(self.handPosition - newHandPosition)
        # 如果要换把，首先要抬指
        if hand_position_diff > 0:
            for finger in self.fingers:
                if finger.press != PRESSSTATE["Open"]:
                    entropy += self.fingerDistanceTofretboard

        # 计算每一个手指的位移
        for index in range(1, 5):
            distance = None
            old_finger = next(
                (finger for finger in self.fingers if finger._fingerIndex == index), None)
            new_finger = next(
                (finger for finger in all_fingers if finger._fingerIndex == index), None)

            if old_finger is not None and new_finger is not None:
                distance = old_finger.distanceTo(guitar, new_finger)
                entropy += distance

            # 计算按下手指的熵
            if distance is not None and new_finger.press != PRESSSTATE["Open"]:
                entropy += self.fingerDistanceTofretboard

        return entropy


def print_strikethrough(text):
    return f"\033[9m{text}\033[0m"
