import os
import numpy as np
from matplotlib import mlab
import matplotlib.pyplot as plt
sample_rate_Hz = 3200
length_s = 2
os.system(f'sudo adxl345spi -t {length_s} -f {sample_rate_Hz} -s out.csv')
acc_data = np.genfromtxt('out.csv', delimiter=',', names=True)
acc_x, freq_x, _ = mlab.specgram(acc_data['x'], Fs=sample_rate_Hz, NFFT=sample_rate_Hz * length_s)
acc_y, freq_y, _ = mlab.specgram(acc_data['y'], Fs=sample_rate_Hz, NFFT=sample_rate_Hz * length_s)
acc_z, freq_z, _ = mlab.specgram(acc_data['z'], Fs=sample_rate_Hz, NFFT=sample_rate_Hz * length_s)
plt.plot(freq_x[10:], acc_x[10:], label='x', linewidth=0.5)
plt.plot(freq_y[10:], acc_y[10:], label='y', linewidth=0.5)
plt.plot(freq_z[10:], acc_z[10:], label='z', linewidth=0.5)
plt.yscale('log')
plt.xlim((0, 160))
plt.legend(loc='upper right')
plt.savefig('spectrum.png')