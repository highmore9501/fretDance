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
        handPosition = 0
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
        empty_fingers = []
        pressed_fingers = []
        pressed_finger_dict = {}
        finger_touch_string_counter = [0] * 5  # 1~4 号手指的触弦数，下标 0 不用
        newHandPosition = 0
        minFingerIndex = 5
        # 最小空弦音的弦的索引，用于判断食指是横按还是普通按
        min_empty_stringIndex = len(guitar.guitarStrings) - 1

        # 这里的使用弦的索引用于计算休息的手指放在哪个区间合适
        max_used_stringIndex = -1
        min_used_stringIndex = len(guitar.guitarStrings) - 1
        pressed_finger_index_set = set()

        # --第一次循环，处理空弦音，并且计算各个手指的触弦总数,更新最高和最低按弦索引，更新使用的手指索引--
        for fingerPosition in fingerPositions:
            fret = fingerPosition['fret']
            finger_index = fingerPosition.get('finger', -1)
            string_index = fingerPosition['index']
            # --生成空弦音的手指--
            if finger_index == -1:
                empty_finger = LeftFinger(
                    -1, guitar.guitarStrings[fingerPosition['index']], 0, "Open")
                empty_fingers.append(empty_finger)
                min_empty_stringIndex = min(
                    min_empty_stringIndex, fingerPosition['index'])
            # 统计按弦手指的触弦总数
            else:
                finger_touch_string_counter[finger_index] += 1
                # 统计最低的按弦的手指的位置
                if 0 < finger_index < minFingerIndex:
                    minFingerIndex = finger_index
                    newHandPosition = fret
                # 如果这个手指同时按了多个弦，那么就使用这些弦里最低一根的弦的索引
                if finger_touch_string_counter[finger_index] > 1:
                    old_fret, old_string_index = pressed_finger_dict[finger_index]
                    string_index = max(string_index, old_string_index)

                max_used_stringIndex = max(max_used_stringIndex, string_index)
                min_used_stringIndex = min(min_used_stringIndex, string_index)
                pressed_finger_dict[finger_index] = (fret, string_index)
                pressed_finger_index_set.add(finger_index)

        # 原手型的食指品位
        current_index_finger_fret = next(
            (finger.fret for finger in self.fingers if finger._fingerIndex == 1), 0)

        # --第二次循环，判断是否横按状态--
        use_barre = False
        for finger_index in pressed_finger_dict:
            fret, string_index = pressed_finger_dict[finger_index]
            touch_count = finger_touch_string_counter[finger_index]

            # 这里的意思是虽然这个食指只处理一个音符，但仍然可以用横按的方式
            # 当手指为食指，并且手指所在的品格和当前食指所在的品格（这个值是根据把位算出来的）相同，并且当前手指的弦索引小于最小空弦音的弦索引，那么这个食指可以横按
            could_barre = (fret == current_index_finger_fret and finger_index ==
                           1 and string_index < min_empty_stringIndex)
            # --这是必须使用横按--
            need_barre = (touch_count > 1 and finger_index == 1)

            use_barre = could_barre or need_barre
            # 先判断是否横按，并重新计算手指的位置
            if use_barre:
                press_state = "Barre"
                string_index = min_empty_stringIndex - 1
            elif touch_count == 1:
                press_state = "Pressed"
            elif touch_count == 2 and finger_index == 4:
                press_state = "Partial_barre_2_strings"
                # 虽然这里有定义两弦小横按，但实际上动画里只处理食指的三弦到六弦横按
            elif touch_count == 3 and finger_index == 4:
                press_state = "Partial_barre_3_strings"
            else:
                return None, None, None

            pressed_fingers.append(
                LeftFinger(finger_index, guitar.guitarStrings[string_index], fret, press_state))

        # 下面计算当前的把位，就是食指应该在的品格
        newHandPosition = max(1, newHandPosition - (minFingerIndex - 1))

        # 筛选出所有可能的保留指
        keep_finger_index_set = set()

        # 如果没有发生换把
        if newHandPosition == self.handPosition:
            for finger in self.fingers:
                if finger.stringIndex not in pressed_finger_index_set and finger.press != PRESSSTATE["Open"]:
                    keep_finger_index_set.add(finger._fingerIndex)
            # 横按状态尽量继承
            use_barre = self.useBarre or use_barre

        # 第三次循环，是为了检测有没有食指以外的手指按在横按上
        if use_barre and 1 in pressed_finger_index_set:
            barre_fret, barre_string_index = pressed_finger_dict[1]
            for finger_index in pressed_finger_dict:
                fret, string_index = pressed_finger_dict[finger_index]
                if finger_index != 1 and fret == barre_fret:
                    pressed_finger_index_set.remove(finger_index)

        # --寻找并生成未按弦的手指--
        open_fingers = []

        for finger_index in range(1, 5):
            # 跳过已按的指
            if finger_index in pressed_finger_index_set:
                continue
            # 处理非保留指
            if finger_index not in keep_finger_index_set:
                # 这里是不使用手指默认放置休息的弦位
                defalut_string_index = int(
                    (max_used_stringIndex+min_used_stringIndex)/2) if newHandPosition < 17 else 0
                defalut_string = guitar.guitarStrings[defalut_string_index]
                # 这里是默认放置休息的品位
                defalut_fret = newHandPosition + finger_index - 1
                press_state = "Open"
            # 处理保留指
            else:
                same_finger = [
                    finger for finger in self.fingers if finger._fingerIndex == finger_index][0]
                # 这里是保留值默认继承的位置
                defalut_string = guitar.guitarStrings[same_finger.stringIndex]
                defalut_fret = same_finger.fret
                # 如果保留指原来是按弦的，那状态改为Keep;如果是其它（横按），那么保持横按状态
                if same_finger.press == PRESSSTATE["Pressed"]:
                    press_state = "Keep"
                else:
                    press_state = [key for key, value in PRESSSTATE.items(
                    ) if value == same_finger.press][0]

            open_finger = LeftFinger(
                finger_index, defalut_string, defalut_fret, press_state)

            open_fingers.append(open_finger)

        all_fingers = pressed_fingers + empty_fingers + open_fingers

        if not self.verifyValid(all_fingers):
            return None, None, None

        diff = self.caculateDiff(
            all_fingers, newHandPosition, guitar)
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
