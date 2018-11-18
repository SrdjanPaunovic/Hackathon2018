#!/usr/bin/env python
"""This module runs both contestant's solution and framework."""

import webbrowser
from multiprocessing import Process
import run_solution as solution
import run_framework as framework
from hackathon.utils.utils import CFG
from hackathon.framework.http_server import prepare_dot_dir

__author__ = "Novak Boskov"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"


if __name__ == '__main__':
    prepare_dot_dir()
    solution = Process(target=solution.run, args=('log', ))
    solution.start()
    framework = Process(target=framework.run, args=('log', ))
    framework.start()

    webbrowser.open('http://localhost:{}/viz.html'
                    .format(CFG.results_http_server_port))
