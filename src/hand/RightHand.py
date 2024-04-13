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

    def validateRightHand(self) -> bool:
        usedString = []
        for finger in self.usedFingers:
            usedString.append(self.rightFingerPositions[rightFingers[finger]])
            if finger not in rightFingers:
                return False

        if len(usedString) != len(set(usedString)):
            return False

        for i in range(3):
            if self.rightFingerPositions[i] < self.rightFingerPositions[i+1]:
                return False

        return True

    def caculateDiff(self, otherRightHand: "RightHand") -> int:
        diff = 0
        for i in range(4):
            diff += abs(self.rightFingerPositions[i] -
                        otherRightHand.rightFingerPositions[i])
        # 检测两只手的usedFingers相同的元素个数有多少
        common_elements = set(self.usedFingers).intersection(
            set(otherRightHand.usedFingers))
        same_finger_count = len(common_elements)

        diff += 3 * same_finger_count

        return diff

    def output(self):
        print("RightHand: ", self.usedFingers, self.rightFingerPositions)
