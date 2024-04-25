from .LeftFinger import LeftFinger, PRESSSTATE
from ..guitar.Guitar import Guitar
from typing import List


class LeftHand():
    """
    params:
    LeftFingers: List of LeftFinger. 手指列表
    maxFingerDistance: Maximum distance between two adjacent fingers. 两只相邻手指所能打开的最大距离，单位是cm
    """

    def __init__(self, LeftFingers: List[LeftFinger], maxFingerDistance: float = 5.73) -> None:
        self.fingers = LeftFingers
        self._maxFingerDistance = maxFingerDistance
        self.fingerDistanceTofretboard = 0.025
        self.handPosition = self.calculateHandPosition()
        self.reArrangeFingers()

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
        rearrange the fingers. 重新排列手指
        """
        for finger in self.fingers:
            if finger._fingerIndex != 0 and finger.fret == 0:
                finger.press = PRESSSTATE["Open"]
                finger.fret = self.handPosition + finger._fingerIndex - 1

    def output(self, showOpenFinger: bool = False) -> None:
        """
        print current hand. 输出当前手型
        """
        from ..utils.utils import print_strikethrough
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

    def verifyValid(self) -> bool:
        """
        verify if the hand is valid. 验证手型是否合法
        """
        if len(self.fingers) == 0:
            return False

        sortedFingers = sorted(self.fingers, key=lambda x: x._fingerIndex)
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

    def generateNextHands(self, guitar: Guitar, fingerPositions: List[tuple[str, int]], notes) -> tuple['LeftHand', float]:
        """
        :parma guitar: Guitar. 吉他
        :param chord: List of notes, including fret and string index and index of finger which pressed it. 音符列表，包括品格，弦的索引和按下它的手指的索引
        :return: List of next hands and their entropy. 下一个手型和它们的熵的列表
        """
        empty_fingers = []
        finger_touch_string_counter = {}
        newHandPosition = 0
        minFingerIndex = 4
        for fingerPosition in fingerPositions:
            fret = fingerPosition['fret']
            finger_index = fingerPosition.get('finger', -1)
            # 统计最低的手指的位置
            if 0 < finger_index < minFingerIndex:
                minFingerIndex = finger_index
                newHandPosition = fret
            # 生成空弦音的手指
            if finger_index == -1:
                empty_finger = LeftFinger(
                    -1, guitar.guitarStrings[fingerPosition['index']], 0, "Open")
                empty_fingers.append(empty_finger)
            # 统计按弦手指的触弦总数
            else:
                if finger_index not in finger_touch_string_counter:
                    finger_touch_string_counter[finger_index] = 0
                finger_touch_string_counter[finger_index] += 1

        # 生成按弦手指
        pressed_fingers = []
        pressed_finger_indexs = []
        for fingerPosition in fingerPositions:
            finger_index = fingerPosition.get('finger', -1)
            if finger_index == -1:
                continue
            touch_count = finger_touch_string_counter[finger_index]
            if touch_count == 1:
                press_state = "Pressed"
            elif touch_count > 1 and finger_index == 1:
                press_state = "Barre"
            elif touch_count == 2 and finger_index == 4:
                press_state = "Partial_barre_2_strings"
            elif touch_count == 3 and finger_index == 4:
                press_state = "Partial_barre_3_strings"
            else:
                return None, None
            pressed_finger = LeftFinger(
                finger_index, guitar.guitarStrings[fingerPosition['index']], fingerPosition['fret'], press_state)
            pressed_fingers.append(pressed_finger)
            pressed_finger_indexs.append(finger_index)

        # 下面计算当前的把位，就是食指应该在的品格
        newHandPosition -= (minFingerIndex - 1)
        if newHandPosition < 1:
            newHandPosition = 1

        open_fingers = []
        # 寻找并生成未按弦的手指
        for finger_index in range(1, 5):
            if finger_index not in pressed_finger_indexs:
                defalut_string = guitar.guitarStrings[2]
                defalut_fret = newHandPosition + finger_index - 1
                open_finger = LeftFinger(
                    finger_index, defalut_string, defalut_fret, "Open")
                open_fingers.append(open_finger)

        all_fingers = pressed_fingers + empty_fingers + open_fingers

        newHand = LeftHand(all_fingers, self.getMaxFingerDistance)

        if not newHand.verifyValid():
            return None, None

        diff = self.caculateDiff(newHand, pressed_finger_indexs, guitar)
        return newHand, diff

    def caculateDiff(self, newHand: 'LeftHand', pressed_finger_indexs: List[int], guitar: Guitar) -> float:
        entropy = 0
        hand_position_diff = abs(self.handPosition - newHand.handPosition)
        # 如果要换把，首先要抬指
        if hand_position_diff > 0:
            for finger in self.fingers:
                if finger.press != PRESSSTATE["Open"]:
                    entropy += self.fingerDistanceTofretboard

        # 计算每一个手指的位移
        for index in range(1, 5):
            old_finger = next(
                (finger for finger in self.fingers if finger._fingerIndex == index), None)
            new_finger = next(
                (finger for finger in newHand.fingers if finger._fingerIndex == index), None)

            if old_finger is not None and new_finger is not None:
                entropy += old_finger.distanceTo(guitar, new_finger)

        # 计算按下手指的熵
        entropy += len(pressed_finger_indexs) * self.fingerDistanceTofretboard

        return entropy
