from typing import List

rightFingers = {
    "p": 0,
    "i": 1,
    "m": 2,
    "a": 3
}


class RightHand():
    def __init__(self, usedFingers: List[str], rightFingerPositions: List[int]):
        self.usedFingers = usedFingers
        self.rightFingerPositions = rightFingerPositions
        # 手掌的位置由右手中指的位置来决定
        self.rightHandPosition = rightFingerPositions[2]
        self.afterPlayed()

    def validateRightHand(self) -> bool:
        usedString = []
        for finger in self.usedFingers:
            usedString.append(self.rightFingerPositions[rightFingers[finger]])
            # 检测是否有pima以外的手指
            if finger not in rightFingers:
                return False

        # 不能有重复的弦被拨动
        if len(usedString) != len(set(usedString)):
            return False

        for i in range(3):
            # 检测手指的位置是否从左到右递减
            if self.rightFingerPositions[i] < self.rightFingerPositions[i+1]:
                return False

        return True

    def caculateDiff(self, otherRightHand: "RightHand") -> int:
        # 每只手在转化到下一个手型时，必须先将ima手指归位
        diff = 0
        for i in range(4):
            diff += abs(self.afterPlayedRightFingerPositions[i] -
                        otherRightHand.rightFingerPositions[i])
        # 检测两只手的usedFingers相同的元素个数有多少
        common_elements = set(self.usedFingers).intersection(
            set(otherRightHand.usedFingers))
        same_finger_count = len(common_elements)

        diff += 3 * same_finger_count

        return diff

    def afterPlayed(self):
        # 如果没有手指拨弦或者只有p指拨弦，则不需要调整
        if len(self.usedFingers) == 0 or (len(self.usedFingers) == 1 and "p" in self.usedFingers):
            self.afterPlayedRightHandPosition = self.rightHandPosition
            self.afterPlayedRightFingerPositions = self.rightFingerPositions
            return

        self.afterPlayedRightFingerPositions = self.rightFingerPositions.copy()

        # 根据ima手指的位置来调整手掌的位置
        if "i" in self.usedFingers:
            if "m" not in self.usedFingers and self.afterPlayedRightFingerPositions[2] < self.rightFingerPositions[1]-1:
                self.afterPlayedRightFingerPositions[2] = self.rightFingerPositions[1]-1
            if "a" not in self.usedFingers and self.afterPlayedRightFingerPositions[3] < self.rightFingerPositions[1]-2:
                self.afterPlayedRightFingerPositions[3] = self.rightFingerPositions[1]-2
        elif "m" in self.usedFingers:
            if "a" not in self.usedFingers and self.afterPlayedRightFingerPositions[3] < self.rightFingerPositions[2]-1:
                self.afterPlayedRightFingerPositions[3] = self.rightFingerPositions[2]-1
            if "i" not in self.usedFingers and self.afterPlayedRightFingerPositions[1] > self.rightFingerPositions[2]+1:
                self.afterPlayedRightFingerPositions[1] = self.rightFingerPositions[2]+1
        else:
            if "i" not in self.usedFingers and self.afterPlayedRightFingerPositions[1] > self.rightFingerPositions[3]+2:
                self.afterPlayedRightFingerPositions[1] = self.rightFingerPositions[3]+2
            if "m" not in self.usedFingers and self.afterPlayedRightFingerPositions[2] > self.rightFingerPositions[3]+1:
                self.afterPlayedRightFingerPositions[2] = self.rightFingerPositions[3]+1

        self.afterPlayedRightHandPosition = self.rightFingerPositions[2]

    def output(self):
        print("RightHand: ", self.usedFingers, self.rightFingerPositions)
