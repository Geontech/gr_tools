#!/usr/bin/python
"""Convenience functions for generating signals with GNU Radio components

This module houses functions to launch a source and sink around a
component to quickly run an input and extract an output.  Although
it may sound similiar to creating a flowgraph for the same purpose,
this allows for scripting the scenario with different input source,
and configuring the component under various parameters.

Examples
--------
>>> import numpy as np
>>> r = np.random.rand(10000)
>>> r.astype(np.complex64).tofile("/tmp/input.32cf")

>>> in_sig = {"path":"/tmp/input.32cf",
>>>     "type":DTYPE["COMPLEX"], "repeat":True}
>>> out_sig = {"path":"/tmp/output.32cf",
>>>     "type":DTYPE["COMPLEX"], "n_items":4000}
>>> component = blocks.multiply_const_cc(1.0)

# run simulation and load output from file.
>>> run_file_source(component, in_sig, out_sig)
>>> output = np.fromfile("/tmp/output.32cf", dtype=np.complex64)
"""
import os
import sys
import numpy as np
from gnuradio import gr, blocks
from gr_tools import *
from gr_tools.parameter_space import get_param_space

def batch_run_file_source(comp_func, param_dict, base_name,
        in_spec=DEFAULT_FILE_SPEC, out_spec=DEFAULT_OUT_SPEC,
        connections=None):
    """
    Run through the list of parameters.

    Parameters
    ----------
    comp_func : function
        The constructor for the GNU Radio component

    param_dict : dict
        Each key is a keyword of the constructor.
        Each value is a list of acceptable parameter.

    base_name : str
        Base name for output signal

    in_spec : dict
        The input spec for the file

    out_spec : dict
        The output spec with data type and number output
        bytes.  The path for the output file is updated
        with the base_name

    connections : None or (tuple)
        If None, just try to connect.
        If provided, enforce connect to the right port
        First element of tuple defines the port on input
        Second element of tuple defines the port on output

    Returns
    -------
    out_dict : dict
        Each key is the output file generated.
        Each value is the param settings.
    """
    # get the list of parameters
    param_list = get_param_space(param_dict)
    out_ext = FILE_EXT[out_spec["type"]]

    out_dict = {}

    for p_ind, param in enumerate(param_list):
        # ---------------------  update the output spec  --------------------
        o_spec = {}
        o_spec.update(out_spec)

        # update output file name based on parameter
        o_spec["path"] = base_name + "_param_%06d%s"%(p_ind, out_ext)

        # -----------  generate component with the new parameters  ----------
        component = comp_func(**param)

        # ------------------------  run simulation  -------------------------
        run_file_source(component, in_spec, o_spec, connections)

        # track the params associated with each file
        out_dict[o_spec["path"]] = param

    return out_dict

def batch_run_msg_source(comp_func, param_dict, base_name,
        in_spec=DEFAULT_FILE_SPEC, out_spec=DEFAULT_OUT_SPEC,
        connections=None):
    """
    Run through the list of parameters.

    Parameters
    ----------
    comp_func : function
        The constructor for the GNU Radio component

    param_dict : dict
        Each key is a keyword of the constructor.
        Each value is a list of acceptable parameter.

    base_name : str
        Base name for output signal

    in_spec : dict
        The input spec for the message source

    out_spec : dict
        The output spec with data type and number output
        bytes.  The path for the output file is updated
        with the base_name

    connections : None or (tuple)
        If None, just try to connect.
        If provided, enforce connect to the right port
        First element of tuple defines the port on input
        Second element of tuple defines the port on output

    Returns
    -------
    out_dict : dict
        Each key is the output file generated.
        Each value is the param settings.
    """
    # get the list of parameters
    param_list = get_param_space(param_dict)
    out_ext = FILE_EXT[out_spec["type"]]
    out_dict = {}

    for p_ind, param in enumerate(param_list):
        # ---------------------  update the output spec  --------------------
        o_spec = {}
        o_spec.update(out_spec)

        # update output file name based on parameter
        o_spec["path"] = base_name + "_param_%06d%s"%(p_ind, out_ext)

        # -----------  generate component with the new parameters  ----------
        component = comp_func(**param)

        # ------------------------  run simulation  -------------------------
        run_msg_source(component, in_spec, o_spec, connections)

        # track the params associated with each file
        out_dict[o_spec["path"]] = param

    return out_dict

def run_file_source(component,
        file_spec=DEFAULT_FILE_SPEC, out_spec=DEFAULT_OUT_SPEC,
        connections=None):
    """Run simulation with file source as input

    Parameters
    ----------
    component : gnuradio component
        This will typically be a subclass of gnuradio.gr.hier_block2
        Since this will need to import itself, that will be left to
        the calling function to import, create this instance and
        configure.

    file_spec : dict
        Dictionary with "type", "path", "repeat"

    out_spec : dict
        Dictionary with "type", "path", "n_items"

    connections : None or (tuple)
        If None, just try to connect.
        If provided, enforce connect to the right port
        First element of tuple defines the port on input
        Second element of tuple defines the port on output
    """
    top = gr.top_block()

    # ------------------------  setup scenario  -----------------------------
    file_src = blocks.file_source(
        DTYPE[file_spec["type"]], file_spec["path"], file_spec["repeat"])

    # use the head block to limit output
    head = blocks.head(DTYPE[out_spec["type"]], out_spec["n_items"])
    file_sink = blocks.file_sink(
        DTYPE[out_spec["type"]], out_spec["path"]
    )

    # add connections
    if connections is None:
        top.connect(file_src, component, head, file_sink)
    else:
        top.connect((file_src), (component, connections[0]))
        top.connect((component, connections[1]), (head))
        top.connect(head, file_sink)

    # -----------------------  run simulation  ------------------------------
    top.run(max_noutput_items=out_spec["n_items"])

def run_msg_source(component,
        msg_spec=DEFAULT_MESSAGE_SPEC, out_spec=DEFAULT_OUT_SPEC,
        connections=None):
    """Run simulation with file source as input

    Parameters
    ----------
    component : gnuradio component
        This will typically be a subclass of gnuradio.gr.hier_block2
        Since this will need to import itself, that will be left to
        the calling function to import, create this instance and
        configure.

    msg_spec : dict
        Dictionary with "message", "periodic"

    out_spec : dict
        Dictionary with "type", "path", "n_items"

    connections : None or (tuple)
        If None, just try to connect.
        If provided, enforce connect to the right port
        First element of tuple defines the port on input
        Second element of tuple defines the port on output
    """
    top = gr.top_block()

    # ------------------------  setup scenario  -----------------------------
    import pmt
    source = blocks.message_strobe(pmt.intern("".join(msg_spec["message"])),
        msg_spec["period(ms)"])

    # use the head block to limit output
    head = blocks.head(DTYPE[out_spec["type"]], out_spec["n_items"])
    file_sink = blocks.file_sink(
        DTYPE[out_spec["type"]], out_spec["path"]
    )


    top.msg_connect((source, "strobe"), (component, connections[0]))
    top.connect((component, connections[1]), (head, 0))
    top.connect(head, file_sink)

    # -----------------------  run simulation  ------------------------------
    # NOTE: top.run() does not seem to check head
    #       when tested on msg_source -> wifi -> file_sink
    import time
    top.start(max_noutput_items=out_spec["n_items"])
    while head.nitems_written(0) < out_spec["n_items"]:
        time.sleep(1e-3)

    print("Completed simulation")

    del(top)