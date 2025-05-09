
"""
Correlation/Sync Block
Developed by Kate Gothberg
Last Edited: 5/9/25

"""


import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    
    """
    initialize the block
    params:
        in_sig: input samples
        out_sig: output samples
        window: number of samples to correlate over
    """
    def __init__(self, window=1.0):  
        gr.sync_block.__init__(
            self,
            name='Correlation/Synch Block', 
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        self.window = window

    """
    functional code over samples
    """
    def work(self, input_items, output_items):

        samples = input_items[0] #rename input samples
        symbol_buffer = []       #storage for each block of samples

        #iterate for all samples
        for i, sample in enumerate(samples):

            #add to sample block
            symbol_buffer.append(samples[i])

            #if block is full continue processing
            if len(symbol_buffer) > self.window:

                
                #correlation and reset of buffer
                corr_data = np.correlate(symbol_buffer, symbol_buffer, "full")
                symbol_buffer = []

                #output correlation samples
                for j in range(len(corr_data)-1):
                    print(corr_data[j])
                    output_items[0][j] = corr_data[j]

        return len(output_items[0])
