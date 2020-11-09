from mxm.midifile import MidiInFile
from mxm.midifile import MidiToCode
from mxm.midifile import exampledir

from calculate import *
from LeftHand import FretDance
from chordToFinger import *


# test_file = testdir('midifiles/cubase-minimal-type1.mid')
# test_file = testdir('midifiles-out/mxm_midifile_type_1_minimal.mid')

# advanced Creative Commons midi file example found at:
# http://www.piano-midi.de/bach.htm
# Copyright © 1996-2016 by Bernd Krueger


def testMidi():
    test_file = exampledir('midi-in/bach_847.mid')
    midiIn = MidiInFile(MidiToCode(), test_file)
    midiIn.read()


class test:
    def __init__(self):
        pass

    def testChord(self, chordNotes=[5, 20, 24, 29]):
        """
        测试和弦变指法,主要涉及以下函数
        position(从音符生成位置),
        handChordPosition（过滤留下符合人体工程学的位置组合）,
        classifyChord（判断和弦指型）,
        arrangeNotesInChord（和弦音按弦或按品来排列）
        """
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

    def testOutput(self):
        trace = [[[4, 2], [5, 3]], [[5, 8], [4, 0]], [[5, 7], [3, 0]], [[4, 7], [5, 8]], [[5, 10], [2, 0]],
                 [[3, 5], [4, 7]], [[3, 7], [2, 0]], [[1, 5], [2, 5], [3, 5]]]
        outPut(trace)

    def testChordToFinger(self, fun, chord):
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


if __name__ == '__main__':
    a = test()
    chord = [[3, 0]]

    fun = chord2Finger00
    a.testChordToFinger(fun, chord)
