# gr_tools
Python library to aid in running and debugging GNU Radio processes

| Module | Description |
| --- | --- |
| install_grc | Install a folder of GRC files |
| run_sim | Run simulation with multiple combinations of parameters |
| run_simulator_custom | Load a scenario from a json file |

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

### Run Simulator Custom
[run_simulator_custom](gr_tools/run_simulator_custom.py) supports running a scenario described in a json file.  Example json files available in the example folder.

'components' is specified as a dict with "unique id" per component.
Each component is a dictionary with 'key' specifying the component type and 'val', specifying the parameters of the component.

'connections' is a list of connections.  A connection is a list of 4 elements.
* Unique Id of the first component
* Port of the first component
* unique Id of the second component
* port of the second component

'simulation' specifies how to run the scene.
* Data
  * This requires a 'head' component to specify the number of samples to limit the simulation.
* Time
  * value should have 'duration', to specify time in seconds to run simulation
* User
  * User is prompted to hit enter to stop the simulation
~~~bash
$ python -m gr_tools.run_simulator_custom example/usrp_to_file.json
~~~