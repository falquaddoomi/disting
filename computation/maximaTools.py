__author__ = 'Faisal'

import socket

def formatMatrix(in_mat):
    return "matrix(" + ",".join(str(in_mat).replace(" ","").split("\n")) + ")"

def getMatrixRank(in_mat):
    command = "rank(%s);" % formatMatrix(in_mat)

    # first, see if we have a memoized version, which will save us a lot of time...
    # if we don't, make one!
    # if command not in getMatrixRank.memoized:
    #     getMatrixRank.memohit += 1
    #     result = calculate(command)
    #     getMatrixRank.memoized[command] = int(result)
    #
    # return getMatrixRank.memoized[command]
    return int(calculate(command))

getMatrixRank.memoized = {}
getMatrixRank.memohit = 0

def calculate(calc):
    """
    Performs a Maxima calculation by attempting to connect to the local Maxima proxy,
    sending the calculation off, waiting for a response, and then returning that.

    :param calc: The calculation to send to the Maxima proxy server
    :type calc: str
    """
    HOST, PORT = "localhost", 8523

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