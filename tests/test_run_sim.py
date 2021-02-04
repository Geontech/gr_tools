import numpy as np
from gnuradio import blocks, gr
from gr_tools import run_sim
def test_file_sim():
    """
    Connect a file source -> multiply_const -> file_sink
    """
    r = np.random.rand(10000)
    r.astype(np.complex64).tofile("/tmp/input.32cf")

    # ------------------------- prepare parameters   ------------------------
    out_limit = 40000
    in_sig = {
        "path":"/tmp/input.32cf", "type":run_sim.DTYPE["COMPLEX"], "repeat":True
    }

    out_sig = {
        "path":"/tmp/output.32cf", "type":run_sim.DTYPE["COMPLEX"], "n_items":out_limit
    }

    # load a component from gnuradio blocks
    component = blocks.multiply_const_cc(1.0)

    # ------------------------  run ------------------------------------------
    run_sim.run_file_source(component, in_sig, out_sig)
    output = np.fromfile("/tmp/output.32cf", dtype=np.complex64)

    # verify that head is used and limits output to specified ammount
    print("Length of output = %d"%len(output))
    assert len(output) == out_limit,\
        "Limit specified (%d) does not match len output(%d)"%\
            (out_limit, len(output))