from numpy import ndarray, linalg, array, mean, dot, cross
from numpy.linalg import svd
from typing import Tuple


def find_transform_matrix(p1: ndarray, p2: ndarray, p3: ndarray, q1: ndarray, q2: ndarray, q3: ndarray) -> Tuple[ndarray, ndarray]:
    # 计算中心点
    p_center = mean(array([p1, p2, p3]), axis=0)
    q_center = mean(array([q1, q2, q3]), axis=0)

    # 计算协方差矩阵
    covariance_matrix = dot(
        (array([p1, p2, p3]) - p_center).T, array([q1, q2, q3]) - q_center)

    # 使用SVD计算旋转矩阵
    U, _, Vt = svd(covariance_matrix)
    rotation_matrix = dot(Vt.T, U.T)

    # 计算平移向量
    translation_vector = q_center - dot(p_center, rotation_matrix)

    return rotation_matrix, translation_vector


def transform_point(point: ndarray, rotation_matrix: ndarray, translation_vector: ndarray) -> ndarray:
    transformed_point = dot(rotation_matrix, point) + translation_vector
    return transformed_point


def normalVector(p1: ndarray, p2: ndarray, p3: ndarray) -> ndarray:
    v1 = p2 - p1
    v2 = p3 - p1
    normal_vector = cross(v1, v2)
    normal_vector = normal_vector / linalg.norm(normal_vector)
    return normal_vector
