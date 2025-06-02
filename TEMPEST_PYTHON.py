##################################
#Master's Project OSU: gr-tempest implemntation in Python
#Developed by: Kate Gothberg
#Last Edited: 05/20/2025
##################################

import uhd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import resample_poly
import PIL

#for now grab samples from file, hope to implement in real-time
f = np.fromfile(open("test_file_5M"), dtype=np.complex64)
samples = f[1: 1000000]

"""
usrp = uhd.usrp.MultiUSRP("type=b200")
usrp.set_rx_freq(100e6)
"""

fv = 60                              #frame rate
samp_rate = 50e6 #122880              #sample rate of SDR
Py = 1125 #1080                      #number of vert pixels + blanking
Px = 1920 + 280 #740 #1920                       #number of hor pixels + blanking
fp = Py*Px*fv                        #pixel rate
symbol_buffer = []                   #storage for each block of samples
symbol_buffer_prev = []              #storage of previous block/ frame
Tv = 1/(fv)                          #length of frame in time
window = np.floor(Tv * samp_rate)    #number of samples per frame 
M = int(.5*window)                   #default M
del_buff = 10                        #delay length (samples)
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
            
            corr_data = np.correlate(symbol_buffer, symbol_buffer_prev, "same")
            corr_data = corr_data / window

            M = np.argmax(corr_data)

            corr_data = []
            
        ##################################
        #Rational Resampler
        ##################################
        
        V = Py
        H = np.floor(Px*samp_rate/fp)
        L = V*H
        resamp = resample_poly(symbol_buffer, L-1, M)
        
        #output = np.append(output, resamp)
            
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
        #Delay
        ##################################
        

"""
#debug plots
plt.plot(samples)
plt.plot(output)
plt.legend(['data', 'resamp_poly'], loc='best')
plt.show()


plt.plot(samples)
plt.show()
"""
