# gr_tools
Python library to aid in running and debugging GNU Radio processes

## Usage

### Installing GRC

The [install_grc](gr_tools/install_grc.py) module supports installing a folder full of hierarchal blocks.  It uses the installed 'grcc' to compile the grc file.  A recursive loop is used to support installing GRC blocks that depend on one another.

~~~bash
$ python -m gr_tools.install_grc grc_folder --target ~/.grc_gnuradio
~~~

### Run Simulation
The [run_sim](gr_tools/run_sim.py) module is used to script running a hierarchal block.  It current supports input of (file source or message port in) and file sink on output.

Batch functions are available to configure the component of interest.

~~~python
# at ~/.grc_gnuradio to path to gain access to installed components
import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
from atsc_8vsb_transmit import atsc_8vsb_transmit

from gr_tools.run_sim import batch_run_file_source

# run with combinations of sample rate and snr levels
# the keys should match the parameters of the component
param_dict = {
    "sample_rate": [10e6, 20e6],
    "snr": [10, 20, 30],
}

# specify input and output formats.
in_spec = {"path":"input_file.bytes", "type":"BYTE", "repeat":True}
out_spec = {"path":"/tmp/out.32cf", "type":"COMPLEX", "n_items":1000000}

# run the batch of simulation
batch_run_file_source(
    atsc_8vsb_transmit, param_dict, "/tmp/base_name",
    in_spec, out_spec)
~~~