"""
需要按一个音符时的处理流程
1.列出有几个点可以按出此音符，乘以四个手指，生成对应个数的dancer()，并且计算并生成消耗点数
2.对所有的dancer继续应用下一个音符，分裂出更多的dancer()，每一个都继承父dancer()的轨迹和消耗点数
3.限制所有dancer()的数量，保持在200以内

tmd空弦音被跳过了，明天再检查
"""
import copy

from LeftHand import FretDance
from calculate import dancerMaker

# 一个自然音阶下的，三度双音上行
# piece = [[8, 12],
#          [10, 13],
#          [12, 15],
#          [13, 17],
#          [15, 19],
#          [17, 20],
#          [19, 22],
#          [20, 24]]
piece = [[8],[10],[12],[13],[15],[17],[19],[20],[22],[24]]
dancer = FretDance()
AllDancers = [dancer]
dancerLimits = 200

for ChordNotes in piece:
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

print(AllDancers[0].trace)
print(AllDancers[0].entropy)




