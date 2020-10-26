"""
需要按一个音符时的处理流程
1.列出有几个点可以按出此音符，乘以四个手指，生成对应个数的dancer()，并且计算并生成消耗点数
2.对所有的dancer继续应用下一个音符，分裂出更多的dancer()，每一个都继承父dancer()的轨迹和消耗点数
3.限制所有dancer()的数量，保持在200以内
"""
import copy

from LeftHand import FretDance
from calculate import position, filterDance, handChordPosition

# 一个自然音阶下的，三度双音上行
piece = [[8, 10],
         [10, 13],
         [12, 15],
         [13, 17],
         [15, 19],
         [17, 20],
         [19, 22],
         [20, 24]]


def fingerDanceMaker(dancerNumberLimit=200):
    fretDance = FretDance()
    allFretDance = [fretDance]

    for chord in piece:  # 把整个乐曲分解成和弦
        chordPosition = []  # 生成一个空的和弦按法列表
        for note in chord:  # 把和弦分解成音符
            notePositions = position(note)  # 得到当前音符可能的位置列表
            chordPosition.append(notePositions)  # 得到所有音符的可能的位置列表
        filteredChordPositions = handChordPosition(chordPosition)  # 过滤得到所有无重复弦的音符位置组合，也就是可能的和弦按法组合

        currentDancerNumber = len(allFretDance)

        for dancerNumber in range(currentDancerNumber):  # 对所有留存的指法列表遍历
            for handPosition in filteredChordPositions:  # 对所有可能的和弦按法遍历
                currentDancer = copy.deepcopy(allFretDance[dancerNumber])  # 先继承一个父指法
                dancers = currentDancer.handMoveTo(handPosition)  # ?? 用当前手指去按当前和弦的位置，这里会生成多个可能性，需要展开来处理
                for dancer in dancers:
                    if dancer.validation:  # 验证指法是否手指生理要求
                        allFretDance.append(dancer)  # 可行则加入留存的指法列表
        allFretDance = allFretDance[currentDancerNumber:]  # 删掉父指法
        allFretDance = filterDance(allFretDance, dancerNumberLimit)  # 对指法列表进行排序过滤
    return allFretDance[0]
