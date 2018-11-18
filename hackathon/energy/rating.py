"""This module handles rating of solution's returned messages."""

__author__ = "Miroslav Nikolic"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"

from typing import Tuple
from hackathon.utils.utils import DataMessage, PVMode, ResultsMessage, CFG

penal_l1_cnt = 0
penal_l2_cnt = 0
penal_l3_cnt = 0
overload_cnt = 0

PENAL_L1_INIT = 20
PENAL_L1_CONT = 1

PENAL_L2_INIT = 4
PENAL_L2_CONT = 0.4

PENAL_L3_CONT = 0.3


def real_load(load_one: int,
              load_two: int,
              load_three: int,
              current_load: float) -> float:
    return (load_one * 0.2 + load_two * 0.4 + load_three * 0.4) * current_load


def main_grid(on: bool,
              real_load: float,
              power_reference: float,
              solar_production: float,
              pv_mode: PVMode) -> float:
    s_prod = solar_production if pv_mode == PVMode.ON else 0
    if on:
        return real_load - power_reference - s_prod
    else:
        return real_load - s_prod


def energy_mark(consumption: float,
                bess_sell: float) -> float:
    return consumption - bess_sell


def get_physics_metrics(d: DataMessage, r: ResultsMessage,
                        spent_time: float, match: bool) \
                        -> Tuple[float, float, float, float, float, float,
                                 float, bool, float]:
    global overload_cnt
    global penal_l1_cnt
    global penal_l2_cnt

    BESS_MAX_POWER = 5
    BESS_CAPACITY = 20

    penal = 0.0
    if r.power_reference > BESS_MAX_POWER:
        r.power_reference = BESS_MAX_POWER
    elif r.power_reference < -BESS_MAX_POWER:
        r.power_reference = -BESS_MAX_POWER

    if not r.load_one:
        if penal_l1_cnt == 0:
            penal += PENAL_L1_INIT + PENAL_L1_CONT
            penal_l1_cnt += 1
        else:
            penal += PENAL_L1_CONT
    else:
        penal_l1_cnt = 0

    if not r.load_two:
        if penal_l2_cnt == 0:
            penal += PENAL_L2_INIT + PENAL_L2_CONT
            penal_l2_cnt += 1
        else:
            penal += PENAL_L2_CONT
    else:
        penal_l2_cnt = 0

    if not r.load_three:
        penal += PENAL_L3_CONT

    if d.grid_status:
        if (d.bessSOC == 0 and r.power_reference > 0) \
           or (d.bessSOC == 1 and r.power_reference < 0):
            r.power_reference = 0

        r_load = real_load(int(r.load_one), int(r.load_two),
                           int(r.load_three), d.current_load)

        mg = main_grid(True, r_load, r.power_reference,
                       d.solar_production, r.pv_mode)
        # we sell
        if mg < 0:
            bess_sell = abs(mg) * d.selling_price / CFG.sampleRate
            consumption = 0.0
        else:
            consumption = mg * d.buying_price / CFG.sampleRate
            bess_sell = 0

        current_power = r.power_reference

        soc_bess = d.bessSOC - r.power_reference / (CFG.sampleRate * BESS_CAPACITY)

        overload = False
    elif not d.grid_status:
        r_load = real_load(int(r.load_one), int(r.load_two),
                           int(r.load_three), d.current_load)

        current_power = main_grid(False, r_load, r.power_reference,
                                  d.solar_production, r.pv_mode)

        soc_bess = d.bessSOC - current_power / (CFG.sampleRate * BESS_CAPACITY)

        if abs(current_power) > BESS_MAX_POWER or (soc_bess >= 1 and current_power < 0) \
           or (soc_bess <= 0 and current_power > 0):
            overload = True
            overload_cnt += 1
        else:
            overload = False
            overload_cnt = 0

        if overload_cnt > 1:
            penal = PENAL_L1_INIT + PENAL_L1_CONT + PENAL_L2_INIT + PENAL_L2_CONT + PENAL_L3_CONT
            current_power = 0
            r.load_one = False
            r.load_two = False
            r.load_three = False
            r.pv_mode = PVMode.OFF
            overload = False
            overload_cnt = 0
            soc_bess = d.bessSOC
            r_load = 0

        consumption = 0
        mg = 0
        bess_sell = 0

    if 0 > soc_bess:
        soc_bess = 0
    if soc_bess > 1:
        soc_bess = 1

    TARGET_1MS_PRICE = 100  # targeted daily price for 1ms avg spent time
    performance_mark = (spent_time*1000) * (24/(TARGET_1MS_PRICE*CFG.sampleRate))

    em = energy_mark(consumption, bess_sell)
    pv_power = d.solar_production if r.pv_mode == PVMode.ON else 0
    return em, performance_mark, mg, penal, r_load, pv_power, soc_bess, \
        overload, current_power
