from src.hand.LeftHand import LeftHand


class HandPoseRecorder():
    """
    a recorder for hand pose. 一个手势记录器
    """

    def __init__(self) -> None:
        self.handPoseList = []
        self.currentEntropy = 0.0
        self.entropys = [0.0]
        self.beats = [0.0]

    def addHandPose(self, handPose: LeftHand, entropy: float, beat: float) -> None:
        self.handPoseList.append(handPose)
        self.currentEntropy += entropy
        self.entropys.append(self.currentEntropy)
        self.beats.append(beat)

    def currentHandPose(self) -> LeftHand:
        return self.handPoseList[-1]

    def outputCurrent(self) -> None:
        if len(self.handPoseList) > 0:
            print("Entropy: ", self.currentEntropy)
            print("Beat: ", self.beats[-1])
            self.handPoseList[-1].output()

    def output(self) -> None:
        for i in range(1, len(self.handPoseList)):
            print("Entropy: ", self.entropys[i])
            print("Beat: ", self.beats[i])
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
        self.preHandPoseRecordPool = self.curHandPoseRecordPool
        self.curHandPoseRecordPool = []

    def append(self, handPoseRecorder: HandPoseRecorder) -> None:
        # if the pool is full and the entropy of the new handPoseRecorder is greater than the entropy of the last element in the pool, return directly. 如果池子已经满了，而且新进入的handPoseRecorder的entropy比池子中的最后一个元素的entropy还要大，直接返回。
        if len(self.curHandPoseRecordPool) == self.size and handPoseRecorder.currentEntropy >= self.curHandPoseRecordPool[-1].currentEntropy:
            return None

        # insert the new handPoseRecorder into the curHandPoseRecordPool at the appropriate position. 将新加入的handPoseRecorder加入到curHandPoseRecordPool中的适当位置。
        if len(self.curHandPoseRecordPool) == 0 or handPoseRecorder.currentEntropy >= self.curHandPoseRecordPool[-1].currentEntropy:
            self.curHandPoseRecordPool.append(handPoseRecorder)
        # search the elements in the queue, find the first element whose entropy is greater than the entropy of the new handPoseRecorder, and insert the new handPoseRecorder into the position of this element. 查询队列中的元素，找到第一个entropy比新加入的handPoseRecorder的entropy大的元素，将新加入的handPoseRecorder插入到这个元素的位置。
        else:
            for i in range(len(self.curHandPoseRecordPool)):
                if handPoseRecorder.currentEntropy < self.curHandPoseRecordPool[i].currentEntropy:
                    self.curHandPoseRecordPool.insert(i, handPoseRecorder)
                    break

        # if the length of curHandPoseRecordPool is greater than size, pop the last element. 如果curHandPoseRecordPool的长度超过size，将最后一个元素弹出。
        if len(self.curHandPoseRecordPool) > self.size:
            self.curHandPoseRecordPool.pop()
