"""This module contains mathematical functions needed to generate
data."""

__author__ = "Miroslav Nikolic and Novak Boskov"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"

import json
from math import pi, cos
from functools import partial
from typing import Optional, Tuple, List, Dict, Union


def buying_price(t: float) -> Optional[float]:
    if t < 7 or 23 <= t <= 24:
        return 3
    elif 7 <= t < 23:
        return 8
    else:
        raise Exception('Time should be between 0 and 24')


def selling_price(t: float) -> Optional[float]:
    if 0 <= t < 11 or 17 <= t <= 24:
        return 3
    elif 11 <= t < 17:
        return 0
    else:
        raise Exception('Time should be between 0 and 24')


def current_load(t: float, load_scaling=1.0, load_scaling_prev=1.0) -> float:
    if 3 <= t < 13:
        return (load_scaling * 1.5) * (cos(1/5 * pi * (t - 8)) + 1) + 2
    elif 13 <= t <= 24:
        return (load_scaling * 3) * (cos(1/7 * pi * (t - 20)) + 1) + 2
    elif 0 <= t < 3:
        return (load_scaling_prev * 3) * (cos(1/7 * pi * (t + 4)) + 1) + 2
    else:
        raise Exception('Time should be between 0 and 24')


def solar_produciton(t: float, solar_scaling=1.0) -> float:
    if 7 <= t < 19:
        return (solar_scaling * 2.5) * (cos(1/6 * pi * (t - 13)) + 1)
    elif 0 <= t < 7 or 19 <= t <= 24:
        return 0
    else:
        raise Exception('Time should be between 0 and 24')


def samples_to_time(sampleRate: int, sample: int) -> float:
    """Converts sample number to day time."""
    return sample / sampleRate


def gen_profile(sampleRate: int, load_scaling=1.0,
                load_scaling_prev=1.0, solar_scaling=1.0, blackouts=[]) \
    -> Tuple[str, List[Dict[str, Union[float, bool]]]]:
    """Generates ideal profile."""
    to_time = partial(samples_to_time, sampleRate)
    data = []

    for s in range(sampleRate*24):
        t = to_time(s)
        gs = 1
        if blackouts:
            for blackout in blackouts:
                if blackout[0] <= t < blackout[1]:
                    gs = 0
        data.append({'gridStatus': gs,
                     'buyingPrice': buying_price(t),
                     'sellingPrice': selling_price(t),
                     'currentLoad': current_load(t,
                                                 load_scaling,
                                                 load_scaling_prev),
                     'solarProduction': solar_produciton(t, solar_scaling)})

    return json.dumps(data), data
