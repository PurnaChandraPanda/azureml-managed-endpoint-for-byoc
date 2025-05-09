import os
import subprocess
from api_server import ApiServer
from logging_config import configure_logger

## Setup the logger
_logger = configure_logger(__name__)

def init():
    """
    This function is called when the container is initialized/started, typically after create/update of the deployment.
    You can write the logic here to perform init operations like caching the model in memory
    """
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # Please provide your model's folder name if there is one
    model_path = os.path.join(
        os.getenv("AZUREML_MODEL_DIR"), "model/sklearn_regression_model.pkl"
    )

    ## Set env variable for the model path
    ## Let it be leveraged in web server end
    os.environ["AZUREML_MODEL_PATH"] = model_path

    _logger.info("model path: %s", model_path)

    ## Start the api web server
    ApiServer()
    
    ## Print ports listening
    _logger.info("ports in active mode: ")
    result = subprocess.run(['netstat', '-tulnp'], stdout=subprocess.PIPE)
    _logger.info(result.stdout.decode('utf-8'))
    
    _logger.info("Init complete")


## This function would not be called in the current setup, as the api web server is started in a separate thread and process.
def run(raw_data):
    pass
