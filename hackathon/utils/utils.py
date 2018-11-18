"""This module contains utilities that can be used from solution as
well as from framework.

"""

import sys
import os
import re
import time
from functools import partial
from configparser import ConfigParser
import pickle
from enum import Enum
import zmq
from typing import Tuple, Optional, List, Any

__author__ = "Novak Boskov"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"

TYPHOON_DIR = '.typhoon'
LATEST_RESULT = None


class DataMessage:
    """Message that is sent by the framework to the solution."""
    def __init__(self, id,
                 grid_status: bool,
                 # True or False, depending on the grid being available or not, in each moment
                 buying_price: float,
                 # The price of the energy from the grid, in each moment in time
                 selling_price: float,
                 # The price of the energy being "sold" to the grid, in each moment in time
                 current_max_load: float,
                 # Maximum theoretical power of all the loads, in each moment in time
                 solar_production: float,
                 # Theoretical power available from the solar panel
                 bessSOC: float,
                 # State Of Charge od the battery energy storage system
                 bessOverload: bool,
                 # True or False, depending on whether the battery is overloaded, or not
                 mainGridPower: float,
                 # Power of the energy taken from, or "returned" to the grid (therefore, might be negative)
                 bessPower: float) -> None:
                 # Power of the energy taken from, or "returned" to the battery (positive when discharging)
        self.id = id
        self.grid_status = grid_status
        self.buying_price = buying_price
        self.selling_price = selling_price
        self.current_load = current_max_load
        self.solar_production = solar_production
        self.bessSOC = bessSOC
        self.bessOverload = bessOverload
        self.mainGridPower = mainGridPower
        self.bessPower = bessPower

    def __str__(self):
        return "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}" \
            .format(self.id, self.grid_status, self.buying_price,
                    self.selling_price, self.current_load,
                    self.solar_production, self.bessSOC,
                    self.bessOverload, self.mainGridPower, self.bessPower)


class PVMode(Enum):
    """Photo-voltaic panel working mode."""
    OFF = 0
    ON = 1


class ResultsMessage:
    """Message that is sent back to the framework by the solution."""
    def __init__(self, data_msg: DataMessage,
                 load_one: bool,
                 # True or False, depending on whether the first load is on or off
                 load_two: bool,
                 # True or False, depending on whether the second load is on or off
                 load_three: bool,
                 # True or False, depending on whether the third load is on or off
                 power_reference: float,
                 # Describing how much power should the battery be using (positive when discharging)
                 pv_mode: PVMode) -> None:
                 # True or False, depending on whether the solar panel is being used or not
        self.data_msg = data_msg
        self.load_one = load_one
        self.load_two = load_two
        self.load_three = load_three
        self.power_reference = power_reference
        self.pv_mode = pv_mode

    def __str__(self):
        return "{}: {}, {}, {}, {}, {}" \
            .format(self.data_msg, self.load_one, self.load_two,
                    self.load_three, self.power_reference, self.pv_mode)

    def validate(self):
        if not type(self.load_one) is bool:
            raise Exception('ResultsMessage load_one should be a bool.')
        elif not type(self.load_two) is bool:
            raise Exception('ResultsMessage load_two should be a bool.')
        elif not type(self.load_three) is bool:
            raise Exception('ResultsMessage load_three should be a bool.')
        elif not type(self.power_reference) is float:
            raise Exception('ResultsMessage power_reference should be a float.')
        elif not type(self.pv_mode) is PVMode:
            raise Exception(('ResultsMessage pv_mode should be a value'
                             'from PVMode enum: {} or {}')
                            .format(PVMode.OFF, PVMode.ON))

        return self


def bind_sub_socket(address: str, port: int) -> \
    Optional[Tuple[zmq.Socket, zmq.Context]]:
    """Make subscribe socket and return pair of socket itself and its
    context

    """
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    try:
        socket.connect('tcp://{}:{}' .format(address, port))
        socket.setsockopt(zmq.SUBSCRIBE, b'')
        print('Subscribe socket connected at {}:{}.'.format(address, port))
        return socket, context
    except Exception as e:
        print('Connection to socket at {}:{} has failed.'
              .format(address, port), file=sys.stderr)
        print(e)
        exit()


def bind_pub_socket(address: str, port: int) -> \
    Optional[Tuple[zmq.Socket, zmq.Context]]:
    """Same as bind_sub_socket but for publish socket"""
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    try:
        socket.bind("tcp://{}:{}".format(address, port))
        return socket, context
    except Exception as e:
        print('Connection to socket at {}:{} has failed.'
              .format(address, port), file=sys.stderr)
        print(e)
        exit()


def safe_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except:
        return None


def safe_bool(s: str) -> Optional[bool]:
    return True if s == 'True' else False


def safe_path(s: str) -> Optional[str]:
    return os.path.join(*re.split('/|\\\\', s))


