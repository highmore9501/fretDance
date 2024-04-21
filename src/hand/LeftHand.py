from .LeftFinger import LeftFinger, PRESSSTATE
from ..guitar.Guitar import Guitar
import copy
from typing import List
from ..utils.utils import print_strikethrough
from ..utils.fretDistanceDict import FRET_DISTANCE_DICT
import itertools


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

    @property
    def getMaxFingerDistance(self) -> float:
        return self._maxFingerDistance

    def allOpen(self) -> None:
        """
        set all fingers to open. 将所有手指设置为抬起
        """
        for finger in self.fingers:
            finger.press = PRESSSTATE["Open"]

    def output(self, showOpenFinger: bool = False) -> None:
        """
        print current hand. 输出当前手型
        """
        print("当前手型如下：")
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

    def generateNextHands(self, guitar: Guitar, fingerPositions: List[tuple[str, int]]) -> tuple['LeftHand', float]:
        """
        :parma guitar: Guitar. 吉他
        :param chord: List of notes, including fret and string index and index of finger which pressed it. 音符列表，包括品格，弦的索引和按下它的手指的索引
        :return: List of next hands and their entropy. 下一个手型和它们的熵的列表
        """
        # 初始化一些信息
        entropy = 0

        fingerIndexCounter = {}

        # 统计每个手指的触弦数量
        hasPressedFinger = False
        for fingerPosition in fingerPositions:
            if "finger" in fingerPosition:
                fingerIndex = fingerPosition['finger']
                hasPressedFinger = True
            else:
                fingerPosition['finger'] = -1
                fingerIndex = -1

            if fingerIndex in fingerIndexCounter:
                fingerIndexCounter[fingerIndex] += 1
            else:
                fingerIndexCounter[fingerIndex] = 1

        tmpFingers = copy.deepcopy(self.fingers)
        # 去掉tmpFingers中index小于1的手指，确保tmpFinger里只会有1234手指
        tmpFingers = [
            finger for finger in tmpFingers if finger._fingerIndex > 0]

        if not hasPressedFinger:
            for finger in tmpFingers:
                finger.press = PRESSSTATE["Open"]
            newHand = LeftHand(tmpFingers)
            return newHand, entropy

        # 先遍历所有fingerPosition，判断出下一个手型的把位
        newHandPosition = 0
        minFingerIndex = 4
        for fingerPosition in fingerPositions:
            fret = fingerPosition['fret']
            finger_index = fingerPosition['finger']
            if 0 < finger_index < minFingerIndex:
                minFingerIndex = finger_index
                newHandPosition = fret

        newHandPosition -= (minFingerIndex - 1)
        if newHandPosition < 1:
            newHandPosition = 1

        # 换把
        handPositionDiff = newHandPosition - self.handPosition

        if abs(handPositionDiff) > 1:
            # 先计算手指抬起的消耗
            for finger in tmpFingers:
                if finger.press != PRESSSTATE["Open"]:
                    entropy += self.fingerDistanceTofretboard

            if self.handPosition != newHandPosition:
                start_fret = min(self.handPosition, newHandPosition)
                end_fret = max(self.handPosition, newHandPosition)
                distance_query_name = str(start_fret) + "-" + str(end_fret)
                distance_query_result = FRET_DISTANCE_DICT[distance_query_name]
                entropyChangeBarrel = guitar._fullString * distance_query_result

                entropy += entropyChangeBarrel
            # 把临时的fingers列表里面的每个手指都移动handPositionDiff品格
            for tmpFinger in tmpFingers:
                tmpFinger.fret += handPositionDiff
                tmpFinger.press = PRESSSTATE["Open"]
                if tmpFinger.fret > 23:
                    return None, None

        # 计算那些在新手型里需要按弦的手弦的消耗
        pressedFingers = []
        indexIsCaculated = {
            1: False,
            2: False,
            3: False,
            4: False
        }
        for fingerPosition in fingerPositions:
            # 如果是一个空弦音，生成一个空手指，并加入到pressedFingers中
            if fingerPosition['finger'] == -1:
                newGuitarString = copy.deepcopy(guitar.guitarStrings[0])
                newFinger = LeftFinger(-1, newGuitarString, 0, "Open")
                newFinger.stringIndex = fingerPosition['index']
                pressedFingers.append(newFinger)
                continue

            # 如果这个位置不是空弦音，需要计算它的消耗
            guitar_string_index = fingerPosition['index']
            fret = fingerPosition['fret']
            finger_index = fingerPosition['finger']

            # 如果某个手指已经计算过了，就跳过
            if indexIsCaculated[finger_index] == True:
                continue

            for tmpFinger in tmpFingers:
                if tmpFinger._fingerIndex == finger_index:
                    # 计算手指的按弦状态
                    finger_repeat_times = fingerIndexCounter[finger_index]
                    if finger_repeat_times == 1:
                        pressState = PRESSSTATE["Pressed"]
                    elif finger_repeat_times > 1 and finger_index == 1:
                        pressState = PRESSSTATE["Barre"]
                    elif finger_repeat_times == 2 and finger_index == 4:
                        pressState = PRESSSTATE["Partial_barre_2_strings"]
                    elif finger_repeat_times == 3 and finger_index == 4:
                        pressState = PRESSSTATE["Partial_barre_3_strings"]
                    else:
                        return None, None
                    # 计算抬指的消耗
                    if (tmpFinger.fret != fret or tmpFinger.stringIndex != guitar_string_index) and tmpFinger.press != PRESSSTATE["Open"]:
                        entropy += self.fingerDistanceTofretboard
                    # 计算移动手指的消耗
                    fingerStringDistance = abs(
                        tmpFinger.stringIndex - guitar_string_index) * guitar._stringDistance
                    entropy += fingerStringDistance

                    if fret != tmpFinger.fret:
                        start_fret = min(fret, tmpFinger.fret)
                        end_fret = max(fret, tmpFinger.fret)
                        distance_query_name = str(
                            start_fret) + "-" + str(end_fret)
                        distance_query_result = FRET_DISTANCE_DICT[distance_query_name]
                        fingerFretDistance = guitar._fullString * distance_query_result

                        entropy += fingerFretDistance
                        tmpFinger.fret = fret

                    tmpFinger.stringIndex = guitar_string_index

                    tmpFinger.press = pressState
                    # 计算落指的消耗
                    entropy += self.fingerDistanceTofretboard
                    pressedFingers.append(tmpFinger)
                    indexIsCaculated[finger_index] = True

        # 将无归属的手指计算当前位置以及消耗
        openFingers = []
        for tmpFinger in tmpFingers:
            if tmpFinger not in pressedFingers:
                if tmpFinger.press != PRESSSTATE["Open"]:
                    entropy += self.fingerDistanceTofretboard
                    tmpFinger.press = PRESSSTATE["Open"]
                # 没有被使用的手指要向原始位置回归一点
                fretIsTooLarge = tmpFinger.fret-self.handPosition > tmpFinger._fingerIndex
                if fretIsTooLarge:
                    tmpFinger.fret += -1
                stringIsTooLarge = tmpFinger.stringIndex > 2
                tmpFinger.stringIndex += -1 if stringIsTooLarge else 1
                openFingers.append(tmpFinger)

        conflictFinger = []
        if len(openFingers) != 0 and len(pressedFingers) != 0:
            # 寻找两个数列中是否存在stringIndex和fret都相同的手指，如果有，就将openFinger在品格上反向移动一格以解决冲突
            for openFinger, pressedFinger in itertools.product(openFingers, pressedFingers):
                if openFinger.stringIndex == pressedFinger.stringIndex and openFinger.fret == pressedFinger.fret:
                    openFinger.fret += openFinger._fingerIndex - pressedFinger._fingerIndex
                    conflictFinger.append(openFinger)
                # 如果第一个手指是食指，第二个手指是中指，且两个手指在同一品上，并且两个手指并没有同时按下，移动未按的手指以解决冲突
                # 之所以要有这个判断，是因为这两指的位置决定了手掌旋转的角度，所以除非是两指都需要按弦，否则不应该在同一个品位上
                if pressedFinger.fret == openFinger.fret and (pressedFinger._fingerIndex == 1 and openFinger._fingerIndex == 2 or pressedFinger._fingerIndex == 2 and openFinger._fingerIndex == 1):
                    openFinger.fret += 1 if openFinger._fingerIndex == 2 else - 1
                    conflictFinger.append(openFinger)

        # 用现在的手指状态生成新的LeftHand，返回它以及消耗
        nextLeftFingerList = pressedFingers + openFingers
        newHand = LeftHand(nextLeftFingerList)
        if not newHand.verifyValid():
            return None, None

        return newHand, entropy
