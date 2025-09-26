##################################
#Master's Project OSU: gr-tempest implemntation in Python
#Developed by: Kate Gothberg
#Last Edited: 09/05/2025
##################################

#ToDo:
    #-delay
    #-reverse image colors
    #-optimize
    
##################################
#Functions
##################################

#autocorrelation : finds index in sample block of largest correlation, avgs over time

#inputs:
#   -symbol_buffer: current block of samples being processed
#   -symbol_buffer_prev : previous block of samples, needed since autocorrelation
#   -M_list : previous indexes of max correlation in previous sample blocks
#   -M : index in sample block of max correlation
#outputs:
#   -M : max correlation value in sample block
#   -M_list : collection of past max correlation values from previous sample blocks
def autocorrelation(symbol_buffer, symbol_buffer_prev, M_list, M)   :
    
    corr_data = correlate(symbol_buffer, symbol_buffer_prev, mode='same')
    corr_data = corr_data / window

    M_inst = np.argmax(corr_data)
    M_list = np.append(M_list, M_inst)
    M = np.floor(np.mean(M_list))
    
    return(M, M_list)

#rational_resampler : upsamples and downsamples sample block to correct fidelity
#inputs:
#   -symbol_buffer: current block of samples being processed
#   -Py : total number of pixels vertical
#   -Px : total number of pixels horizontal
#   -samp_rate : sample rate of SDR
#   -fp : refresh rate of monitor, usually 60Hz
#outputs:
#   -resamp : resampled samples
def rational_resampler(symbol_buffer, Py, Px, samp_rate, fp)   :
    
    V = Py
    H = np.floor(Px*samp_rate/fp)
    L = V*H
    
    resamp = resample_poly(symbol_buffer, L, M)
    
    return resamp
    
#interpolate : reshape to correct number of rows, then interpolate down the columns
#inputs: 
#   -Py : number of rows/pixels vertically
#   -amp_real : samples after gain is applied
#outputs:
#   -matrix : reshaped samples to correct dimensions
def interpolate(Py, amp_real)   :
    
    V = Py
    rows = int(V)
    cols = int(np.floor(len(amp_real)/V))
    del_len = len(amp_real) - rows*cols
    amp_real = amp_real[:-del_len]
    matrix = np.reshape(amp_real,(rows,cols))
    
    return matrix
    
#display : graph monitor
#inputs:
#   -matrix : reshaped samples to be displayed
#   -ax1 : initialize plot for display 
def display(matrix, ax1)   :
    
    im1 = ax1.imshow(matrix)
    im1.set_data(matrix)
    plt.pause(.1)
    
##################################
#Imported Modules
##################################

import uhd
import numpy as np
from scipy.signal import resample_poly, correlate
from matplotlib import pyplot as plt
import time

##################################
#Constants
##################################

fv = 60                                #frame rate
samp_rate = 50e6 #122880               #sample rate of SDR
"""
Py = 624              #number of vert pixels + blanking
Px = 801   #number of hor pixels + blanking
py = 600                               #number of vert pixels
px = 800                               #number of vert pixels
"""
Py = 1125              #number of vert pixels + blanking
Px = 2200   #number of hor pixels + blanking
py = 1080                             #number of vert pixels
px = 1920

##################################
#Main Program
##################################

#calculations to begin the program

fp = Py*Px*fv                          #pixel rate
symbol_buffer = []                     #storage for each block of samples
symbol_buffer_prev = []                #storage of previous block/ frame
Tv = 1/(fv)                            #length of frame in time
window = np.floor(Tv * samp_rate)      #number of samples per frame 
M = int(.5*window)                     #avg m used to make frame; default half of interval
M_list = []                            #list of all M's calculated
M_inst = 0                             #M of single frame examined
del_buff = 0                           #delay length (samples)
counter = 0                            #number of frames examined, do process 1/s ie after 60 frames
plt.ion()                              #initialize plt interactive for display
ax1 = plt.subplot(111)                 #initialize plt plot for display

#debug, for time inbetween frames
#start_time = time.time()
window_int = int(window)

#initialize USRP
usrp = uhd.usrp.MultiUSRP("num_recv_frames=1000")

#main loop
while True:

    #receive samples and transpose
    samples = usrp.recv_num_samps(2*window_int, 2*fp, samp_rate, [0], 50) # units: N, Hz, Hz, list of channel IDs, dB
    samples = samples.T

    #create block of samples numbering window to be processed
    symbol_buffer = samples[(1)*window_int:(2)*window_int]
    symbol_buffer_prev = samples[0:(1)*window_int]

    #if block is full continue processing
    if len(symbol_buffer) == window_int:

        #counter iterates every time that a new set of samples is processed
        counter = counter + 1
        
        #for timings sake only process every how ever many sample blocks
        if counter % 1 == 0:
            
            end_time = time.time()
    
            #if two symbol buffers perform autocorr and rat resample
            if len(symbol_buffer_prev) == window:
    
                ##################################
                #Autocorrelation => M
                ##################################
                
                M, M_list = autocorrelation(symbol_buffer, symbol_buffer_prev, M_list, M)
                
            ##################################
            #Rational Resampler
            ##################################
            
            resamp = rational_resampler(symbol_buffer, Py, Px, samp_rate, fp)
                
            #reset symbol_buffer and allocate prev buffer
            
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
            #Display
            ##################################
        
            #reshape to correct number of rows, then interpolate down the columns
            matrix = interpolate(Py, amp_real)
            
            #plot using plt, turn off axis
            display(matrix, ax1)
            
            #timing
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            #print(f"Elapsed time using time.time(): {elapsed_time:.6f} seconds")
                
 

# Calculate and print the elapsed time
#elapsed_time = end_time - start_time
#print(f"Elapsed time using time.time(): {elapsed_time:.6f} seconds")