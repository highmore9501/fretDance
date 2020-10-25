def position(note):
    result = []
    stringMode = [0, 5, 10, 15, 19, 24]
    for i in range(6):
        string = 6 - i
        fret = note - stringMode[i]
        if 12 >= fret >= 0:
            result.append([string, fret])
    return result


def filterDance(arr, max):  # 冒泡排序
    length = len(arr)
    if length >= max:
        for i in range(length - 1):
            for j in range(length - 1 - i):  # 第二层for表示具体比较哪两个元素
                if arr[j].entropy > arr[j + 1].entropy:  # 如果前面的大于后面的，则交换这两个元素的位置
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        arr = arr[:max - 1]
    return arr
