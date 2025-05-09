import subprocess
from constants import WebServer, ServerSetupParams
import time
import os
import socket
import atexit
from logging_config import configure_logger
import threading

_logger = configure_logger(__name__)

class ApiServer:

    def __init__(self):
        self._start_server()

    def _start_server(self):
        """
        Start the api server.
        """
        ## Setup the command to start the api engine
        cmd = ["python", "-m", "engine.api_engine", WebServer.HOST, f"{WebServer.PORT}"]

        ## Start the subprocess
        _logger.info(f"starting subprocess: {cmd}")
        process = subprocess.Popen(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT,
                                   text=True)
        
        # Function to stream subprocess output to the parent process's console
        def stream_output(pipe):
            for line in iter(pipe.readline, ""):
                _logger.info(line.rstrip())
            pipe.close()

        # Start threads to capture stdout and stderr
        threading.Thread(target=stream_output, args=(process.stdout,), daemon=True).start()

        ## Clean up processes on script exit. 
        ## Use atexit, for signal handling to terminate subprocesses when main script exits.
        ## Ensure it's terminated on exit.
        atexit.register(lambda: process.terminate())
     
        ## Preferrably: Wait briefly to check if process starts correctly
        time.sleep(2)        
        if process.poll() is not None:
            _logger.info("Failed to start FastAPI app.")
        else:
            _logger.info("FastAPI app started successfully.")

        ## Wait until the server is healthy via port checks on socket
        self._wait_until_server_healthy(host=WebServer.HOST, port=WebServer.PORT)
    

    def _wait_until_server_healthy(self, host: str, port: int, timeout: float = 1.0):
        """Wait until the server is healthy."""
        start_time = time.time()
        while time.time() - start_time < ServerSetupParams.WAIT_TIME_MIN * 60:
            is_healthy = self._is_port_open(host, port, timeout)
            if is_healthy:
                if os.environ.get("LOGGING_WORKER_ID", "") == str(os.getpid()):
                    _logger.info("Server is healthy.")
                return
            if os.environ.get("LOGGING_WORKER_ID", "") == str(os.getpid()):
                _logger.info("Waiting for server to start...")
            time.sleep(30)
        raise Exception(f"Server did not become healthy within 15 minutes.")

    # Helper function to check if a port is open
    def _is_port_open(self, host: str = "localhost", port: int = 8000, timeout: float = 1.0) -> bool:
        """Check if a port is open on the given host."""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                _logger.info(f"host:{host}, port:{port} - socket connected")
                return True
        except (ConnectionRefusedError, TimeoutError, OSError):
            _logger.error(f"host:{host}, port:{port} - socket connction error")
            return False