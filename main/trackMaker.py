import sympy as sym
import numpy as np
bez_points = [((0,0),(0,60),(0,100)), ((0,100),(0,115),(20,115)), ((20,115),(40,115),(40,90)), ((40,90),(40,75),(35,70)), ((35,70),(20,60),(40,50)), ((40,50),(70,35),(120,50)), ((120,50),(160,65),(140,80)), ((140,80),(125,95),(100,90)), ((100,90),(60,85),(70,105)), ((70,105),(74,112),(100,110)), ((100,110),(150,105),(190,85)), ((190,85),(215,75),(190,70)), ((190,70),(170,65),(190,55)), ((190,55),(200,50),(210,60)), ((210,60),(220,70),(250,60)), ((250,60),(260,57),(250,45)), ((250,45),(240,35),(205,35)), ((205,35),(180,35),(185,10)), ((185,10),(190,-5),(165,-10)), ((165,-10),(140,-15),(155,25)), ((155,25),(170,60),(130,35)), ((130,35),(118,27),(120,0)), ((120,0),(120,-60),(80,-20)), ((80,-20),(55,0),(40,-50)), ((40,-50),(20,-110),(-20,-70)), ((-20,-70),(-40,-50),(-30,-40)), ((-30,-40),(-7,-20),(-5,-15)), ((-5,-15),(0,-5),(0,0)),]
THRESHHOLD = 1
PIECEWISE_POINTS = []
PARALLEL_POINTS_PLUS = []
PARALLEL_POINTS_MINUS = []
TRACK_WDITH = 6
i = 0

def point_maker(bez_point, lp1, lp2, step_f, p_step_f):
    t = sym.Symbol('t')
    Bx = (1 - t)*((1 - t)*bez_point[0][0] + t*bez_point[1][0]) + t*((1 - t)*bez_point[1][0] + t*bez_point[2][0])
    By = (1 - t)*((1 - t)*bez_point[0][1] + t*bez_point[1][1]) + t*((1 - t)*bez_point[1][1] + t*bez_point[2][1])
    step_p = (Bx.subs(t, step_f), By.subs(t, step_f))

    if abs(lp2[1]-lp1[1]) > abs(lp2[0]-lp1[0]):
        m = ((lp2[0]-lp1[0])/(lp2[1]-lp1[1]))
        dist = (abs(m*step_p[1]-step_p[0]+(-m*lp1[1]+lp1[0]))/(np.sqrt(np.float64(((m)**2)+1))))
    else:
        m = ((lp2[1]-lp1[1])/(lp2[0]-lp1[0]))
        dist = (abs(m*step_p[0]-step_p[1]+(-m*lp1[0]+lp1[1]))/(np.sqrt(np.float64(((m)**2)+1))))

    if dist > THRESHHOLD:
        if p_step_f >= step_f:
            point_maker(bez_point, lp1, step_p, (step_f-(0.5*(p_step_f-step_f))), step_f)
            point_maker(bez_point, step_p, lp2, (step_f+(0.5*(p_step_f-step_f))), step_f)

        else:
            point_maker(bez_point, lp1, step_p, (step_f-(0.5*(step_f-p_step_f))), step_f)
            point_maker(bez_point, step_p, lp2, (step_f+(0.5*(step_f-p_step_f))), step_f)

    else:
        global i
        i += 1
        vx = lp2[0]-lp1[0]
        vy = lp2[1]-lp1[1]
        l = np.sqrt(((vx)**2)+((vy)**2))
        dy=(TRACK_WDITH/l)*vx
        dx=(TRACK_WDITH/l)*vy
        p1lp1 = (lp1[0]+dx, lp1[1]-dy)
        p2lp1 = (lp1[0]-dx, lp1[1]+dy)
        p1lp2 = (lp1[0]+dx, lp1[1]-dy)
        p2lp2 = (lp1[0]-dx, lp1[1]+dy)

        if i % 2 == 0:
            pl1 = 
        else:

            PARALLEL_POINTS_PLUS.extend((p1lp1, p1lp2))
            PARALLEL_POINTS_MINUS.extend((p2lp1, p2lp2))
        PIECEWISE_POINTS.append(lp1)





for point in bez_points:
    point_maker(point, point[0], point[2], 0.5, 1)
#print(PIECEWISE_POINTS)


def get_sides():
    pass

