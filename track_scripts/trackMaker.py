import sympy as sym
import numpy as np
bez_points = [((0,0),(0,60),(0,100)), ((0,100),(0,115),(20,115)), ((20,115),(40,115),(40,90)), ((40,90),(40,75),(35,70)), ((35,70),(20,60),(40,50)), ((40,50),(70,35),(120,50)), ((120,50),(160,65),(140,80)), ((140,80),(125,95),(100,90)), ((100,90),(60,85),(70,105)), ((70,105),(74,112),(100,110)), ((100,110),(150,108),(198,94)), ((198,94),(224,83),(195,71)), ((195,71),(162,61),(184,48)), ((184,48),(198,43),(210,60)), ((210,60),(220,70),(250,60)), ((250,60),(277,49),(255,40)), ((255,40),(240,35),(205,35)), ((205,35),(180,35),(185,10)), ((185,10),(190,-8),(165,-10)), ((165,-10),(130,-10),(156,17)), ((156,17),(177,45),(134,37)), ((134,37),(116,34),(120,0)), ((120,0),(120,-60),(80,-20)), ((80,-20),(55,0),(40,-50)), ((40,-50),(20,-110),(-20,-70)), ((-20,-70),(-40,-50),(-30,-40)), ((-30,-40),(-7,-20),(-5,-15)), ((-5,-15),(0,-5),(0,0))]
THRESHHOLD = 0.8
PIECEWISE_POINTS = []
PARALLEL_POINTS_PLUS_X = []
PARALLEL_POINTS_MINUS_X = []
PARALLEL_CUT = []
TRACK_WDITH = 6

start = True
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
        vx = float(lp2[0]-lp1[0])
        vy = float(lp2[1]-lp1[1])
        l = float(np.sqrt(np.float64(((vx)**2)+((vy)**2))))

        dy=float((TRACK_WDITH/l)*vx)
        dx=float((TRACK_WDITH/l)*vy)
        l1_p1 = (lp1[0]+dx, lp1[1]-dy)
        l2_p1 = (lp1[0]-dx, lp1[1]+dy)
        l1_p2 = (lp2[0]+dx, lp2[1]-dy)
        l2_p2 = (lp2[0]-dx, lp2[1]+dy)


        global start
        if not start:
            prev_l1_p1 = PARALLEL_CUT[-2]
            prev_l1_p2 = PARALLEL_POINTS_PLUS_X[-1]
            prev_l2_p1 = PARALLEL_CUT[-1]
            prev_l2_p2 = PARALLEL_POINTS_MINUS_X[-1]

            try: t_plus = ((l1_p2[0]-l1_p1[0])*(prev_l1_p1[1]-l1_p1[1])-(l1_p2[1]-l1_p1[1])*(prev_l1_p1[0]-l1_p1[0]))/((l1_p2[1]-l1_p1[1])*(prev_l1_p2[0]-prev_l1_p1[0])-(l1_p2[0]-l1_p1[0])*(prev_l1_p2[1]-prev_l1_p1[1]))
            except ZeroDivisionError: t_plus = 1
            try: t_minus = ((l2_p2[0]-l2_p1[0])*(prev_l2_p1[1]-l2_p1[1])-(l2_p2[1]-l2_p1[1])*(prev_l2_p1[0]-l2_p1[0]))/((l2_p2[1]-l2_p1[1])*(prev_l2_p2[0]-prev_l2_p1[0])-(l2_p2[0]-l2_p1[0])*(prev_l2_p2[1]-prev_l2_p1[1]))
            except ZeroDivisionError: t_minus = 1
            #assert t_plus < 0, "Angle to small"
            #assert t_minus < 0, "Angle to small"
            PARALLEL_POINTS_MINUS_X.pop(-1)
            PARALLEL_POINTS_PLUS_X.pop(-1)
            PARALLEL_CUT.extend((l1_p1, l2_p1))
            PARALLEL_POINTS_MINUS_X.append((round((prev_l2_p2[0]-prev_l2_p1[0])*t_minus + prev_l2_p1[0], 2), round((prev_l2_p2[1]-prev_l2_p1[1])*t_minus + prev_l2_p1[1], 2)))
            PARALLEL_POINTS_PLUS_X.append((round((prev_l1_p2[0]-prev_l1_p1[0])*t_plus + prev_l1_p1[0], 2), round((prev_l1_p2[1]-prev_l1_p1[1])*t_plus + prev_l1_p1[1], 2)))
            PARALLEL_POINTS_MINUS_X.append((round(l2_p2[0], 2), round(l2_p2[1], 2)))
            PARALLEL_POINTS_PLUS_X.append((round(l1_p2[0], 2), round(l1_p2[1], 2)))
        else:
            start = False
            PARALLEL_POINTS_PLUS_X.extend(((round(l1_p1[0], 2), round(l1_p1[1], 2)), (round(l1_p2[0], 2), round(l1_p2[1], 2))))
            PARALLEL_POINTS_MINUS_X.extend(((round(l2_p1[0], 2), round(l2_p1[1], 2)), (round(l2_p2[0], 2), round(l2_p2[1], 2))))
            PARALLEL_CUT.extend((l1_p1, l2_p1))
        PIECEWISE_POINTS.append((round(lp1[0], 2), round(lp1[1], 2)))





for point in bez_points:
    point_maker(point, point[0], point[2], 0.5, 1)

print(PIECEWISE_POINTS)
print("                     break                     ")
print(PARALLEL_POINTS_PLUS_X)
print("                     break                     ")
print(PARALLEL_POINTS_MINUS_X)


