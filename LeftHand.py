import math

from calculate import classifyChord
from chordToFinger import *


class FretDance:
    """
    FretDance是表示左手的状态，也就是表现在和弦谱上的左手指法，主要包括几个概念：
    1.把位，也就是第一指所在的品位
    2.四个手指.每个手指状态分悬空与按弦，品位满足4>=3>=2>=1
    3.空弦
    4.横按。 这个功能写到finger()里去
    默认弦距为0.85cm，品格高为3.637，暂不考虑品高因品格升高而变小的影响

    FretDance还包括以下属性：
    trace:用来记录
    """

    def __init__(self, stringDistance=0.85, fretDistance=3.637):
        """
        初始化左手，位置在第一把位，四指悬空，分别在1/2/3/4品。
        """
        self.handPosition = 1
        self.fingerA = LeftFinger()
        self.fingerA.fret = self.handPosition
        self.fingerB = LeftFinger()
        self.fingerB.fret = self.fingerA.fret + 1
        self.fingerC = LeftFinger()
        self.fingerC.fret = self.fingerA.fret + 2
        self.fingerD = LeftFinger()
        self.fingerD.fret = self.fingerA.fret + 3
        self.stringDistance = stringDistance
        self.fretDistance = fretDistance
        self.allFinger = [self.fingerA, self.fingerB, self.fingerC, self.fingerD]
        self.trace = []
        self.entropy = 0

    def changeBarre(self, fingerNumber, string, fret):
        """
        换把位，默认所有手指全部抬起来,整体移动
        :param fret: 横按指放在第几品
        :param string: 横按指按的最高弦
        :param fingerNumber: 使用第几指横横按，1/2/3/4
        """
        self.handPosition = fret - fingerNumber - 1
        self.fingerA.fret = self.handPosition
        self.fingerB.fret = self.fingerA.fret + 1
        self.fingerC.fret = self.fingerA.fret + 2
        self.fingerD.fret = self.fingerA.fret + 3
        for finger in self.allFinger:
            finger.string = string
            finger.press = 0

    def fingerMoveTo(self, fingerNumber, string, fret, press=1):
        """
        完成按弦动作,返回消耗的行动力
        :param press: 手指的按弦状态
        :param fingerNumber: 第几指，分别有1/2/3/4四根手指
        :param string: 目标弦
        :param fret: 目标品
        如果要移动的距离过大，就直接换把,然后按弦
        如果目标位置是空弦，或者不用按，就啥也不干，只松开手指
        如果目标位置距离合适，移指，然后按弦
        """
        finger = self.allFinger[fingerNumber - 1]
        fingerStringDistance = abs(finger.string - string) * self.stringDistance
        fingerFretDistance = abs(finger.fret - fret) * self.fretDistance
        distance = math.sqrt(math.pow(fingerStringDistance, 2) + math.pow(fingerFretDistance, 2))
        if distance > 1.5 * self.fretDistance:  # 换把
            self.changeBarre(fingerNumber, string, fret)
            finger.press = press
            actionPoint = 4 * self.fretDistance
        elif fret == 0 or press == 0:  # 空弦或不按，不移指
            actionPoint = 0
            finger.press = 0
        else:  # 不换把，只移指
            actionPoint = distance
            finger.string = string
            finger.fret = fret
            finger.press = press
        return actionPoint

    def touchPoints(self):
        """
        得到当前手型能弹奏的位置，每弦一个音，都取当前弦上被按的最高位置；如果某弦没有被按，则取空弦音。
        :return:
        """
        touchPoint = list(set(self.fingerA.point + self.fingerB.point + self.fingerC.point + self.fingerD.point))
        result = []
        resultAppend = result.append
        for i in range(6):
            frets = []
            for [string, fret] in touchPoint:
                if string == i + 1:
                    frets.append(fret)
                else:
                    frets.append(0)
            resultAppend([i + 1, min(frets)])
        return result

    def handMoveTo(self, chord):
        """
        将整个手移动到某个手型，然后计算消耗的行动力，以及每个手指按在哪里
        :param chord:当前和弦需要按的位置列表，类似([5, 7], [4, 7], [3, 5], [2, 5], [1, 5])
        :return:返回多个dancer，也就是手型
        """
        dancers = []
        positionList = list(chord)
        # 去掉空弦音
        # for item in positionList:
        #     if item[1] == 0:
        #         positionList.remove(item)

        ChordType = classifyChord(positionList)  # 判断和弦类型
        positionType = []
        for item in ChordType:
            positionType.append(item[1])

        if positionType == [0]:
            dancers.append(chord2Finger00(self))
        if positionType == [1]:
            dancers.append(chord2Finger01(self, chord))
        if positionType == [2]:
            dancers.append(chord2Finger02(self, chord))
        if positionType == [1, 1]:
            dancers.append(chord2Finger03(self, chord))
        if positionType == [3]:
            dancers.append(chord2Finger04(self, chord))
        if positionType == [2, 1]:
            dancers.append(chord2Finger05(self, chord))
        if positionType == [1, 2]:
            dancers.append(chord2Finger06(self, chord))
        if positionType == [1, 1, 1]:
            dancers.append(chord2Finger07(self, chord))
        if positionType == [4] or positionType == [5] or positionType == [6]:
            dancers.append(chord2Finger08(self, chord))
        if positionType == [1, 3]:
            dancers.append(chord2Finger09(self, chord))
        if positionType == [2, 2]:
            dancers.append(chord2Finger10(self, chord))
        if positionType == [3, 1] or positionType == [4, 1] or positionType == [5, 1]:
            dancers.append(chord2Finger11(self, chord))
        if positionType == [1, 1, 2]:
            dancers.append(chord2Finger12(self, chord))
        if positionType == [1, 2, 1]:
            dancers.append(chord2Finger13(self, chord))
        if positionType == [2, 1, 1]:
            dancers.append(chord2Finger14(self, chord))
        if positionType == [1, 1, 1, 1]:
            dancers.append(chord2Finger15(self, chord))
        if positionType == [1, 4]:
            dancers.append(chord2Finger16(self, chord))
        if positionType == [2, 3]:
            dancers.append(chord2Finger17(self, chord))
        if positionType == [3, 2]:
            dancers.append(chord2Finger18(self, chord))
        if positionType == [4, 2]:
            dancers.append(chord2Finger19(self, chord))
        if positionType == [1, 1, 3]:
            dancers.append(chord2Finger20(self, chord))
        if positionType == [1, 1, 1, 3]:
            dancers.append(chord2Finger21(self, chord))
        if positionType == [2, 1, 2]:
            dancers.append(chord2Finger22(self, chord))
        if positionType == [2, 2, 1]:
            dancers.append(chord2Finger23(self, chord))
        if positionType == [3, 1, 1]:
            dancers.append(chord2Finger24(self, chord))
        if positionType == [1, 1, 1, 2]:
            dancers.append(chord2Finger25(self, chord))
        if positionType == [2, 1, 1, 1]:
            dancers.append(chord2Finger26(self, chord))
        if positionType == [2, 1, 1, 1]:
            dancers.append(chord2Finger27(self, chord))
        if positionType == [3, 3]:
            dancers.append(chord2Finger28(self, chord))
        if positionType == [2, 4]:
            dancers.append(chord2Finger29(self, chord))
        if positionType == [1, 5]:
            dancers.append(chord2Finger30(self, chord))
        if positionType == [1, 1, 4]:
            dancers.append(chord2Finger31(self, chord))
        if positionType == [2, 1, 3]:
            dancers.append(chord2Finger32(self, chord))
        if positionType == [3, 1, 2]:
            dancers.append(chord2Finger33(self, chord))
        if positionType == [4, 1, 1]:
            dancers.append(chord2Finger34(self, chord))
        if positionType == [2, 1, 1, 2]:
            dancers.append(chord2Finger35(self, chord))
        if positionType == [3, 1, 1, 1]:
            dancers.append(chord2Finger36(self, chord))

        return dancers

    def fingerDistance(self, fingerA, fingerB):
        """
        计算两个手指按弦点之间的距离，如果其中一指是在横按，侧取第三弦点
        :param fingerA:
        :param fingerB:
        :return: 返回距离
        """
        fingerStringDistance = abs(fingerA.string - fingerB.string) * self.stringDistance
        fingerFretDistance = abs(fingerA.fret - fingerB.fret) * self.fretDistance
        distance = math.sqrt(math.pow(fingerStringDistance, 2) + math.pow(fingerFretDistance, 2))
        if fingerA.fret == 0 or fingerB.fret == 0:
            return 0.0
        return distance

    def validation(self):
        if self.fingerDistance(self.fingerA, self.fingerB) > 1.5 * self.fretDistance:
            return False
        if self.fingerDistance(self.fingerB, self.fingerC) > 1.5 * self.fretDistance:
            return False
        if self.fingerDistance(self.fingerC, self.fingerD) > 1.5 * self.fretDistance:
            return False
        if self.fingerA.fret > self.fingerB.fret or self.fingerB.fret > self.fingerC.fret or self.fingerC.fret > self.fingerD.fret:
            return False
        else:
            return True


