import numpy as np
CORNER_TO_CENTER_LEN = np.sqrt(1**2 + 2**2)
CORNER_TO_CENTER_ANGLE = np.arctan(1/2)
car_angle = np.pi/2
player_angle = 0
player_pos = [0,0]
car_pos = [0,0]

norm_angle = car_angle - (player_angle - np.pi/2)
if norm_angle > np.pi: norm_angle -= 2*np.pi
if norm_angle < -np.pi: norm_angle += 2*np.pi
norm_pos_vec = np.array(car_pos) - np.array(player_pos)

#top left, top right, bottom left, bottom right from car view
car_corners = [[norm_pos_vec[0]+np.cos(norm_angle+CORNER_TO_CENTER_ANGLE)*CORNER_TO_CENTER_LEN, norm_pos_vec[1]+np.sin(norm_angle+CORNER_TO_CENTER_ANGLE)*CORNER_TO_CENTER_LEN],
[norm_pos_vec[0]+np.cos(norm_angle-CORNER_TO_CENTER_ANGLE)*CORNER_TO_CENTER_LEN, norm_pos_vec[1]+np.sin(norm_angle-CORNER_TO_CENTER_ANGLE)*CORNER_TO_CENTER_LEN],
[norm_pos_vec[0]+np.cos((norm_angle-np.pi)-CORNER_TO_CENTER_ANGLE)*CORNER_TO_CENTER_LEN, norm_pos_vec[1]+np.sin((norm_angle-np.pi)-CORNER_TO_CENTER_ANGLE)*CORNER_TO_CENTER_LEN],
[norm_pos_vec[0]+np.cos((norm_angle-np.pi)+CORNER_TO_CENTER_ANGLE)*CORNER_TO_CENTER_LEN, norm_pos_vec[1]+np.sin((norm_angle-np.pi)+CORNER_TO_CENTER_ANGLE)*CORNER_TO_CENTER_LEN]]
print(car_corners)

