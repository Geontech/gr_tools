#!/usr/bin/env python
"""Parameter space

Use the parameter space to describe the set of allowable values of a
given function.  This then will create list of combinations to span
the parameter space.

Examples
--------
>>> spec = {
>>>     "sample_rate":[5e6, 10e6, 20e6],
>>>     "mode": ["real", "complex"],
>>>     "n_syms":[1000, 10000, 10000]}
>>> param_list = get_param_space(spec)
"""
# ----------------------  import libraries used  ----------------------------
import itertools

def get_param_space(param_dict):
    """Get parameter space

    Uses itertools to get the list of combinations of the
    parameters.  This can be used to run a function with the list
    of settings.

    Parameters
    ----------
    param_dict : dict
        Dictionary with fields in the keys of the dictionary.
        The values of the dictionary would be a list of possible
        values.

    Results
    -------
    list_params : list
        List of dictionaries.  Each is one combination of parameters
    """
    keys = param_dict.keys()
    param_list = []
    for i in itertools.product(*param_dict.values()):
        param_list.append(dict(zip(keys, i)))

    return param_list