from LeftHand import *
from fingerMove import *

F = fingerMove()
F.leftHand.fingerA.moveAndPress(2,1,1)
F.leftHand.fingerB.moveAndPress(4,2,1)
F.leftHand.fingerC.moveAndPress(5,3,1)
fingerNumber, actionPoint = F.moveTo(3,7)

for finger in F.leftHand.allFinger:
    print("第{}指现在在{}弦{}品,状态是{}".format(F.leftHand.allFinger.index(finger),finger.string,finger.fret,finger.press))

print("整个动作消耗行动力为{}".format(actionPoint))
