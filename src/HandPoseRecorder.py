from .hand.LeftHand import LeftHand
from .hand.RightHand import RightHand
import copy
import json


class HandPoseRecorder():
    """
    a recorder for hand pose. 一个手势记录器
    """

    def __init__(self) -> None:
        self.handPoseList = []
        self.currentEntropy = 0.0
        self.entropys = []
        self.real_ticks = []

    def addHandPose(self, handPose: LeftHand, entropy: float, real_tick: float) -> None:
        self.handPoseList.append(handPose)
        self.currentEntropy += entropy
        self.entropys.append(self.currentEntropy)
        self.real_ticks.append(real_tick)

    def currentHandPose(self) -> LeftHand:
        return self.handPoseList[-1]

    def outputCurrent(self, showOpenFinger: bool = False) -> None:
        if len(self.handPoseList) > 0:
            print("Entropy: ", self.currentEntropy)
            print("real_tick: ", self.real_ticks[-1])
            self.handPoseList[-1].output(showOpenFinger)

    def output(self, showOpenFinger: bool = False) -> None:
        for i in range(1, len(self.handPoseList)):
            print("Entropy: ", self.entropys[i])
            print("real_tick: ", self.real_ticks[i])
            self.handPoseList[i].output(showOpenFinger)

    def save(self, jsonFilePath: str):
        handsDict = []
        for i in range(1, len(self.handPoseList)):
            handInfo = []
            real_tick = self.real_ticks[i]
            leftHand = self.handPoseList[i]
            for finger in leftHand.fingers:
                fingerIndex = finger._fingerIndex
                fingerInfo = {
                    "stringIndex": finger.stringIndex,
                    "fret": finger.fret,
                    "press": finger.press
                }
                handInfo.append({
                    "fingerIndex": fingerIndex,
                    "fingerInfo": fingerInfo
                })

            handsDict.append({
                "real_tick": real_tick,
                "leftHand": handInfo
            })

        with open(jsonFilePath, 'w') as f:
            json.dump(handsDict, f)


class RightHandRecorder():
    def __init__(self) -> None:
        self.handPoseList = []
        self.currentEntropy = 0
        self.entropys = []
        self.real_ticks = []

    def addHandPose(self, handPose: RightHand, entropy: int, real_tick: float) -> None:
        self.handPoseList.append(handPose)
        self.currentEntropy += entropy
        self.entropys.append(self.currentEntropy)
        self.real_ticks.append(real_tick)

    def currentHandPose(self) -> RightHand:
        return self.handPoseList[-1]

    def save(self, jsonFilePath: str):
        handsDict = []
        for i in range(1, len(self.handPoseList)):
            handInfo = []
            real_tick = self.real_ticks[i]
            rightHand = self.handPoseList[i]
            handInfo = {
                "usedFingers": rightHand.usedFingers,
                "rightFingerPositions": rightHand.rightFingerPositions,
                "rightHandPosition": rightHand.rightHandPosition,
                "afterPlayedRightFingerPositions": rightHand.afterPlayedRightFingerPositions
            }

            handsDict.append({
                "real_tick": real_tick,
                "rightHand": handInfo
            })

        with open(jsonFilePath, 'w') as f:
            json.dump(handsDict, f)

    def output(self):
        print("Entropy: ", self.currentEntropy)
        for i in range(1, len(self.handPoseList)):
            print("Entropy: ", self.entropys[i])
            print("real_tick: ", self.real_ticks[i])
            self.handPoseList[i].output()


class HandPoseRecordPool():
    """
    a pool including hand pose recorders. 包含手势记录器的池子
    :param size: size of the pool. 池子的大小
    """

    def __init__(self, size: int = 10) -> None:
        self.curHandPoseRecordPool = []
        self.preHandPoseRecordPool = []
        self.size = size

    def readyForRecord(self) -> None:
        self.preHandPoseRecordPool = self.curHandPoseRecordPool[:]
        self.curHandPoseRecordPool = []

    def check_insert_index(self, entropy: float) -> int:
        current_size = len(self.curHandPoseRecordPool)
        current_HandPoseRecord_is_largest = current_size > 0 and entropy >= self.curHandPoseRecordPool[
            -1].currentEntropy
        if current_size == self.size and current_HandPoseRecord_is_largest:
            return -1

        if current_size == 0 or (current_size < self.size and current_HandPoseRecord_is_largest):
            return current_size

        for i in range(current_size):
            if entropy < self.curHandPoseRecordPool[i].currentEntropy:
                return i

    def insert_new_hand_pose_recorder(self, newHandPoseRecorder, index):
        # 插入新的元素
        self.curHandPoseRecordPool.insert(index, newHandPoseRecorder)

        # 如果插入后的大小超过了 self.size，移除最后一个元素
        if len(self.curHandPoseRecordPool) > self.size:
            self.curHandPoseRecordPool.pop()
