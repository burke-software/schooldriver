import numpy as np


def array_contains_anything(np_array):
    """ Return true if numpy array contains any values above 0
    Does not work with negative values """
    if np.nansum(np_array) > 0:
        return True
    return False
