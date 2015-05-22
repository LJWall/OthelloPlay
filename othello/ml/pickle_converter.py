import pickle
import os

thisdir = os.path.dirname(os.path.realpath(__file__))

with open(thisdir + '/nn6-simple2.pickle.it3', mode='rb') as F:
    NN_6 = pickle.load(F)

with open(thisdir + '/nn6-simple2.pickle.old.it3', mode='wb') as F:
    pickle.dump(NN_6, F, protocol=2)

with open(thisdir + '/nn8-simple2.pickle.it4', mode='rb') as F:
    NN_8 = pickle.load(F)

with open(thisdir + '/nn8-simple2.pickle.old.it4', mode='wb') as F:
    pickle.dump(NN_8, F, protocol=2)

