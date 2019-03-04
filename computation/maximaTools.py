import random
from compgraph_web.settings import PYMAX_INSTANCES, PYMAX_STARTING_PORT

__author__ = 'Faisal'

import socket

def formatMatrix(in_mat):
    # tested to work with a relatively recent version of maxima (5.41.0)
    dim_set = ", ".join(str(z) for z in list([list(in_mat.row(x)) for x in range(in_mat.rows)]))
    return "matrix(%s)" % dim_set

def getMatrixRank(in_mat):
    command = "rank(%s);" % formatMatrix(in_mat)

    # first, see if we have a memoized version, which will save us a lot of time...
    # if we don't, make one!
    # if command not in getMatrixRank.memoized:
    #     getMatrixRank.memohit += 1
    #     result = calculate(command)
    #     getMatrixRank.memoized[command] = int(result)

    # return getMatrixRank.memoized[command]
    try:
        result = calculate(command)

        try:
            return int(result)
        except ValueError as ex:
            print "Couldn't cast result '%s' to an integer" % result
            raise ex
    except Exception as ex:
        print "Failed when executing the command '%s'" % command
        raise ex


# getMatrixRank.memoized = {}
# getMatrixRank.memohit = 0

def calculate(calc):
    """
    Performs a Maxima calculation by attempting to connect to the local Maxima proxy,
    sending the calculation off, waiting for a response, and then returning that.

    :param calc: The calculation to send to the Maxima proxy server
    :type calc: str
    """
    HOST, PORT = "localhost", PYMAX_STARTING_PORT

    # choose a random service running on some port and access that
    PORT += random.randint(0, PYMAX_INSTANCES-1)

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(str(calc) + "\n")
        # Receive data from the server and shut down
        received = sock.recv(8192)
    finally:
        sock.close()

    return received.strip()
