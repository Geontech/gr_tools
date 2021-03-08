#!/usr/bin/env python
"""Module to control USRP

Use Cases
---------
Receive Only
- Record to File (USRP RX -> FileSink)
- Receive Stream (USRP RX -> TCP/UDP)

Broadcast Only
- Playback/broadcast file (FileSource -> USRP TX)
- Broadcast stream (TCP/UDP -> USRP TX)

Hybrid
- Forward (RX -> TX), potentially same frequency
- Playback + Record (Add over the air effects to simulated signals)
"""
import json
import sys
import time
from gnuradio import gr, blocks, uhd

# get appropriate user prompt based on Python
if sys.version_info.major == "2":
    user_prompt = raw_input
else:
    user_prompt = input

COMP_CONSTRUCTORS = {
    "usrp_source":uhd.usrp_source,
    "usrp_sink": uhd.usrp_sink
}

def load_blocks():
    """Load blocks available through gnuradio

    Returns
    -------
    out : dict
        The dictionary of blocks available in
    """
    from inspect import getmembers, isfunction
    tmp = getmembers(blocks, isfunction)
    return dict(tmp)

# update with gnuradio.blocks
COMP_CONSTRUCTORS.update(load_blocks())

def load_and_run_scenario(json_file):
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

        if c_comp_type == "uhd_source":
            c_comp = config_uhd_source(**c_comp_value)
        elif c_comp_type == "uhd_sink":
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
        # TODO: assert that a head component is in components
        top.run(max_noutput_items=simm["value"]["max_noutput_items"])
    else:
        raise RuntimeError("Unexpected type of simulation")

def config_uhd_source(device, sample_rate, radio_freq, gain):
    """
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
    args = parser.parse_args()

    # ---------------------------------  process  ---------------------------
    load_and_run_scenario(args.json)
