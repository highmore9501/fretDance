from calculate import *
from LeftHand import FretDance
from chordToFinger import *


class test:
    def __init__(self):
        pass

    def testChord(self, chordNotes=None):
        """
        测试和弦变指法,主要涉及以下函数
        position(从音符生成位置),
        handChordPosition（过滤留下符合人体工程学的位置组合）,
        classifyChord（判断和弦指型）,
        arrangeNotesInChord（和弦音按弦或按品来排列）
        """
        if chordNotes is None:
            chordNotes = [5, 20, 24, 29]
        chordPosition = []
        chordPositionAppend = chordPosition.append
        for note in chordNotes:  # 把和弦分解成音符
            notePositions = position(note)  # 得到当前音符可能的位置列表
            chordPositionAppend(notePositions)  # 得到所有音符的可能的位置列表
        outer = handChordPosition(chordPosition)
        types = len(outer)
        print('当前音符是' + str(chordNotes) + ', 一共有{}种指法: '.format(types))
        for i in range(types):
            print('第{}种指法是:'.format(i + 1))
            print(outer[i])
            self.testClassifyChord(outer[i])
            self.testArrangeNotesInChord(outer[i], 'string')
            self.testArrangeNotesInChord(outer[i], 'fret')

    def testClassifyChord(self, chord=([6, 5], [5, 7], [4, 7], [3, 5], [2, 5])):
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
        print('和弦类型是' + str(positionType) + '型')

    def testArrangeNotesInChord(self, chord, way):
        newChordByString = arrangeNotesInChord(chord, way)
        print('和弦按{}排列的结果是：'.format(way))
        print(newChordByString)

    def testChordToFinger(self, fun, chord):
        """
        测试chordToFinger里各种公式有没有问题
        :param fun: 公式的名字
        :param chord: 测试和弦
        :return:
        """
        dancer = FretDance()
        result = fun(dancer, chord)
        i = 1
        if type(result) == type(dancer):
            print(result.entropy)
            for finger in result.allFinger:
                if finger.press != 0:
                    print([finger.string, finger.fret])
        else:
            for dancer in result:
                print('第{}种指法是：'.format(i))
                print(dancer.entropy)
                i += 1
                for finger in dancer.allFinger:
                    if finger.press != 0:
                        print([finger.string, finger.fret])

    def testDancerMaker(self, ChordNotes, dancerNumberLimit=20):
        dancer = FretDance()
        allFretDance = [dancer]
        chordPosition = []  # 生成一个空的和弦按法列表
        chordPositionAppend = chordPosition.append

        if len(ChordNotes) > 6:
            print(ChordNotes)
            print('音符超出6个')
            raise

        for note in ChordNotes:  # 把和弦分解成音符
            if note < 0 or note > 48:
                print(ChordNotes)
                print('音符超出上下限')
                raise
            notePositions = position(note)  # 得到当前音符可能的位置列表
            chordPositionAppend(notePositions)  # 得到所有音符的可能的位置列表
        filteredChordPositions = handChordPosition(chordPosition)  # 过滤得到所有无重复弦的音符位置组合，也就是可能的和弦按法组合

        currentDancers = copy.deepcopy(allFretDance)
        currentDancerNumber = len(currentDancers)

        for dancerNumber in range(currentDancerNumber):  # 对所有留存的指法列表遍历
            for handPosition in filteredChordPositions:  # 对所有可能的和弦按法遍历
                currentDancer = copy.deepcopy(allFretDance[dancerNumber])  # 先继承一个父指法
                dancers = currentDancer.handMoveTo(handPosition)  # 用当前指法去按当前和弦的位置，这里会生成多个可能性，需要展开来处理
                allFretDance += dancers  # 加入留存的指法列表
        allFretDance = allFretDance[currentDancerNumber:]  # 删掉父指法
        allFretDance = arrangeDancers(allFretDance, dancerNumberLimit)  # 对指法列表进行排序过滤
        allFretDance[0].outPutNote()


if __name__ == '__main__':
    a = test()
    chordNote = [24, 16, 19, 12]
    a.testDancerMaker(chordNote)

