import numpy as np
x = -1
y = 0
print(np.degrees(np.arctan2(x, y)))
angle = -65
if abs(angle) > 180:
    angle += np.sign(angle)*-360


print(angle)