import json
from numpy import ndarray, array
from ..utils.fretDistanceDict import FRET_DISTANCE_DICT
from ..utils.tab2Space import transform_point


def hand2Animation(recorder: str, animation: str, BPM: float, FPS: float, rotation_matrix: ndarray, translation_vector: ndarray, fret_open_distance: ndarray) -> None:
    handDicts = None
    data_for_animation = []
    with open(recorder, "r") as f:
        handDicts = json.load(f)

    for item in handDicts:
        beat = item["beat"]
        time = beat / BPM * 60
        frame = time * FPS

        leftHand = item["leftHand"]
        fingerList = []
        for data in leftHand:
            fingerIndex = data["fingerIndex"]
            # skip open string. 空弦音跳过
            if fingerIndex == -1:
                continue
            stringIndex = data["fingerInfo"]["stringIndex"]
            fret = data["fingerInfo"]["fret"]
            fret_x_in_board = FRET_DISTANCE_DICT[f"{0}-{fret}"]
            press = data["fingerInfo"]["press"]

            finger_point = array([stringIndex, fret_x_in_board, 0])
            finger_point = transform_point(
                finger_point, rotation_matrix, translation_vector)
            if press != 0:
                finger_point = finger_point + fret_open_distance
            fingerList.append({
                "fingerIndex": fingerIndex,
                "finger_point": [finger_point[0], finger_point[1], finger_point[2]]
            })

        data_for_animation.append({
            "frame": frame,
            "fingerList": fingerList
        })

    with open(animation, "w") as f:
        json.dump(data_for_animation, f)
