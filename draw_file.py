import numpy as np
import matplotlib.pyplot as plt


NCHANNELS = 16

dat = np.fromfile('stream_log.bin','H')

nsamp =len(dat)/NCHANNELS
inputs = np.reshape(dat,(nsamp,NCHANNELS))

plot_channels = [1,3,4,5,6,7]

plt.plot(inputs[:,plot_channels])

chvals = inputs[-1,:]

for ch in range(NCHANNELS):
    plt.text(nsamp,chvals[ch],ch)

plt.show()

