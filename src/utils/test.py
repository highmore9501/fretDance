import numpy as np


def get_position_by_fret(fret: int, value_1: np.array, value_12: np.array) -> np.array:
    base_ratio = 2**(1/12)
    value_0 = (2 * value_12 - base_ratio *
               (2 * value_12 - value_1)) / (2 - base_ratio)

    return fret_position(value_0, value_12, fret)


def fret_position(string_start, string_middle, fret_number):
    string_end = 2 * string_middle - string_start
    end_to_start = string_end - string_start

    end_to_fret = end_to_start * 0.5**(fret_number/12)
    fret_position = string_end - end_to_fret
    return fret_position


if __name__ == '__main__':
    fret = 24
    # value_0 = np.array([0.0, 0.0, 0.0])
    value_1 = np.array([0.0, 0.0, 0.0])
    value_12 = np.array([0.5, 0.5, 0.5])
    print(get_position_by_fret(fret, value_1, value_12))
