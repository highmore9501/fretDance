from mxm.midifile import MidiInFile
from mxm.midifile import MidiToCode
from mxm.midifile import exampledir

from calculate import *


# test_file = testdir('midifiles/cubase-minimal-type1.mid')
# test_file = testdir('midifiles-out/mxm_midifile_type_1_minimal.mid')

# advanced Creative Commons midi file example found at:
# http://www.piano-midi.de/bach.htm
# Copyright © 1996-2016 by Bernd Krueger


def testMidi():
    test_file = exampledir('midi-in/bach_847.mid')
    midiIn = MidiInFile(MidiToCode(), test_file)
    midiIn.read()


class testCalculate:
    def __init__(self):
        pass

    def testChord(self, chordNotes=[5, 12, 17, 20, 24]):
        """
        测试和弦变指法,主要涉及position(),handChordPosition()两个函数
        :return:
        """
        chordPosition = []
        chordPositionAppend = chordPosition.append
        for note in chordNotes:  # 把和弦分解成音符
            notePositions = position(note)  # 得到当前音符可能的位置列表
            chordPositionAppend(notePositions)  # 得到所有音符的可能的位置列表
        outer = handChordPosition(chordPosition)
        types = len(outer)
        print(chordNotes)
        print('一共有{}种指法'.format(types))
        for i in range(types):
            print('第{}种指法是'.format(i + 1))
            print(outer[i])
            self.testClassifyChord(outer[i])

    def testClassifyChord(self, chord=([6, 5], [5, 7], [4, 7], [3, 5], [2, 5])):
        n = classifyChord(chord)
        positionType = []
        for item in n:
            positionType.append(item[1])
        print('和弦类型是' + str(positionType) + '型。')


if __name__ == '__main__':
    a = testCalculate()
    a.testChord()
