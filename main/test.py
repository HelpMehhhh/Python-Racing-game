import pickle
with open('parallel_points_01.pickle', 'rb') as f:
    data = pickle.load(f)

print(data)