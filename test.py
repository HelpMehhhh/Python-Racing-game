import numpy as np
import random
from math import atan2
def get_data_seg(first_point, second_point):
        result = []
        pos = [-6.04,13.64]

        t = ((first_point[0]-pos[0])*(first_point[0]-second_point[0])-(first_point[1]-pos[1])*(second_point[1]-first_point[1]))/((second_point[1]-first_point[1])**2+(second_point[0]-first_point[0])**2)
        first_point = np.array(first_point)
        second_point = np.array(second_point)
        p = first_point+t(second_point - first_point)
        if abs(first_point[1]-second_point[1]) > abs(first_point[0]-second_point[0]):
            dist_sign = np.sign((p[0]-pos[0])/(second_point[1]-first_point[1]))

        else:
            dist_sign = np.sign((p[1]-pos[1])/(first_point[0]-second_point[0]))

        result.append(dist_sign*np.linalg.norm(p-np.array(pos)))
        result.append(p)
        return result

print(get_data_seg((4.43,-3.34), (-50.076, 121.2)))