class Config:
    """Class that represents configuration file.

    It is initialized only once when this module is imported. The aim
    is to have only one instance of this class that could be imported
    wherever it is needed - CFG.

    """
    def __init__(self):
        """
        socket_in_port - port used by framework to send data to solution
        socket_out_port - port used by solution to send calculated data to framework
        in_address - IP address for socket_in_port
        out_address - IP address for socket_out_port
        """
        conf = self.get_conf()
        sockets = partial(self.get_from, conf, 'sockets')
        results = partial(self.get_from, conf, 'results')
        framework = partial(self.get_from, conf, 'framework')

        self.in_port = safe_int(sockets('inPort')) # type: Optional[int]
        self.out_port = safe_int(sockets('outPort')) # type: Optional[int]
        self.in_address = sockets('inAddress') # type: Optional[str]
        self.out_address = sockets('outAddress') # type: Optional[str]
        self.results = safe_path(
            results('resultsFile')) # type: Optional[str]
        self.results_dump = self.get_dump_name(
            self.results) # type Optional[str]
        self.results_http_server_port = safe_int(
            results('resultsHTTPServerPort')) # type: Optional[int]
        self.shutdown_http_server = safe_bool(
            results('shutdownHTTPServer')) # type: Optional[bool]
        self.days = eval(
            framework('days')) or range(1,6) # type List[int]
        self.sampleRate = safe_int(
            framework('sampleRate'))  # type: Optional[int]
        self.framework_lapse_time = safe_int(
            framework('frameworkLapseTime')) # type: Optional[int]
        self.max_results_wait = safe_int(
            framework('maxResultsWait')) # type: Optional[int]
        self.DBG = safe_bool(framework('DBG')) # type: Optional[bool]
        self.DBGPhysics = safe_bool(
            framework('DBGPhysics')) # type: Optional[bool]
        self.profile_file = safe_path(
            framework('profileFile')) # type: Optional[str]
        self.physics_init = safe_path(
            framework('physicsInit')) # type: Optional[str]

    @staticmethod
    def get_conf() -> ConfigParser:
        """Read configuration file to a dictionary."""
        conf_fname = 'params.conf'

        try:
            with open(conf_fname, 'r'):
                pass
        except FileNotFoundError:
            print('Configuration file is not foud.' + 2*os.linesep +
                  'This script normally looks for params.conf in current directory.',
                  file=sys.stderr)
            return None

        cp = ConfigParser()
        cp.read(conf_fname)
        return cp

    @staticmethod
    def get_from(cp: ConfigParser, section: str, key: str) \
        -> Optional[str]:
        try:
            return cp[section][key]
        except:
            return None

    @staticmethod
    def get_dump_name(results: str) -> str:
        return os.path.splitext(results)[0] + '.out'


# Unique configuration object that should be used everywhere
CFG = Config()


def write_a_result(energy_mark: float, performance_mark: float,
                   mg: float, penal: float, r_load: float, pv_power: float,
                   soc_bess: float, overload: bool, current_power: float,
                   data_msg: DataMessage) \
                   -> None:
    """Writes a single result record in results dump."""
    with open(CFG.results_dump, 'rb') as f:
        if os.path.getsize(CFG.results_dump) == 0:
            current = []
        else:
            current = pickle.load(f)

    with open(CFG.results_dump, 'wb') as f:
        current_mark = energy_mark + performance_mark + penal
        last = current[-1]['overall'] if current else 0
        last_energy = current[-1]['overall_energy'] if current else 0
        last_penalty = current[-1]['overall_penalty'] if current else 0
        last_performance = current[-1]['overall_performance'] if current else 0
        new = {'overall': last + current_mark,
               'overall_energy': last_energy + energy_mark,
               'overall_penalty': last_penalty + penal,
               'overall_performance': last_performance + performance_mark,
               'energyMark': energy_mark,
               'performance': performance_mark,
               'real_load': r_load,
               'pv_power': pv_power,
               'bessSOC': soc_bess,
               'bessOverload': overload,
               'bessPower': current_power,
               'mainGridPower': mg,
               'penal': penal,
               'DataMessage': data_msg.__dict__}
        current.append(new)
        pickle.dump(current, f)
        global LATEST_RESULT
        LATEST_RESULT = new


def read_results() -> Optional[List[Any]]:
    """Load results python object from dump file. If file is still open
    wait for 10 milliseconds

    """
    while True:
        try:
            with open(CFG.results_dump, 'rb+') as f:
                content = pickle.load(f)

            return content
        except:
            time.sleep(0.01)


def get_latest_result() -> Any:
    """Returns latest result that is written to output file."""
    global LATEST_RESULT
    return LATEST_RESULT


def config_outs(args: List[str], log_name: str) -> None:
    """If run is called with command line args then log outputs to files.

    """
    if len(args) > 1:
        sys.stdout = open(os.path.join(TYPHOON_DIR, '{}.log'
                                       .format(log_name)), 'w')
        sys.stderr = open(os.path.join(TYPHOON_DIR, '{}_err.log'
                                       .format(log_name)), 'w')
