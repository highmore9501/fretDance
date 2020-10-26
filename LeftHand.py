import math


class FretDance:
    """
    左手主要包括几个概念：
    1.把位，也就是第一指所在的品位
    2.四个手指.每个手指状态分悬空与按弦，品位满足4>=3>=2>=1
    3.空弦
    4.把位切换
    5.横按。1指可以在横按状态，这时1指可以同时有多个同品的触弦点。
    默认弦距为0.85cm，品格高为3.637
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

    def changeBarre(self, barre):
        """
        切换把位，默认所有手指全部抬起来
        :param barre: 把位数
        """
        self.handPosition = barre
        self.fingerA.fret = self.handPosition
        self.fingerB.fret = self.fingerA.fret + 1
        self.fingerC.fret = self.fingerA.fret + 2
        self.fingerD.fret = self.fingerA.fret + 3
        self.fingerA.press = 0
        self.fingerB.press = 0
        self.fingerC.press = 0
        self.fingerD.press = 0

    def fingerMoveTo(self, fingerNumber, string, fret):
        """
        完成按弦动作,返回弦，品，使用手指，以及消耗的行动力
        :param fingerNumber: 第几指
        :param string: 目标弦
        :param fret: 目标品
        """
        finger = self.allFinger[fingerNumber]
        fingerStringDistance = abs(finger.string - string) * self.stringDistance
        fingerFretDistance = abs(finger.fret - fret) * self.fretDistance
        distance = math.sqrt(math.pow(fingerStringDistance, 2) + math.pow(fingerFretDistance, 2))
        index = self.allFinger.index(finger)
        barre = fret - index
        if fret == 0:
            actionPoint = 0
        elif distance > 1.5 * self.fretDistance:
            self.changeBarre(barre)
            finger.string = string
            finger.fret = fret
            actionPoint = 4 * self.fretDistance
        else:
            finger.string = string
            finger.fret = fret
            actionPoint = distance
        finger.press = 1
        return [string, fret, self.allFinger.index(finger) + 1], actionPoint

    def handMoveTo(self, position):
        """
        将整个手移动到某个手型，然后计算消耗的行动力，以及每个手指按在哪里
        :param position:
        :return:
        """
        pass

    def fingerDistance(self, fingerA, fingerB):
        """
        计算两个手指按弦点之间的距离，如果其中一指是在横按，侧取第三弦点
        :param fingerA:
        :param fingerB:
        :return: 返回距离
        """
        distance = 0.0
        fingerStringDistance = abs(fingerA.string - fingerB.string) * self.stringDistance
        fingerFretDistance = abs(fingerA.fret - fingerB.fret) * self.fretDistance
        if fingerA.press == 0 or fingerB.press == 0:
            return distance
        elif fingerA.press == 1 and fingerB.press == 1:
            distance = math.sqrt(math.pow(fingerStringDistance, 2) + math.pow(fingerFretDistance, 2))
            return distance
        elif fingerA.press > 1:
            distance = math.sqrt(math.pow(abs(3 - fingerB.string), 2) + math.pow(fingerFretDistance, 2))
            return distance
        elif fingerB.press > 1:
            distance = math.sqrt(math.pow(abs(3 - fingerA.string), 2) + math.pow(fingerFretDistance, 2))
            return distance
        else:
            raise ValueError("不能同时有两个手指横按")

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
        if self.press == 0:
            return self.point
        elif self.press == 1:
            self.point.append([self.string, self.fret])
            return self.point
        else:
            for i in range(self.press):
                self.point.append([i + 1, self.fret])
            return self.point

    def moveAndPress(self, string, fret, press=1):
        self.string = string
        self.fret = fret
        self.press = press
        self.touchPoint()
