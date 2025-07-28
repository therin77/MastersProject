##################################
#Master's Project OSU: gr-tempest implemntation in Python
#Developed by: Kate Gothberg
#Last Edited: 07/28/2025
##################################

#ToDo:
    #-SDR real time
    #-SDR samples to test
    #-avg M
    #-image in same spot/pane
    #-reverse image colors
    #-multithread

#import uhd
import numpy as np
from scipy.signal import resample_poly, correlate
import PIL
from matplotlib import pyplot as plt
import time

#for now grab samples from file, hope to implement in real-time
f = np.fromfile(open("test_file_50M"), dtype=np.complex64)
samples = f[0: 20*2*833334]

"""
usrp = uhd.usrp.MultiUSRP("type=b200")
usrp.set_rx_freq(100e6)
"""

fv = 60                                #frame rate
samp_rate = 50e6 #122880               #sample rate of SDR
Py = 624 #628 #1125 #1080              #number of vert pixels + blanking
Px = 801 #1056 #1920 + 280 #740 #1920  #number of hor pixels + blanking
py = 600                               #number of vert pixels
px = 800                               #number of vert pixels
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

start_time = time.time()
#iterate for all samples
for i, sample in enumerate(samples):

    #add to current sample block for autocorr
    symbol_buffer.append(samples[i])

    #if block is full continue processing
    if len(symbol_buffer) == window:
        
        #iterate counter for video gui
        counter = counter + 1
        
        if counter % 10 == 0:
            
            end_time = time.time()

            #if two symbol buffers perform autocorr and rat resample
            if len(symbol_buffer_prev) == window:
                
    
                ##################################
                #Autocorrelation => M
                ##################################
                
                corr_data = correlate(symbol_buffer, symbol_buffer_prev, mode='same')
                corr_data = corr_data / window
    
                M_inst = np.argmax(corr_data)
                M_list = np.append(M_list, M_inst)
                M = np.mean(M_list)
    
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
            #Display
            ##################################
        
            rows = int(V)
            cols = int(np.floor(len(amp_real)/V))
            del_len = len(amp_real) - rows*cols
            amp_real = amp_real[:-del_len]
            matrix = np.reshape(amp_real,(rows,cols))
            
            plt.figure(1); plt.clf()
            plt.imshow(matrix)
            plt.title('Number')
            plt.pause(.1)
            
            #reset counter
            counter = 0
            
            #screen = PIL.Image.fromarray(matrix)
            #screen.show()
        else:
            
            #reset symbol_buffer and allocate prev buffer
            symbol_buffer_prev = symbol_buffer
            symbol_buffer = []


#end_time = time.time()

# Calculate and print the elapsed time
elapsed_time = end_time - start_time
print(f"Elapsed time using time.time(): {elapsed_time:.6f} seconds")