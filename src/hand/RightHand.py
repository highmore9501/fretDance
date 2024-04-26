from typing import List

rightFingers = {
    "p": 0,
    "i": 1,
    "m": 2,
    "a": 3
}

handPositionToFingerPositions = {
    0: {"p": (1, 2), "i": (0, 1), "m": (0, 1), "a": (0, 1)},
    1: {"p": (2, 4), "i": (0, 2), "m": (0, 1), "a": (0, 1)},
    2: {"p": (3, 5), "i": (1, 3), "m": (0, 2), "a": (0, 2)},
    3: {"p": (4, 5), "i": (3, 5), "m": (2, 4), "a": (2, 4)}
}


class RightHand():
    def __init__(self, usedFingers: List[str], rightFingerPositions: List[int], isArpeggio: bool = False):
        self.usedFingers = usedFingers
        self.rightFingerPositions = rightFingerPositions
        # 手掌的位置由右手中指的位置来决定
        self.rightHandPosition = self.caculateHandPosition()
        self.isArpeggio = isArpeggio
        self.afterPlayed()

    def caculateHandPosition(self, rightFingerPositions=None) -> int:
        if rightFingerPositions == None:
            rightFingerPositions = self.rightFingerPositions

        results = [2, 1, 0, 3]
        for hand_position in results:
            for finger in ['p', 'i', 'm', 'a']:
                min_pos, max_pos = handPositionToFingerPositions[hand_position][finger]
                if not min_pos <= rightFingerPositions[rightFingers[finger]] <= max_pos:
                    break
            else:
                return hand_position
        return -1  # 返回-1表示没有找到满足条件的hand_position

    def validateRightHand(self, usedFingers=None, rightFingerPositions=None) -> bool:
        if rightFingerPositions == None:
            rightFingerPositions = self.rightFingerPositions
        if usedFingers == None:
            usedFingers = self.usedFingers

        usedString = []
        rightHandPosition = self.caculateHandPosition(rightFingerPositions)

        if rightHandPosition == -1:
            return False
        for finger in usedFingers:
            usedString.append(rightFingerPositions[rightFingers[finger]])
            # 检测是否有pima以外的手指
            if finger not in rightFingers:
                return False

        # 不能有重复的弦被拨动
        if len(usedString) != len(set(usedString)):
            return False

        for i in range(3):
            # 检测手指的位置是否从左到右递减
            if rightFingerPositions[i] < rightFingerPositions[i+1]:
                return False

        return True

    def caculateDiff(self, otherRightHand: "RightHand") -> int:
        diff = 0
        # 计算手指改变所在弦位置的情况，每有移动一根弦距就加1单位的diff
        for i in range(4):
            diff += abs(self.rightFingerPositions[i] -
                        otherRightHand.rightFingerPositions[i])

        # 检测两只手的usedFingers相同的元素个数有多少
        common_elements = set(self.usedFingers).intersection(
            set(otherRightHand.usedFingers))
        same_finger_count = len(common_elements)

        # 检测重复使用的手指中有没有P指
        if 0 in common_elements:
            diff += 1
            same_finger_count -= 1

        # 其它重复使用的手指按3单位diff来算，也就是不鼓励除P指以外的手指重复使用
        diff += 3 * same_finger_count

        # 不考虑手掌移动，因为手掌是由身体来带动的，它的移动比手指移动要来得轻松
        return diff

    def afterPlayed(self):
        self.afterPlayedRightFingerPositions = self.rightFingerPositions.copy()

        # 根据ima手指的位置来调整手掌的位置
        if "i" in self.usedFingers:
            if "m" not in self.usedFingers and self.afterPlayedRightFingerPositions[2] < self.rightFingerPositions[1]-1:
                self.afterPlayedRightFingerPositions[2] = self.rightFingerPositions[1]-1
            if "a" not in self.usedFingers and self.afterPlayedRightFingerPositions[3] < self.rightFingerPositions[1]-2:
                self.afterPlayedRightFingerPositions[3] = self.rightFingerPositions[1]-2
            if "p" not in self.usedFingers and self.afterPlayedRightFingerPositions[0] > self.rightFingerPositions[1]+2:
                self.afterPlayedRightFingerPositions[0] = self.rightFingerPositions[1]+2
        elif "m" in self.usedFingers:
            if "a" not in self.usedFingers and self.afterPlayedRightFingerPositions[3] < self.rightFingerPositions[2]-1:
                self.afterPlayedRightFingerPositions[3] = self.rightFingerPositions[2]-1
            if "i" not in self.usedFingers and self.afterPlayedRightFingerPositions[1] > self.rightFingerPositions[2]+1:
                self.afterPlayedRightFingerPositions[1] = self.rightFingerPositions[2]+1
            if "p" not in self.usedFingers and self.afterPlayedRightFingerPositions[0] > self.  rightFingerPositions[2]+3:
                self.afterPlayedRightFingerPositions[0] = self.rightFingerPositions[2]+3
        elif "a" in self.usedFingers:
            if "i" not in self.usedFingers and self.afterPlayedRightFingerPositions[1] > self.rightFingerPositions[3]+2:
                self.afterPlayedRightFingerPositions[1] = self.rightFingerPositions[3]+2
            if "m" not in self.usedFingers and self.afterPlayedRightFingerPositions[2] > self.rightFingerPositions[3]+1:
                self.afterPlayedRightFingerPositions[2] = self.rightFingerPositions[3]+1
            if "p" not in self.usedFingers and self.afterPlayedRightFingerPositions[0] > self.rightFingerPositions[3]+4:
                self.afterPlayedRightFingerPositions[0] = self.rightFingerPositions[3]+4
        elif "p" in self.usedFingers:
            if "i" not in self.usedFingers and self.afterPlayedRightFingerPositions[1] < self.rightFingerPositions[0]-2:
                self.afterPlayedRightFingerPositions[1] = self.rightFingerPositions[0]-2
            if "m" not in self.usedFingers and self.afterPlayedRightFingerPositions[2] < self.rightFingerPositions[0]-3:
                self.afterPlayedRightFingerPositions[2] = self.rightFingerPositions[0]-3
            if "a" not in self.usedFingers and self.afterPlayedRightFingerPositions[3] < self.rightFingerPositions[0]-4:
                self.afterPlayedRightFingerPositions[3] = self.rightFingerPositions[0]-4

    def output(self):
        print("RightHand: ", self.usedFingers, self.rightFingerPositions)
