"""This module facilitates communication with the framework component."""

from typing import Optional, Generator
from hackathon.utils.utils import *

__author__ = "Novak Boskov"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"

class Control:
    """Abstraction that represents connection between framework and
    solution.

    """
    def __init__(self,
                 in_port: Optional[int]=None, in_addr: Optional[str]=None,
                 out_port: Optional[int]=None, out_addr: Optional[str]=None) \
                 -> None:
        """Communication sockets can be given by address and port, if not
        configuration file is used.

        """
        self.in_socket, self.in_context = bind_sub_socket(
            in_addr or CFG.in_address,
            in_port or CFG.in_port)
        self.out_socket, self.out_context = bind_pub_socket(
            out_addr or CFG.out_address,
            out_port or CFG.out_port)

    def get_data(self) -> Generator[DataMessage, None, None]:
        """Get data from the framework.

        Generator containing data is being returned.

        """
        while True:
            msg = self.in_socket.recv_pyobj()
            if msg:
                yield msg
            else:
                return

    def push_results(self, obj: ResultsMessage) -> None:
        """Send message that contains results calculated by the solution back
        to the framework.

        """
        self.out_socket.send_pyobj(obj)
