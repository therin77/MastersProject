"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""


import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, window=1.0, length=1024):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Correlation/Synch Block',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.window = window
        self.length = length

    def work(self, input_items, output_items):
        """example: multiply with constant"""

        in_data = np.array(input_items[0])

        in_data = np.concatenate([np.zeros(self.length, dtype=np.complex64)])

        corr_data = np.correlate(in_data, in_data)

        output_items[0][:] = input_items[0]
                  
        #output_items[0][:self.length] = corr_data[len(in_data)-1:]
        
    
    
