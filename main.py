"""
需要按一个音符时的处理流程
1.列出有几个点可以按出此音符，乘以四个手指，生成对应个数的dancer()，并且计算并生成消耗点数
2.对所有的dancer继续应用下一个音符，分裂出更多的dancer()，每一个都继承父dancer()的轨迹和消耗点数
3.限制所有dancer()的数量，保持在200以内
"""
import copy

from LeftHand import FretDance
from calculate import position, filterDance, handChordPosition,dancerMaker

# 一个自然音阶下的，三度双音上行
piece = [[8, 10],
         [10, 13],
         [12, 15],
         [13, 17],
         [15, 19],
         [17, 20],
         [19, 22],
         [20, 24]]
dancer = FretDance()
AllDancers = [dancer]
dancerLimits = 200

for ChordNotes in piece:
    for dancer in AllDancers:
        DancerAmount = len(AllDancers)
        NewDancers = dancerMaker(dancer, ChordNotes, dancerLimits)
        AllDancers += NewDancers
        AllDancers = AllDancers[DancerAmount:]

print(AllDancers[0].trace)




