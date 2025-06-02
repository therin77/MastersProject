
"""
Correlation/Sync Block
Developed by Kate Gothberg
Last Edited: 5/15/25

"""

import numpy as np
from gnuradio import gr

class blk(gr.interp_block):   #gr.sync_block
    
    """
    initialize the block
    params:
        in_sig: input samples
        out_sig: output samples
        Px: number of pixels x axis
        Py: number of pixels y axis
        fv: refresh rate of monitor
        samp_rate: sampling rate of gnu
    """
    def __init__(self, Px=1920.0, Py= 1080.0, fv = 60.0, samp_rate = 50e6):  
        gr.sync_block.__init__(
            self,
            name='Correlation/Synch Block', 
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        self.Px = Px
        self.Py = Py
        self.fv = fv
        self.samp_rate = samp_rate

    """
    functional code over samples
    """
    def work(self, input_items, output_items):

        samples = input_items[0] #rename input samples
        symbol_buffer = []       #storage for each block of samples
        symbol_buffer_prev = []  #storage of previous block/ frame
        Tv = 1/(self.fv)         #length of frame in time
        window = np.floor(Tv * self.samp_rate)  #number of samples per frame 


        #iterate for all samples
        for i, sample in enumerate(samples):

            """
            Determine autocorr and max point
            """

            #add to sample block
            symbol_buffer.append(samples[i])

            #if block is full continue processing
            if len(symbol_buffer) == window:

                if len(symbol_buffer_prev) == window:
    
                    #correlation and reset of buffer
                    corr_data = np.correlate(symbol_buffer, symbol_buffer_prev, "same")
                    corr_data = corr_data / window

                    middle = np.argmax(corr_data)

                    corr_data = []
                
                #reset symbol_buffer and allocate prev buffer
                symbol_buffer_prev = symbol_buffer
                symbol_buffer = []

            """
            Linear Interpolator: Samples
            """
            V = self.Py
            H = np.floor(self.Px*self.samp_rate/self.fv)
            
            zeros_array = np.zeros(5000) #np.zeros(self.Px*self.Py-1) #np.zeros(1024)
            output = np.append(zeros_array, samples[i])
            for j in range(len(output)-1):
                    output_items[0][j] = output[j]


            
            #output_items[0][i*(self.Px*self.Py):(i+1)*(self.Px*self.Py)] = np.append(zeros_array, samples[i])
            

            #output_items[0][i] = samples[i]
        
        return len(output_items[0])
