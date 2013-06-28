from Queue import Queue
import atexit
import random
import subprocess
import threading
import SocketServer
from compgraph_web.settings import PYMAX_STARTING_PORT

__author__ = 'Faisal'

# ===========================================================================
# === Maxima Server, handles communicating calculation tasks to the Maxima instance
# ===========================================================================

class MaximaHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        print "Accepted connection from %s" % str(self.client_address)
        self.server.ready = True

        # read off maxima preamble
        print self.rfile.readline().strip()

        # process requests forever
        while True:
            # grab a task, send it to the server, and get the response
            calc_req = self.server.request_queue.get()
            self.request.sendall(calc_req.calc)
            calc_req.result = self.rfile.readline().strip()
            self.server.request_queue.task_done()

        self.request.close()

class CalculateRequest(object):
    def __init__(self, calc):
        self.calc = calc
        self.result = None

class MaximaTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        # ensure that we can handle more than the usual number of pending requests
        self.request_queue_size = 30

        # initialize the request queue
        self.ready = False
        self.request_queue = Queue()

    def calculate(self, calc):
        if not self.ready:
            return None

        # terminate the request if it hasn't been terminated already
        # otherwise maxima will wait forever for extra input
        if not calc.endswith(";"):
            calc += ";"

        # form a calcrequest and put it on the queue for processing
        calc_req = CalculateRequest(calc)
        self.request_queue.put(calc_req)

        # wait until its done
        self.request_queue.join()

        # use the result that was populated by MaximaHandler when
        # it pulled our request off the queue and sent it to maxima,
        # then stored the response in result
        return calc_req.result

# ===========================================================================
# === Maxima Query Server, handles requests from the python side to Maxima
# ===========================================================================

class MaximaQueryHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        # grab whatever line they send us, and post it as a calculation
        incmd = self.rfile.readline().strip()
        result = self.server.query_server.calculate(incmd)
        # send the result back to the caller...
        self.wfile.write(result.strip())
        # and close the connection
        self.request.close()

class MaximaQueryTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, query_server, bind_and_activate=True):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.query_server = query_server
        self.request_queue_size = 30

# ===========================================================================
# === Maxima Proxy Server (spawns both MaximaTCPServer and MaximaQueryTCPServer)
# ===========================================================================

class MaximaProxyServer(object):
    def __init__(self, host="localhost", client_port=PYMAX_STARTING_PORT):
        self.host = host
        self.client_port = client_port

    def start(self):
        # ===========================================
        # === STEP 1. create the maxima-facing server
        # ===========================================

        # initialize the maxima-facing server
        # randport = random.randrange(7000, 8000)
        randport = 0
        self.maxima_server = MaximaTCPServer((self.host, randport), MaximaHandler)
        self.maxima_ip, self.maxima_port = self.maxima_server.server_address

        # start up the maxima server to listen for connections (just one in this case)
        self.server_thread = threading.Thread(target=self.maxima_server.serve_forever)
        self.server_thread.daemon = True # Exit the server thread when the main thread terminates
        self.server_thread.start()
        print "MAXIMA server loop running on %d in thread: %s" % (self.maxima_port, self.server_thread.name)

        # boot maxima itself and tell it to connect to self.maxima_port
        self.maxima_server.maxima_request = None
        FNULL = open('/dev/null', 'w')
        FNULLIN = open('/dev/null', 'r')
        self.maxima_process = subprocess.Popen(['/usr/bin/maxima', '--very-quiet', '-s', str(self.maxima_port)], stdout=FNULL, stderr=FNULL, stdin=FNULLIN)

        print "MAXIMA client process started on port %d" % self.maxima_port

        # ===========================================
        # === STEP 2. create the python-facing server
        # ===========================================

        # now start up the python-side TCP server, which just proxies calc requests to MAXIMA
        self.python_server = MaximaQueryTCPServer((self.host, self.client_port), MaximaQueryHandler, self.maxima_server)
        self.python_ip, self.python_port = self.python_server.server_address

        # start up the maxima server to listen for connections (just one in this case)
        self.py_server_thread = threading.Thread(target=self.python_server.serve_forever)
        self.py_server_thread.daemon = True # Exit the server thread when the main thread terminates
        self.py_server_thread.start()
        print "PyMax server loop running on %d in thread: %s" % (self.python_port, self.py_server_thread.name)

        # and make sure we terminate cleanly
        atexit.register(self.stop)

    def calculate(self, data):
        """Utility method for passing calculate requests to the maxima server w/o making a connection
        :param data: the calculation to be executed, optionally semicolon-terminated (added if not present)
        """
        return self.maxima_server.calculate(data)

    def stop(self):
        # self.maxima_server.request_queue.join()
        if hasattr(self, 'maxima_process'): self.maxima_process.terminate()
        if hasattr(self, 'maxima_server'): self.maxima_server.shutdown()
        if hasattr(self, 'python_server'): self.python_server.shutdown()