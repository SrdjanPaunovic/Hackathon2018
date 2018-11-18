import json
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from hackathon.utils.utils import *

__author__ = "Dusan Majstorovic"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"

with open(CFG.profile_file) as json_data:
    d = json.load(json_data)

gridStatus = []
buyingPrice = []
sellingPrice = []
currentLoad = []
solarProduction = []

for data_point in d:
    gridStatus.append(data_point['gridStatus'])
    buyingPrice.append(data_point['buyingPrice'])
    sellingPrice.append(data_point['sellingPrice'])
    currentLoad.append(data_point['currentLoad'])
    solarProduction.append(data_point['solarProduction'])


time_span = len(gridStatus) / CFG.sampleRate

t = np.arange(0., time_span, 1./CFG.sampleRate)

fig, ax = plt.subplots(3, sharex=True)
ax[0].step(t,gridStatus)
ax[0].set_title('Profiles')
ax[0].legend(['Grid status'], loc = 'upper right', fontsize = 'small')
ax[0].set_ylim(-0.1,1.1)
ax[0].grid(True, linestyle='--')

ax[1].step(t,buyingPrice)
ax[1].step(t,sellingPrice)
ax[1].legend(['Buying price', 'Selling price'], loc = 'upper right', fontsize = 'small')
ax[1].grid(True, linestyle='--')

ax[2].step(t,currentLoad)
ax[2].step(t,solarProduction)
ax[2].legend(['Total load', 'Solar production'], loc = 'upper right', fontsize = 'small')
ax[2].grid(True, linestyle='--')

plt.xlim(0, time_span)

formatter = matplotlib.ticker.FuncFormatter(lambda m, x: time.strftime('%H:%M', time.gmtime(m*60*60)))
ax[2].xaxis.set_major_formatter(formatter)

plt.tight_layout(pad=0.2, h_pad=1.0)

plt.show()
