##################################
#Master's Project OSU: gr-tempest implemntation in Python
#Developed by: Kate Gothberg
#Last Edited: 07/20/2025
##################################

import uhd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import resample_poly, correlate
import PIL

#for now grab samples from file, hope to implement in real-time
f = np.fromfile(open("test_file_50M"), dtype=np.complex64)
samples = f[1: 1700000]

"""
usrp = uhd.usrp.MultiUSRP("type=b200")
usrp.set_rx_freq(100e6)
"""

fv = 60                              #frame rate
samp_rate = 50e6 #122880             #sample rate of SDR
Py = 624 #628 #1125 #1080                      #number of vert pixels + blanking
Px = 801 #1056 #1920 + 280 #740 #1920           #number of hor pixels + blanking
py = 600
px = 800
fp = Py*Px*fv                        #pixel rate
symbol_buffer = []                   #storage for each block of samples
symbol_buffer_prev = []              #storage of previous block/ frame
Tv = 1/(fv)                          #length of frame in time
window = np.floor(Tv * samp_rate)    #number of samples per frame 
M = int(.5*window)                   #default M
del_buff = 0                         #delay length (samples)
output = []


#iterate for all samples
for i, sample in enumerate(samples):

    #add to current sample block for autocorr
    symbol_buffer.append(samples[i])

    #if block is full continue processing
    if len(symbol_buffer) == window:

        #if two symbol buffers perform autocorr and rat resample
        if len(symbol_buffer_prev) == window:

            ##################################
            #Autocorrelation => M
            ##################################
            
            corr_data = correlate(symbol_buffer, symbol_buffer_prev, mode='same')
            corr_data = corr_data / window

            M = np.argmax(corr_data)

            corr_data = []
            
        ##################################
        #Rational Resampler
        ##################################
        
        V = Py
        H = np.floor(Px*samp_rate/fp)
        L = V*H
        
        resamp = resample_poly(symbol_buffer, L, M)
            
        #reset symbol_buffer and allocate prev buffer
        symbol_buffer_prev = symbol_buffer
        symbol_buffer = []
        
        ##################################
        #Complex to Real
        ##################################
        
        real = np.abs(resamp)
        
        ##################################
        #Delay
        ##################################
        
        zeros = np.zeros(del_buff)
        np.append(real, zeros)
        
        ##################################
        #Normalize
        ##################################
        gain = 256/np.max(real)
        amp_real = real*gain

        ##################################
        #Float to Short
        ##################################

        ##################################
        #Display
        ##################################
    
        rows = int(V)
        cols = int(np.floor(len(amp_real)/V))
        del_len = len(amp_real) - rows*cols
        amp_real = amp_real[:-del_len]
        matrix = np.reshape(amp_real,(rows,cols))
        screen = PIL.Image.fromarray(matrix)
        screen.show()
        

"""
#debug plots
plt.plot(samples)
plt.plot(output)
plt.legend(['data', 'resamp_poly'], loc='best')
plt.show()


plt.plot(samples)
plt.show()
"""
