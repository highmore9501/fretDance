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
    默认弦距为0.85cm，弦长为64.7954cm

    FretDance还包括以下属性：
    trace:用来记录
    """

    def __init__(self, ETC=1.0594630943592956, stringDistance=0.85, fullString=64.7954):
        """
        初始化左手，位置在第一把位，四指悬空，分别在1/2/3/4品。
        :param ETC: 平均律常数，也就是2的十二次方根
        :param stringDistance: 弦距，古典吉他每根弦之间的距离，单位是cm
        :param fullString:弦长，古典吉他的弦长，单位是cm
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
        self.fullString = fullString
        self.equalConstant = ETC
        self.allFinger = [self.fingerA, self.fingerB, self.fingerC, self.fingerD]
        self.traceNote = []
        self.traceFinger = []
        self.entropy = 0

    def stringLength(self, fret):
        """
        :param fret: 品格
        :return: 此品格的弦长
        """
        length = self.fullString / pow(self.equalConstant, fret)
        return length

    def recordTrace(self, fingerList, noPress=None):
        """
        :param fingerList:当前情况下所有用到的手指
        :param noPress: 所有的的空弦音列表，类似[[3,0],[4,0]]
        :return: 记录此时被弹响的音符位置
        """
        # newTrace = []
        # if noPress is not []:
        #     for item in noPress:
        #         newTrace.append([item[0], 0])

        # for fingerNumber in fingerList:
        #     finger = self.allFinger[fingerNumber - 1]
        #     if finger.press != 0:
        #         newTrace.append([finger.string, finger.fret])

        #  所有手指执行计算，得到各指的按弦
        touchPoints = []

        for fingerNumber in fingerList:
            finger = self.allFinger[fingerNumber-1]
            finger.touchPoint()
            touchPoints += finger.point
        # 整合各指按弦，去掉重复的按弦点

        if noPress:
            for item in noPress:
                touchPoints += [item]
            fingerList.append(0)

        self.traceNote.append(touchPoints)
        self.traceFinger.append(fingerList)

    def changeBarre(self, fingerNumber, string, fret, press=1):
        """
        换把位，默认所有手指全部抬起来,整体移动，然后按下横按的手指
        :param press: 大小横按或单按
        :param fret: 横按指放在第几品
        :param string: 横按指按的最高弦
        :param fingerNumber: 使用第几指横横按，1/2/3/4
        """
        self.handPosition = fret - fingerNumber + 1
        self.fingerA.fret = self.handPosition
        self.fingerB.fret = self.fingerA.fret + 1
        self.fingerC.fret = self.fingerA.fret + 2
        self.fingerD.fret = self.fingerA.fret + 3
        for finger in self.allFinger:
            finger.string = string
            finger.press = 0
        self.allFinger[fingerNumber - 1].press = press

    def fingerMoveTo(self, fingerNumber, string, fret, press=1):
        """
        完成按弦动作,返回消耗的行动力
        :param press: 手指的按弦状态
        :param fingerNumber: 第几指，分别有1/2/3/4四根手指
        :param string: 目标弦
        :param fret: 目标品
        如果要移动的距离过大，就直接换把,然后按弦
        如果目标位置是空弦，或者不用按，就啥也不干，只松开手指
        如果目标位置距离合适，移指，然后按弦，所有此时未按弦的手指，也会移弦位
        """

        finger = self.allFinger[fingerNumber - 1]
        fingerChangePoints = 0
        if finger.press != 0:
            fingerChangePoints = self.stringDistance
        fingerStringDistance = abs(finger.string - string) * self.stringDistance
        fingerFretDistance = abs(self.stringLength(finger.fret) - self.stringLength(fret))
        distance = math.sqrt(math.pow(fingerStringDistance, 2) + math.pow(fingerFretDistance, 2))
        if fret == 0 or press == 0:  # 空弦或不按，不移指
            actionPoint = 0
            finger.press = 0

        elif self.allFinger[0].fret - 1 <= fret <= self.allFinger[3].fret + 1:  # 要按的品在整个手掌+-1的范围内，移指
            currentMaxFret = self.allFinger[3].fret
            currentMinFret = self.allFinger[0].fret
            actionPoint = distance + fingerChangePoints

            for item in self.allFinger:
                # 没有按弦的手指会随着移指的动作，产生移动，移动不会超过当前最低到最高品的范围
                if item.press == 0:
                    item.string += string - finger.string
                if item.string > 6:
                    item.string = 6
                if item.string < 1:
                    item.string = 1

                item.fret += fret - finger.fret
                if item.fret > currentMaxFret:
                    item.fret = currentMaxFret
                if item.fret < currentMinFret:
                    item.fret = currentMinFret
                # 与当前手指目标位置同弦或低音弦，且品格更高的手指如果正在大横按，需要抬起来
                if item.press == 2 and item.string >= string and item.fret >= fret:
                    item.press = 0
                # 与当前手指目标位置同弦或者低三根弦，且品格更高的手指正在小横按，需要抬起来
                if item.press == 3 and string <= item.string <= string + 3 and item.fret >= fret:
                    item.press = 0
                # 与当前手指目标位置同弦，且品格更高的手指正在单按，需要抬起来
                if item.press == 1 and item.string == string and item.fret >= fret:
                    item.press = 0
            # 完成按弦动作
            finger.fret = fret
            finger.string = string
            finger.press = press

        else:  # 换把
            self.changeBarre(fingerNumber, string, fret)
            if fret <= 10:
                actionPoint = fingerFretDistance + fingerStringDistance + 4 * self.stringDistance
            else:
                actionPoint = 1.5 * fingerFretDistance + fingerStringDistance + 4 * self.stringDistance
        self.entropy += actionPoint

    def touchPoints(self):
        """
        得到当前手型能弹奏的位置，每弦一个音，都取当前弦上被按的最高位置；如果某弦没有被按，则取空弦音。
        :return:
        """
        #  所有手指执行计算，得到各指的按弦
        for finger in self.allFinger:
            finger.touchPoint()
        # 整合各指按弦，去掉重复的按弦点
        touchPoint = self.fingerA.point + self.fingerB.point + self.fingerC.point + self.fingerD.point

        result = []
        resultAppend = result.append

        for i in range(6):
            frets = []
            for [string, fret] in touchPoint:
                if string == i + 1:
                    frets.append(fret)
                else:
                    frets.append(0)
            try:
                resultAppend([i + 1, max(frets)])
            except:
                pass
        return result

    def handMoveTo(self, chord):
        """
        将整个手移动到某个手型，然后计算消耗的行动力，以及每个手指按在哪里
        :param chord:当前和弦需要按的位置列表，类似([5, 7], [4, 7], [3, 5], [2, 5], [1, 5])
        :return:返回多个dancer，也就是手型
        """
        dancers = []
        positionList = []
        try:
            len(chord[0])
            positionList = list(chord)
        except:
            positionList.append(chord)

        ChordType = classifyChord(positionList)  # 判断和弦类型
        positionType = []
        for item in ChordType:
            positionType.append(item[1])

        if not positionType:
            dancers.append(chord2Finger00(self, chord))
        if positionType == [1]:
            dancers += chord2Finger01(self, chord)
        if positionType == [2]:
            dancers += chord2Finger02(self, chord)
        if positionType == [1, 1]:
            dancers += chord2Finger03(self, chord)
        if positionType == [3]:
            dancers += chord2Finger04(self, chord)
        if positionType == [2, 1]:
            dancers += chord2Finger05(self, chord)
        if positionType == [1, 2]:
            dancers += chord2Finger06(self, chord)
        if positionType == [1, 1, 1]:
            dancers += chord2Finger07(self, chord)
        if positionType == [4] or positionType == [5] or positionType == [6]:
            dancers += chord2Finger08(self, chord)
        if positionType == [1, 3]:
            dancers += chord2Finger09(self, chord)
        if positionType == [2, 2]:
            dancers += chord2Finger10(self, chord)
        if positionType == [3, 1] or positionType == [4, 1] or positionType == [5, 1]:
            dancers += chord2Finger11(self, chord)
        if positionType == [1, 1, 2] or positionType == [1, 1, 3]:
            dancers += chord2Finger12(self, chord)
        if positionType == [1, 2, 1] or positionType == [1, 1, 1, 1]:
            dancers += chord2Finger13(self, chord)
        if positionType == [2, 1, 1]:
            dancers += chord2Finger14(self, chord)
        if positionType == [3, 1, 1, 1] or positionType == [2, 1, 1, 1]:
            dancers += chord2Finger15(self, chord)
        if positionType == [1, 4]:
            dancers += chord2Finger16(self, chord)
        if positionType == [2, 3]:
            dancers += chord2Finger17(self, chord)
        if positionType == [3, 2]:
            dancers += chord2Finger18(self, chord)
        if positionType == [4, 2]:
            dancers += chord2Finger19(self, chord)
        if positionType == [2, 1, 1, 2]:
            dancers += chord2Finger20(self, chord)
        if positionType == [1, 1, 1, 3]:
            dancers += chord2Finger21(self, chord)
        if positionType == [2, 1, 2]:
            dancers += chord2Finger22(self, chord)
        if positionType == [2, 2, 1]:
            dancers += chord2Finger23(self, chord)
        if positionType == [4, 1, 1]:
            dancers += chord2Finger24(self, chord)
        if positionType == [1, 1, 1, 2]:
            dancers += chord2Finger25(self, chord)
        if positionType == [3, 1, 2]:
            dancers += chord2Finger26(self, chord)
        if positionType == [2, 1, 3]:
            dancers += chord2Finger27(self, chord)
        if positionType == [3, 3]:
            dancers += chord2Finger28(self, chord)
        if positionType == [2, 4]:
            dancers += chord2Finger29(self, chord)
        if positionType == [1, 5]:
            dancers += chord2Finger30(self, chord)
        if positionType == [1, 1, 4]:
            dancers += chord2Finger31(self, chord)

        return dancers

    def fingerDistance(self, fingerA, fingerB):
        """
        计算两个手指按弦点之间的距离，如果其中一指是在横按，侧取第三弦点
        :param fingerA:
        :param fingerB:
        :return: 返回距离
        """
        fingerStringDistance = abs(fingerA.string - fingerB.string) * self.stringDistance
        fingerFretDistance = abs(self.stringLength(fingerA.fret)-self.stringLength(fingerB.fret))
        distance = math.sqrt(math.pow(fingerStringDistance, 2) + math.pow(fingerFretDistance, 2))
        if fingerA.fret == 0 or fingerB.fret == 0:
            return 0.0
        return distance

    def validation(self, chord):
        """
        验证当前指型是否符合是人类可以按出来的
        :param chord:
        :return:
        """
        if self.fingerDistance(self.fingerA, self.fingerB) > 4.3:
            return False
        if self.fingerDistance(self.fingerB, self.fingerC) > 4.3:
            return False
        if self.fingerDistance(self.fingerC, self.fingerD) > 4.3:
            return False
        if self.fingerA.fret > self.fingerB.fret or self.fingerB.fret > self.fingerC.fret or self.fingerC.fret > self.fingerD.fret:
            return False

        # 验证所有要按的音符是否都按出来的，特别是空弦音是否被按住发不出声
        touchPoints = self.touchPoints()
        for note in chord:
            if note not in touchPoints:
                return False
        else:
            return True

    def outPutNote(self):

        def printNotes(Notes, lineFeed=30):
            line1 = []
            line2 = []
            line3 = []
            line4 = []
            line5 = []
            line6 = []
            lines = [line1, line2, line3, line4, line5, line6]
            if len(Notes) > lineFeed:
                length = lineFeed
            else:
                length = len(Notes)
            for i in range(length):
                chord = Notes[i]
                strings = [note[0] for note in chord]
                frets = [note[1] for note in chord]
                for string in range(0, 6):
                    if string + 1 in strings:
                        fret = frets[strings.index(string + 1)]
                        if fret > 9:
                            lines[string].append(str(fret))
                        else:
                            lines[string].append(str(fret) + '-')
                    else:
                        lines[string].append('--')

            for i in range(6):
                print(' '.join(lines[i]))

        allNote = copy.copy(self.traceNote)
        while len(allNote) > 30:
            printNotes(allNote)
            allNote = allNote[30:]
        printNotes(allNote)

        print(self.traceFinger)


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
