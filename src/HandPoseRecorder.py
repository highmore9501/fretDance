from .hand.LeftHand import LeftHand
import copy
import json


class HandPoseRecorder():
    """
    a recorder for hand pose. 一个手势记录器
    """

    def __init__(self) -> None:
        self.handPoseList = []
        self.currentEntropy = 0.0
        self.entropys = [0.0]
        self.real_time = [0.0]

    def addHandPose(self, handPose: LeftHand, entropy: float, real_time: float) -> None:
        self.handPoseList.append(handPose)
        self.currentEntropy += entropy
        self.entropys.append(self.currentEntropy)
        self.real_time.append(real_time)

    def currentHandPose(self) -> LeftHand:
        return self.handPoseList[-1]

    def outputCurrent(self, showOpenFinger: bool = False) -> None:
        if len(self.handPoseList) > 0:
            print("Entropy: ", self.currentEntropy)
            print("real_time: ", self.real_time[-1])
            self.handPoseList[-1].output(showOpenFinger)

    def output(self, showOpenFinger: bool = False) -> None:
        for i in range(1, len(self.handPoseList)):
            print("Entropy: ", self.entropys[i])
            print("real_time: ", self.real_time[i])
            self.handPoseList[i].output(showOpenFinger)

    def save(self, jsonFilePath: str):
        handsDict = []
        for i in range(1, len(self.handPoseList)):
            handInfo = []
            real_time = self.real_time[i]
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
                "real_time": real_time,
                "leftHand": handInfo
            })

        with open(jsonFilePath, 'w') as f:
            json.dump(handsDict, f)


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
        self.preHandPoseRecordPool = copy.deepcopy(self.curHandPoseRecordPool)
        self.curHandPoseRecordPool = []

    def append(self, handPoseRecorder: HandPoseRecorder) -> None:
        current_size = len(self.curHandPoseRecordPool)
        current_HandPoseRecord_is_largest = current_size > 0 and handPoseRecorder.currentEntropy >= self.curHandPoseRecordPool[
            -1].currentEntropy
        # if the pool is full and the entropy of the new handPoseRecorder is greater than the entropy of the last element in the pool, return directly.
        if current_size == self.size and current_HandPoseRecord_is_largest:
            return None

        # insert the new handPoseRecorder into the curHandPoseRecordPool at the appropriate position.
        if current_size == 0 or (current_size < self.size and current_HandPoseRecord_is_largest):
            self.curHandPoseRecordPool.append(handPoseRecorder)
        else:
            for i in range(len(self.curHandPoseRecordPool)):
                if handPoseRecorder.currentEntropy < self.curHandPoseRecordPool[i].currentEntropy:
                    self.curHandPoseRecordPool.insert(i, handPoseRecorder)
                    break

        # if the length of curHandPoseRecordPool is greater than size, pop the last element.
        if len(self.curHandPoseRecordPool) > self.size:
            self.curHandPoseRecordPool.pop()
