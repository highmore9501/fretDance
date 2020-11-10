"""
需要按一个音符时的处理流程
1.列出有几个点可以按出此音符，乘以四个手指，生成对应个数的dancer()，并且计算并生成消耗点数
2.对所有的dancer继续应用下一个音符，分裂出更多的dancer()，每一个都继承父dancer()的轨迹和消耗点数
3.限制所有dancer()的数量，保持在200以内

"""
from midiToNote import *
# 一个自然音阶下的，三度双音上行
piece1 = [[8, 12],
          [10, 13],
          [12, 15],
          [13, 17],
          [15, 19],
          [17, 20],
          [19, 22],
          [20, 24]]
# 上行自然音阶
piece2 = [[8], [10], [12], [13], [15], [17], [19], [20], [22], [24]]
# 下行自然音阶
piece3 = [[36], [34], [32], [31], [29], [27], [25], [24], [22], [20]]
piece4 = [[32], [31], [29], [27], [25], [24], [22], [20]]


def outPutFingerStyle(piece, dancerLimits=20):
    import copy
    from LeftHand import FretDance
    from calculate import dancerMaker

    dancer = FretDance()
    AllDancers = [dancer]
    for ChordNotes in piece:
        try:
            currentDancers = copy.deepcopy(AllDancers)
            DancerAmount = len(currentDancers)
            for dancer in currentDancers:
                NewDancers = dancerMaker(dancer, ChordNotes, dancerLimits)
                AllDancers += NewDancers

            # 当AllDancers里元素数量暴涨时，去掉原始的AllDancers以及entropy过高的dancer，只留下200个继续下一轮
            if len(AllDancers) > DancerAmount + dancerLimits:
                AllDancers = AllDancers[DancerAmount:DancerAmount + dancerLimits]
            else:
                AllDancers = AllDancers[DancerAmount:]
                if len(AllDancers) < 1:
                    print('这个和弦只有唯一解了：')
                    print(ChordNotes)
                if len(AllDancers) == 0:
                    print('这个和弦无解了：')
                    print(ChordNotes)
        except:
            print('这个和弦弹不了：')
            print(ChordNotes)

    print('最优指法消耗的行动力是{},指法如下：'.format(AllDancers[0].entropy))
    AllDancers[0].outPutNote()


if __name__ == '__main__':
    midiFile = 'guitarMidiFlies/Aguado_Study_no20.mid'
    piece = midiToNote(midiFile)
    print(piece)

    # outPutFingerStyle(piece1)
    # outPutFingerStyle(piece2)
    # outPutFingerStyle(piece3)
    # outPutFingerStyle(piece4)
    outPutFingerStyle(piece)
