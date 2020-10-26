from mxm.midifile import exampledir
from mxm.midifile import MidiInFile
from mxm.midifile import MidiToCode
from calculate import position,handChordPosition

# test_file = testdir('midifiles/cubase-minimal-type1.mid')
# test_file = testdir('midifiles-out/mxm_midifile_type_1_minimal.mid')

# advanced Creative Commons midi file example found at:
# http://www.piano-midi.de/bach.htm
# Copyright © 1996-2016 by Bernd Krueger


def testMidi():
    test_file = exampledir('midi-in/bach_847.mid')
    midiIn = MidiInFile(MidiToCode(), test_file)
    midiIn.read()


def testChrod(chord=[5, 12, 17, 20, 24]):
    """
    测试和弦变指法
    :return:
    """
    chordPosition = []
    for note in chord:  # 把和弦分解成音符
        notePositions = position(note)  # 得到当前音符可能的位置列表
        chordPosition.append(notePositions)  # 得到所有音符的可能的位置列表
    outer = handChordPosition(chordPosition)
    types = len(outer)
    print('一共有{}种指法'.format(types))
    for i in range(types):
        print('第{}种指法是'.format(i + 1))
        print(outer[i])


if __name__ == '__main__':
    chord = [12, 17, 20, 24, 29]
    testChrod(chord)

