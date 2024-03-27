from src.hand.LeftFinger import LeftFinger, PRESSSTATE
from src.guitar.Guitar import Guitar
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

    @property
    def getMaxFingerDistance(self) -> float:
        return self._maxFingerDistance

    def output(self) -> None:
        """
        print current hand. 输出当前手型
        """
        # 计算所有手指的最小fret值
        minFret = 24
        for finger in self.fingers:
            if finger.fret < minFret and finger.fret != 0:
                minFret = finger.fret
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
        else:
            baseFret = 12
        print(baseFret)

        for i in range(6):
            found = False
            # 寻找self.fingers中具有相同stringIndex的手指
            for finger in self.fingers:
                if finger.guitarString._stringIndex == i:
                    fret = finger.fret
                    if fret == 0:
                        print("0"+8*" --")
                    else:
                        foramttedFret = str(
                            fret) if fret > 9 else " "+str(fret)
                        txt = "|" + (fret-baseFret-1)*" --" + " " + \
                            foramttedFret+(8-fret+baseFret)*" --"
                        print(txt)
                    found = True
            if not found:
                print("|"+8*" --")

        print("-------------------------------")

    def calculateEntropy(self, guitar: Guitar, targetHand: 'LeftHand') -> float:
        """
        calculate the entropy between two hands. 计算两个手型转换之间的熵
        :param targetHand: 目标手型
        :return: entropy. 熵
        """
        entropy = 0
        etc = guitar._ETC
        tmpFingers = self.fingers.copy()
        # 根据食指计算两个手型之间是否要换把位,
        handPositionDiff = self.handPosition - targetHand.handPosition

        if abs(handPositionDiff) > 1:
            # 先计算手指抬起的消耗
            for finger in tmpFingers:
                if finger.press != PRESSSTATE["Open"]:
                    entropy += self.fingerDistanceTofretboard

            # 再计算手掌换把的消耗
            entropy += abs(guitar._fullString / pow(etc, self.handPosition) -
                           guitar._fullString / pow(etc, targetHand.handPosition))

            # 把临时的fingers列表里面的每个手指都移动handPositionDiff品格
            for tmpFinger in tmpFingers:
                tmpFinger.fret += handPositionDiff

        # 最后计算每个手指运动的消耗
        for index in range(len(tmpFingers)):
            currentFinger = tmpFingers[index]
            fingerName = currentFinger._fingerName
            # 在targetHand.fingers中寻找有相同手指名字的手指
            targetFinger = None
            for finger in targetHand.fingers:
                if finger._fingerName == fingerName:
                    targetFinger = finger
                    break
            if targetFinger is None:
                continue

            if currentFinger.press != PRESSSTATE["Open"]:
                entropy += self.fingerDistanceTofretboard
            if targetFinger.press == PRESSSTATE["Open"]:
                continue
            # 计算手指的移动和按下的消耗
            entropy += currentFinger.distanceTo(
                guitar, targetFinger) + self.fingerDistanceTofretboard

        return entropy

    def verifyValid(self) -> bool:
        """
        verify if the hand is valid. 验证手型是否合法
        """
        for i in range(len(self.fingers)-1):
            minIndexFingerIsHigher = self.fingers[i]._fingerIndex < self.fingers[i +
                                                                                 1]._fingerIndex and self.fingers[i].fret > self.fingers[i+1].fret
            if minIndexFingerIsHigher:
                return False

            maxIndexFingerIsLower = self.fingers[i]._fingerIndex > self.fingers[i +
                                                                                1]._fingerIndex and self.fingers[i].fret < self.fingers[i+1].fret
            if maxIndexFingerIsLower:
                return False

            fingerDistanceIsTooLarge = abs(self.fingers[i].fret - self.fingers[i+1].fret) > 2 * abs(
                self.fingers[i]._fingerIndex - self.fingers[i+1]._fingerIndex)
            if fingerDistanceIsTooLarge:
                return False

        return True

    def calculateHandPosition(self) -> int:
        """
        calculate the hand position. 计算手型的位置
        :return: hand position, which means the fret number of index finger. 手的位置，也就是食指所在的品格
        """
        handPosition = 0
        minFingerIndex = 4
        for finger in self.fingers:
            if 0 < finger._fingerIndex < minFingerIndex:
                minFingerIndex = finger._fingerIndex
                handPosition = finger.fret

        handPosition -= (minFingerIndex - 1)
        return handPosition
