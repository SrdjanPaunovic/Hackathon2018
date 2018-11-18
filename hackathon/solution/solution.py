"""This module is main module for contestant's solution."""

from hackathon.utils.control import Control
from hackathon.utils.utils import ResultsMessage, DataMessage, PVMode, \
    TYPHOON_DIR, config_outs
from hackathon.framework.http_server import prepare_dot_dir
from scipy.optimize import minimize
import numpy

open('output.txt', 'w').close()

cheapPrice = 0
BATTERY_MAX_POWER = 5.0
prev_x = numpy.array([1.0,1.0,1.0, -1])
def worker(msg: DataMessage) -> ResultsMessage:

    if msg.grid_status:
        return smartGridOn(msg)
    else:
        return gridOff(msg)


def getParams(msg: DataMessage) :

    k1 = msg.buying_price
    k2 = msg.selling_price
    A = msg.current_load
    B = msg.solar_production

    def f(x):
        loadCost = k1*A*(0.2*x[0]+0.4*x[1]+0.4*x[2])
        oneTimePenaltyCost = 25.0 - 20.0*(x[0] - (1 - prev_x[0])) - 4.0*(x[1] - (1 - prev_x[1])) - x[2]
        downTimePenalyCost = 1.7 - 1*prev_x[0] - 0.4*prev_x[1] - 0.3*prev_x[2]
        generatedPrice = (5.0*x[3] + B)*k2

        return loadCost + 22.0*(oneTimePenaltyCost + downTimePenalyCost) - generatedPrice
    x0_bounds = ( 0, 1)
    x1_bounds = ( 0, 1)
    x2_bounds = ( 0, 1)
    x3_bounds = ( -1, 1)
    initial_value = prev_x
    b = [x0_bounds, x1_bounds, x2_bounds, x3_bounds]
    return minimize(f,x0=initial_value,args=(),method='L-BFGS-B', bounds = b)

def smartGridOn(msg: DataMessage) -> ResultsMessage:
    res = getParams(msg)
    global prev_x
    prev_x = res.x
    pwr_reference = 0.0
    boolVector = res.x == 1.0
    
    if res.x[3] < 0 and msg.bessSOC < 1:
        pwr_reference = -5.0  # punjenje
    elif msg.bessSOC < 0.25:
        pwr_reference = -0.5  # puni svakako ako je ispod 0.25
    elif res.x[3] > 0 and msg.bessSOC > 0.27 :
        pwr_reference = 5  # praznjenje

    return ResultsMessage(data_msg=msg,
                            load_one = bool(boolVector[0]),
                            load_two = bool(boolVector[1]),
                            load_three = bool(boolVector[2]),
                            power_reference = float(pwr_reference),
                            pv_mode = PVMode.ON)

def gridOn(msg: DataMessage) -> ResultsMessage:

    pwr_reference = 0.0

    canCharge = msg.buying_price == 3 or (msg.selling_price == 0 and msg.current_load < msg.solar_production)
    if canCharge and msg.bessSOC < 1:
        pwr_reference = -5.0  # punjenje
    elif msg.bessSOC < 0.25:
        pwr_reference = -0.1  # puni svakako ako je ispod 0.25
    elif msg.bessSOC > 0.27 and msg.selling_price == 3 and msg.buying_price == 8:
        pwr_reference = 5  # praznjenje

    return ResultsMessage(data_msg=msg,
                            load_one= True,
                            load_two= True,
                            load_three= True,
                            power_reference = float(pwr_reference),
                            pv_mode=PVMode.ON)

def gridOff(msg: DataMessage) -> ResultsMessage:
    load_one=True
    load_two=True
    load_three=True
    power_reference=0.0
    pv_mode=PVMode.ON

    if msg.bessSOC > 0.8 or  msg.current_load + BATTERY_MAX_POWER < msg.solar_production:
        pv_mode = PVMode.OFF
        if msg.current_load < BATTERY_MAX_POWER:
            power_reference = msg.current_load
        elif msg.current_load*0.6 < BATTERY_MAX_POWER:
            power_reference = msg.current_load*0.6
            load_three = False
        elif msg.current_load*0.2 < BATTERY_MAX_POWER:
            power_reference = msg.current_load*0.2
            load_three = False
            load_two = False
    else:

        if msg.current_load <= msg.solar_production:
            power_reference = 0.0

        elif msg.current_load <= msg.solar_production + BATTERY_MAX_POWER:

            if msg.current_load - msg.solar_production > BATTERY_MAX_POWER:
                load_three = False
                power_reference = msg.current_load * 0.6 - msg.solar_production
            else:
                power_reference = msg.current_load - msg.solar_production
        else:
            if msg.current_load*0.6 <= msg.solar_production + BATTERY_MAX_POWER:
                load_three = False
                power_reference = msg.current_load*0.6 - msg.solar_production
            elif msg.current_load * 0.2 <= msg.solar_production + BATTERY_MAX_POWER:
                load_three = False
                load_two = False
                power_reference = msg.current_load*0.2 - msg.solar_production

    return ResultsMessage(data_msg=msg,
                            load_one=load_one,
                            load_two=load_two,
                            load_three=load_three,
                            power_reference=power_reference,
                            pv_mode=pv_mode)



    # if msg.current_load <= msg.solar_production:
    #     if msg.bessSOC > 0.8 :
    #         return ResultsMessage(data_msg=msg,
    #                           load_one=True,
    #                           load_two=True,
    #                           load_three=False,
    #                           power_reference=msg.current_load,
    #                           pv_mode=PVMode.OFF) 
                            
    #     return ResultsMessage(data_msg=msg,
    #                           load_one=True,
    #                           load_two=True,
    #                           load_three=False,
    #                           power_reference=0.0,
    #                           pv_mode=PVMode.ON)
    # elif msg.current_load <= msg.solar_production + 5.0:

    #     return ResultsMessage(data_msg=msg,
    #                           load_one=True,
    #                           load_two=True,
    #                           load_three=False,
    #                           power_reference=msg.current_load - msg.solar_production,
    #                           pv_mode=PVMode.ON)
    # else:
    #     return ResultsMessage(data_msg=msg,
    #                           load_one=True,
    #                           load_two=True,
    #                           load_three=False,
    #                           power_reference=5.0,
    #                           pv_mode=PVMode.ON)


def run(args) -> None:
    prepare_dot_dir()
    config_outs(args, 'solution')

    cntrl = Control()

    for data in cntrl.get_data():
        cntrl.push_results(worker(data))
