##################################
#Master's Project OSU: gr-tempest implemntation in Python
#Developed by: Kate Gothberg
#Last Edited: 07/28/2025
##################################

#ToDo:
    #-SDR real time
    #-delay
    #-image in same spot/pane
    #-reverse image colors
    #-optimize
    #-create functions for blocks
    
    
##################################
#Functions
##################################

def autocorrelation(symbol_buffer, symbol_buffer_prev, M_list, M)   :
    
    corr_data = correlate(symbol_buffer, symbol_buffer_prev, mode='same')
    corr_data = corr_data / window

    M_inst = np.argmax(corr_data)
    M_list = np.append(M_list, M_inst)
    M = np.mean(M_list)
    
    return(M, M_list)

def rational_resampler()   :
    print("here")
    
def interpolate()   :
    print("here")
    
def display()   :
    print("here")
    
##################################
#Modules
##################################

#import uhd
import numpy as np
from scipy.signal import resample_poly, correlate
from matplotlib import pyplot as plt
import time

#for now grab samples from file, hope to implement in real-time
f = np.fromfile(open("samples_082525"), dtype=np.complex64)
samples = f[0: 30*2*833334] #30*2*833334]

"""
usrp = uhd.usrp.MultiUSRP("type=b200")
usrp.set_rx_freq(100e6)
"""

##################################
#Constants
##################################

fv = 60                                #frame rate
samp_rate = 50e6 #122880               #sample rate of SDR
Py = 1125 #624 gnu test             #number of vert pixels + blanking
Px = 2200 #801 gnu test  #number of hor pixels + blanking
py = 1080 #600 gnu test                          #number of vert pixels
px = 1920 #800   gnu test                            #number of vert pixels
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

##################################
#Main Program
##################################

start_time = time.time()
#iterate for all samples

while True:

    #add to current sample block for autocorr
    symbol_buffer = samples[(counter+1)*833333:(counter+2)*833333]
    symbol_buffer_prev = samples[counter*833333:(counter+1)*833333]
    

    #if block is full continue processing
    if len(symbol_buffer) == window:
        
        #iterate counter for video gui
        counter = counter + 1
        
        if counter % 30 == 0:
            
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
            #Display
            ##################################
        
            #reshape to correct number of rows, then interpolate down the columns
            rows = int(V)
            cols = int(np.floor(len(amp_real)/V))
            del_len = len(amp_real) - rows*cols
            amp_real = amp_real[:-del_len]
            matrix = np.reshape(amp_real,(rows,cols))
            
            #plot using plt, turn off axis
            plt.figure(clear=True)
            plt.figure(1);
            plt.imshow(matrix)
            plt.axis('off')
            plt.pause(.1)
            
            #timing
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Elapsed time using time.time(): {elapsed_time:.6f} seconds")
            
        else:
            
            #reset symbol_buffer and allocate prev buffer
            symbol_buffer_prev = symbol_buffer
            symbol_buffer = []

 

# Calculate and print the elapsed time
elapsed_time = end_time - start_time
print(f"Elapsed time using time.time(): {elapsed_time:.6f} seconds")