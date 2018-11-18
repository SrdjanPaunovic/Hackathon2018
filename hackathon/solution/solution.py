"""This module is main module for contestant's solution."""

from hackathon.utils.control import Control
from hackathon.utils.utils import ResultsMessage, DataMessage, PVMode, \
    TYPHOON_DIR, config_outs
from hackathon.framework.http_server import prepare_dot_dir

BATTERY_MAX_POWER = 5.0


def worker(msg: DataMessage) -> ResultsMessage:

    if msg.grid_status:
        return grid_on(msg)
    else:
        return grid_off(msg)


def grid_on(msg: DataMessage) -> ResultsMessage:

    pwr_reference = 0.0
    load_three = True

    if msg.buying_price == 8 and msg.current_load > 6.5:
        load_three = False

    can_charge = msg.buying_price == 3 or (msg.selling_price == 0 and msg.current_load < msg.solar_production)
    if can_charge and msg.bessSOC < 1:
        pwr_reference = -1 * BATTERY_MAX_POWER  # punjenje
    elif msg.bessSOC < 0.25:
        pwr_reference = -0.5  # puni svakako ako je ispod 0.25
    elif msg.bessSOC > 0.27 and msg.selling_price == 3 and msg.buying_price == 8:
        pwr_reference = BATTERY_MAX_POWER  # praznjenje

    return ResultsMessage(data_msg=msg,
                            load_one= True,
                            load_two= True,
                            load_three= load_three,
                            power_reference = pwr_reference,
                            pv_mode=PVMode.ON)


def grid_off(msg: DataMessage) -> ResultsMessage:
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


def run(args) -> None:
    prepare_dot_dir()
    config_outs(args, 'solution')

    cntrl = Control()

    for data in cntrl.get_data():
        cntrl.push_results(worker(data))
