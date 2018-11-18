import json
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from hackathon.utils.utils import *

__author__ = "Dusan Majstorovic"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"

with open(CFG.results) as json_data:
    d = json.load(json_data)

overall = []
overall_energy = []
overall_penalty = []
overall_performance = []
energyMark = []
performance = []
bessSOC = []
bessOverload = []
bessPower = []
mainGridPower = []
penal = []
grid_status = []
current_load = []
solar_production = []
real_load = []
pv_power = []

for data_point in d:
    overall.append(data_point['overall'])
    overall_energy.append(data_point['overall_energy'])
    overall_penalty.append(data_point['overall_penalty'])
    overall_performance.append(data_point['overall_performance'])
    energyMark.append(data_point['energyMark'])
    performance.append(data_point['performance'])
    bessSOC.append(data_point['bessSOC'])
    bessOverload.append(data_point['bessOverload'])
    bessPower.append(data_point['bessPower'])
    mainGridPower.append(data_point['mainGridPower'])
    penal.append(data_point['penal'])
    grid_status.append(data_point['DataMessage']['grid_status'])
    current_load.append(data_point['DataMessage']['current_load'])
    solar_production.append(data_point['DataMessage']['solar_production'])
    real_load.append(data_point['real_load'])
    pv_power.append(data_point['pv_power'])

time_span = len(overall) / CFG.sampleRate

t = np.arange(0., time_span, 1./CFG.sampleRate)

fig, ax = plt.subplots(3, sharex=True)

ax[0].step(t, overall, picker=True)
ax[0].step(t, overall_energy)
ax[0].step(t, overall_penalty)
ax[0].step(t, overall_performance)
ax[0].set_title('Results')
ax[0].legend(['Overall cost', 'Energy cost', 'Penalty cost', 'Computational cost'], loc = 'upper right', fontsize = 'small')
ax[0].grid(True, linestyle='--')

ax[1].step(t, grid_status)
ax[1].step(t, bessSOC)
ax[1].step(t, bessOverload)
ax[1].legend(['Grid status', 'BESS SOC', 'BESS overload'], loc = 'upper right', fontsize = 'small')
ax[1].grid(True, linestyle='--')

ax[2].step(t, bessPower)
ax[2].step(t, mainGridPower)
ax[2].step(t, real_load)
ax[2].step(t, pv_power)
ax[2].legend(['BESS power', 'Main grid power', 'Total load', 'PV power'], loc = 'upper right', fontsize = 'small')
ax[2].grid(True, linestyle='--')


plt.xlim(0, time_span)

formatter = matplotlib.ticker.FuncFormatter(lambda m, x: time.strftime('%H:%M', time.gmtime(m*60*60)))
ax[2].xaxis.set_major_formatter(formatter)

plt.tight_layout(pad=0.2, h_pad=1.0)

plt.show()
