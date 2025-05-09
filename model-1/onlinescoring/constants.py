class WebServer:
    HOST = "0.0.0.0" # localhost
    PORT = 8003

class ServerSetupParams:
    """Parameters for setting up the server."""
    WAIT_TIME_MIN = 15  # time to wait for the server to become healthy
    DEFAULT_WORKER_COUNT = 1