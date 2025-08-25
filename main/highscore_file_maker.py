import pickle
import os
score = 0
with open(os.path.join(os.path.dirname(__file__), 'highscore.pickle'), 'wb') as f: pickle.dump(score, f)