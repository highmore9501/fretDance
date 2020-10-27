import math
from calculate import lists_combiantions,classfiyChord,barreChord,noBarreChord


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

    def changeBarre(self, fingerNumber, string, fret):
        """
        切换把位，默认所有手指全部抬起来
        :param fret: 横按指放在第几品
        :param string: 横按指按的最高弦
        :param fingerNumber: 使用第几指横横按
        """
        self.handPosition = fret - fingerNumber
        self.fingerA.fret = self.handPosition
        self.fingerB.fret = self.fingerA.fret + 1
        self.fingerC.fret = self.fingerA.fret + 2
        self.fingerD.fret = self.fingerA.fret + 3
        self.allFinger[fingerNumber].string = string



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
        return [string, fret, self.allFinger.index(finger) + 1], actionPoint

    def handMoveTo(self, position):
        """
        将整个手移动到某个手型，然后计算消耗的行动力，以及每个手指按在哪里
        :param position:当前和弦需要按的位置列表，类似([5, 7], [4, 7], [3, 5], [2, 5], [1, 5])
        :return:返回多个dancer，也就是手型

        分析过程：
        先将整个position里的空弦音去掉，不用处理（默认空弦不影响左手，不消耗行动力）
        position里其它的音，先看音符位置来决定是否需要横按：
            音符超过4个，必须使用横按：
                有相同品格，且相同品格是最小品格:
                先使用1指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
            有相同品格，且品格不是最小品格：
                相同品格所在的弦是邻近弦：
                    相同品格所在的弦是所有弦里最高的：
                        使用4指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
                        使用3指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
                        使用2指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
                    使用3指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
            音符不超过4个，分情况：
                使用横按的话：
                    有相同品格，且相同品格是最小品格:
                        先使用1指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
                    有相同品格，且品格不是最小品格：
                        相同品格所在的弦是邻近弦：
                            相同品格所在的弦是所有弦里最高的：
                                使用4指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
                                使用3指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
                                使用2指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
                            使用3指横按相同品格，生成新的dancer，然后遍历余下三指按其它品格，调用fingerMoveTo，生成移动后的dancer
                不使用横按：
                    使用product函数得到所有每指只按一个音的可能组合，复制原手型生成新的dancer,然后调用fingerMoveTo方法，生成移动后的dancer

        用上述所有情况生成的所有dancer生成一个列表，并返回
        """
        dancers = []
        positionList = list(position)
        # 去掉空弦音
        for item in positionList:
            if item[1] == 0:
                positionList.remove(item)

        positionType = classfiyChord(positionList)  # 判断和弦类型
        if positionType == 'a':
            # 按1指横按处理
            dancers.append(barreChord(self, 1, positionList))
        elif positionType == 'b':
            #  按2,3,4指横按处理
            dancers.append(barreChord(self, 2, positionList))
            dancers.append(barreChord(self, 3, positionList))
            dancers.append(barreChord(self, 4, positionList))
        else:
            #  按不能横按，但实际上又按不完全部的音符来处理
            return dancers
        #  按无横按处理
        dancers.append(noBarreChord(self, position))
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
