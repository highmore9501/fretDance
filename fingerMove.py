from LeftHand import *


class fingerMove:

    def __init__(self):
        self.leftHand = LeftHand()

    def moveTo(self, string, fret):
        """
        用当前左手去按给点的位置，返回最优方案需要消耗的行动力，同时改变左手位置
        :param string:
        :param fret:
        :return:
        """
        # 计算用哪个手指移动行动力最低
        firstFinger = self.leftHand.allFinger[0]
        actionPoint = self.leftHand.calFingerMove(firstFinger,string, fret)
        useFingerNumber = 0

        for i in range(1, 4):
            currentFinger = self.leftHand.allFinger[i]
            currentPoint = self.leftHand.calFingerMove(currentFinger,string, fret)
            if currentPoint < actionPoint:
                actionPoint = currentPoint
                useFingerNumber = i

        useFinger = self.leftHand.allFinger[useFingerNumber]  # 确定最优指
        self.leftHand.fingerMoveTo(useFinger, string, fret)  # 完成动作，改变手的状态
        return useFingerNumber,actionPoint  # 返回最优指数字,消耗行动力

    def calMoveTo(self, notePositions):
        """
        计算同一个音不同按法消耗的行动力，得到最优解
        :param notePositions: 同音位置列表
        :return: 最优note位置
        """
        pass
