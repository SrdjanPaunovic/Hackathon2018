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
previous_grid_status = True
blackout_counter = 0

def worker(msg: DataMessage) -> ResultsMessage:
    global blackout_counter
    global previous_grid_status

    if not previous_grid_status and msg.grid_status:
        blackout_counter += 1
        with open('output.txt', 'a') as f:
            f.write(str(blackout_counter) + '\n')

    previous_grid_status = msg.grid_status
    if msg.grid_status:
        return gridOn(msg)
    else:
        return gridOff(msg)

def gridOn(msg: DataMessage) -> ResultsMessage:

    pwr_reference = 0.0

    load_three = True

    if msg.buying_price == 8 and msg.current_load > 6.5:
        load_three = False

    canCharge = msg.buying_price == 3 or (msg.selling_price == 0 and msg.current_load < msg.solar_production)
    if canCharge and msg.bessSOC < 1:
        pwr_reference = -5.0  # punjenje
    elif msg.bessSOC < 0.25:
        pwr_reference = -0.5  # puni svakako ako je ispod 0.25
    elif msg.bessSOC > 0.27 and msg.selling_price == 3 and msg.buying_price == 8:
        pwr_reference = 5.0  # praznjenje

    # if blackout_counter == 5 and msg.bessSOC > 0.1 and msg.selling_price == 3:
    #     pwr_reference = 5.0
    #
    # if blackout_counter == 5 and pwr_reference < 0:
    #     pwr_reference = 0.0

    return ResultsMessage(data_msg=msg,
                            load_one= True,
                            load_two= True,
                            load_three= load_three,
                            power_reference = pwr_reference,
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
