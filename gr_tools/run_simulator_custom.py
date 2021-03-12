#!/usr/bin/env python3
"""Module to load and rum scenario
"""
import json
import os
import sys
import time
import importlib.util as iutil
from gnuradio import gr, blocks, uhd

# get appropriate user prompt based on Python
if sys.version_info.major == "2":
    # Python2 user prompt
    user_prompt = raw_input
else:
    # Python3 user prompt
    user_prompt = input

COMP_CONSTRUCTORS = {
    "usrp_source":uhd.usrp_source,
    "usrp_sink": uhd.usrp_sink
}

def load_blocks(custom_dir):
    """Load blocks available through gnuradio

    Parameters
    ----------
    custom_dir : str
        The path to the directory of Python modules for custom
        GNU Radio components

    Returns
    -------
    out : dict
        The dictionary of blocks available in
    """
    from inspect import getmembers, isfunction, isclass
    tmp = getmembers(blocks, isfunction)
    out_dict = dict(tmp)

    if not custom_dir:
        # no custom dir, return
        return out_dict

    # ---------------  load modules from custom directory  ------------------
    # store current dir and change to the custome directory
    c_dir = os.path.abspath(".")
    os.chdir(custom_dir)

    # go through list of files
    files = os.listdir(".")
    for c_file in files:
        if c_file[-3:] == ".py":
            mod_name = c_file[:-3]
            mod_spec = iutil.spec_from_file_location(mod_name,
                c_file)

            c_module = iutil.module_from_spec(mod_spec)
            c_module.__loader__.exec_module(c_module)

            try:
                # update out_dict with custom modules
                t_list = getmembers(c_module, isclass)
                t_dict = dict(t_list)
                out_dict[mod_name] = t_dict[mod_name]
            except Exception as e:
                print("Exception caught " + e)
                continue

    # return to original directory
    os.chdir(c_dir)

    return out_dict

def load_and_run_scenario(json_file):
    """Load scenario from json file

    The json file is expected to have a dictionary with
    fields "components", "connections", and "simulation"

    Parameters
    ----------
    json_file : str
        The path to the Json.
    """
    settings = json.load(open(json_file))
    comps = settings["components"]
    conns = settings["connections"]
    simm = settings["simulation"]
    # ----------------------  initialize objects  ---------------------------
    top = gr.top_block()
    comp_obj = {}

    # ---------------------  construct components  --------------------------
    for key in comps.keys():
        c_comp_spec = comps[key]
        c_comp_type = c_comp_spec["key"]
        c_comp_value = c_comp_spec["val"]

        if c_comp_type == "usrp_source":
            c_comp = config_uhd_source(**c_comp_value)
        elif c_comp_type == "usrp_sink":
            c_comp = config_uhd_sink(**c_comp_value)
        else:
            # construct object with parameters
            c_comp = COMP_CONSTRUCTORS[c_comp_type](**c_comp_value)
        comp_obj[key] = c_comp

    # ------------------------  setup connections  --------------------------
    for conn in conns:
        c_src = comp_obj[conn[0]]
        c_src_port = conn[1]
        c_tgt = comp_obj[conn[2]]
        c_tgt_port = conn[3]
        top.connect((c_src, c_src_port), (c_tgt, c_tgt_port))

    # --------------------------  run scenario  -----------------------------
    if simm["type"].lower() in ["time"]:
        # specify duration to run
        top.start()
        time.sleep(simm["value"]["duration"])
        top.stop()
    elif simm["type"].lower() in ["user"]:
        # run till user hits enter
        top.start()
        resp = user_prompt("Hit enter to exit")
        top.stop()
    elif simm["type"].lower() in ["data"]:
    	# NOTE: the number of samples is specified in the "head" component
        # TODO: assert that a head component is in components
        top.run()
    else:
        raise RuntimeError("Unexpected type of simulation")

def config_uhd_source(device, sample_rate, radio_freq, gain):
    """Configure UHD Source

    Configure UHD source

    Parameters
    ----------
    device : str
        An example is "b200".

    sample_rate : float
        The sampling rate of the USRP

    radio_freq : float
        The tuning frequency of the radio in Hertz

    gain : float
        The gain in decibels.

    Returns
    -------
    usrp_src : uhd.usrp_source
        The USRP source
    """
    assert radio_freq > 0, "Receive tune frequency should be > 0"
    assert sample_rate > 0, "Receive sample rate should be > 0"

    uhd_rx = uhd.usrp_source(
        ",".join((device, "")),
        uhd.stream_args(cpu_format="fc32", args="", channels=list(range(0,1))),
    )

    uhd_rx.set_samp_rate(sample_rate)
    uhd_rx.set_time_unknown_pps(uhd.time_spec())
    uhd_rx.set_center_freq(radio_freq, 0)
    uhd_rx.set_antenna("RX2", 0)
    if gain == -1:
        # activate AGC
        uhd_rx.set_rx_agc(True, 0)
    else:
        uhd_rx.set_gain(gain, 0)
    return uhd_rx

def config_uhd_sink(device, sample_rate, radio_freq, gain):
    """Configure UHD Sink

    Configure UHD sink

    Parameters
    ----------
    device : str
        An example is "b200".

    sample_rate : float
        The sampling rate of the USRP

    radio_freq : float
        The tuning frequency of the radio in Hertz

    gain : float
        The gain in decibels.

    Returns
    -------
    usrp_snk : uhd.usrp_sink
        The USRP sink
    """
    assert radio_freq > 0, "Transmit tune frequency should be > 0"
    assert sample_rate > 0, "Transmit sample rate should be > 0"

    uhd_tx = uhd.usrp_sink(
        ",".join((device, "")),
        uhd.stream_args(cpu_format="fc32", args="", channels=list(range(0,1))),
        "",
    )
    uhd_tx.set_samp_rate(sample_rate)
    uhd_tx.set_time_unknown_pps(uhd.time_spec(0))
    uhd_tx.set_center_freq(radio_freq, 0)
    uhd_tx.set_antenna("TX/RX", 0)
    uhd_tx.set_gain(gain, 0)
    return uhd_tx

if __name__ == "__main__":
    # ----------------------  setup argument parser  ------------------------
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("json", help="Scene config stored in json")
    parser.add_argument("--custom", default="",
        help="Custom folder of GNU radio components")
    args = parser.parse_args()

    # ---------------------------------  process  ---------------------------
    # update list of components
    COMP_CONSTRUCTORS.update( load_blocks(args.custom) )

    # run the simulation
    load_and_run_scenario(args.json)
