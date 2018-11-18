"""This module represents Typhoon HIL framework that is used for
testing and rating of solutions.

"""
from multiprocessing import Process

import json
from hackathon.utils.utils import *
from hackathon.energy.rating import get_physics_metrics

from hackathon.framework.http_server import run as http_server_run
from hackathon.framework.http_server import prepare_dot_dir
import generate_profiles as gp

__author__ = "Novak Boskov"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"


def rater(socket: zmq.Socket, poller: zmq.Poller, data_msg: DataMessage) \
    -> None:
    """Calculate time spent by the solution in current cycle and physics
    mark for data_msg (if returned). Calculated data is being written
    in results file.

    """
    start = time.time()
    # poller.poll blocks until message is sent or for passed
    # milliseconds if message is not sent
    msgs = dict(poller.poll(
        None if CFG.DBGPhysics else CFG.max_results_wait * 1000))
    spent = time.time() - start

    if socket in msgs and msgs[socket] == zmq.POLLIN:
        solution_response = socket.recv_pyobj().validate()

        match = True
        if solution_response.data_msg.id != data_msg.id:
            match = False
            spent = CFG.max_results_wait

        if CFG.DBG:
            print('DBG: {} {} received after {}s.'
                  .format('ADEQUATE' if match else 'INADEQUATE',
                          solution_response, spent))

        write_a_result(
            *get_physics_metrics(data_msg, solution_response, spent, match),
            data_msg)
    elif CFG.DBG:
        print('DBG: results are not sent in predefined interval of {}s.'
              .format(CFG.max_results_wait))


def run(args) -> None:
    prepare_dot_dir()
    gp.generate_profiles()
    config_outs(args, 'framework')

    data_emit_socket, _ = bind_pub_socket(CFG.in_address, CFG.in_port)
    result_gather_socket, _ = bind_sub_socket(CFG.out_address, CFG.out_port)
    results_poll = zmq.Poller()
    results_poll.register(result_gather_socket, zmq.POLLIN)

    # Run http server in separate process
    http = Process(target=http_server_run, args=())
    http.start()

    # Create results file, truncate if exists
    with open(CFG.results, 'w'):
        pass

    # Create results dump file, truncate if exists
    with open(CFG.results_dump, 'w'):
        pass

    # Open profile file
    with open(CFG.profile_file, 'r') as f:
        profile = json.load(f)

    print('Profile file from {} has loaded...'.format(CFG.profile_file))

    print('Loading physics initialization file')
    with open(CFG.physics_init, 'r') as f:
        ini = json.load(f)

    lapse_time = CFG.framework_lapse_time or 1
    print('Framework is booting with the lapse time of {}s ...'
          .format(lapse_time))
    time.sleep(lapse_time)

    for i, rec in enumerate(profile):
        if i == 0:
            soc_bess, overload, mg, current_power = ini['bessSOC'],      \
                                                ini['bessOverload'], \
                                                ini['mainGridPower'], \
                                                ini['bessPower']
        else:
            last = get_latest_result()
            soc_bess, overload, mg, current_power = last['bessSOC'],      \
                                                last['bessOverload'], \
                                                last['mainGridPower'], \
                                                last['bessPower']

        data = DataMessage(i,
                           rec['gridStatus'], rec['buyingPrice'],
                           rec['sellingPrice'], rec['currentLoad'],
                           rec['solarProduction'],
                           soc_bess, overload, mg, current_power)

        if CFG.DBG:
            print('Framework emits {}'.format(data))

        data_emit_socket.send_pyobj(data)
        rater(result_gather_socket, results_poll, data)

    # Send terminating message to the solution
    data_emit_socket.send_pyobj(False)

    # Write results json from dump
    with open(CFG.results, 'w') as f:
        json.dump(read_results(), f)

    if CFG.shutdown_http_server:
        # Gracefully terminate HTTP server process that serves results
        # to visualization web page
        time.sleep(2)
        http.terminate()
        print('Simple HTTP server has stopped.')
    else:
        print('Simple HTTP server is still running...')