class LeftFinger:
    """
    左手手指，包含弦位，品位，按弦或横按状态
    string代表弦，fret代表品，弦和品合起来表示当前手指的指尖位置；
    point是一个列表，包含当前手指按到的位置；
    press代表按弦状态，各数值意义如下：
    0 表示悬空未按弦
    1 表示只按一个单音
    2 表示横按，按了从指尖位置到第一弦所有同品的音
    3 表示悬空小横按，按了从指尖位置开始往高音弦方向，同品的三个音；这个时候是把第一指节打横按下去，其实不太好按
    暂时不考虑悬空横按只按2个音的情况，在吉它上试过了，太难按
    """

    def __init__(self):
        self.string = 3
        self.fret = 1
        self.press = 0
        self.point = []

    def touchPoint(self):
        """
        计算此手指此时的按弦点
        :return: 按弦点列表，以[弦数,品格数]的形式来表示每个按弦点。
        """
        self.point = []

        if self.press == 1:
            self.point.append([self.string, self.fret])
        elif self.press == 2:
            self.point = []
            for i in range(self.string):
                self.point.append([i + 1, self.fret])
        elif self.press == 3:
            self.point = []
            for i in range(3):
                self.point.append([self.string - i, self.fret])

    def moveAndPress(self, string, fret, press=1):
        """
        移动手指，并生成新的触弦点
        :param string: 弦
        :param fret: 品
        :param press: 横按状态
        :return:
        """
        self.string = string
        self.fret = fret
        self.press = press
        self.touchPoint()
