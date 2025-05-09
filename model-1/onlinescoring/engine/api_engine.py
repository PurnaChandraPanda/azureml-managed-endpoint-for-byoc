import sys
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import joblib
from contextlib import asynccontextmanager
import time
from logging_config import configure_logger
from model_predictor import ModelPredictor
from .schemas import ScoreRequest, ScoreResponse, PredictRequest, PredictResponse

## Setup the logger
_logger = configure_logger(__name__)

@asynccontextmanager
async def _startup_lifespan(app: FastAPI):
    """This function is called when the container is initialized/started, typically after create/update of the deployment.
    You can write the logic here to perform init operations like caching the model in memory.
    Runs once in **each** Uvicorn worker process -> load the model locally
    so ModelPredictor is initialised for that process.
    """
    _logger.info("startup")

    ## Read the model path from the environment variable
    model_path = os.getenv("AZUREML_MODEL_PATH")

    ## Deserialize the model file back into a sklearn model
    model = joblib.load(model_path)

    ## Set the model in the ModelPredictor
    ModelPredictor.set_model(model)

    _logger.info("startup completed")
    
    yield
    _logger.info("optional shutdown")

## intialize fastapi app
app = FastAPI(lifespan=_startup_lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/score')
def score(request: ScoreRequest) -> ScoreResponse:
    _logger.info("score")        
    _logger.info("raw data: %s", request)

    local_resp = "your_result"
    # Your scoring logic here
    _response = ScoreResponse(prediction=local_resp)
    return _response

@app.get('/score1')
def score1():
    _logger.info("in score1")
    _logger.info("in score1 next line")
    _logger.info("in score1 next next line")
    time.sleep(30) # sleep for 30 seconds
    # Your custom GET logic here
    result = {"message": "This is a custom GET endpoint"}
    return json.dumps(result)

@app.get("/")
def health():
    """Check if server is healthy. Used by the readiness probe to check server is healthy."""
    _logger.info("health")
    return "healthy"

@app.post("/predict")
def predict(request: PredictRequest) -> PredictResponse:
    _logger.info("request received")
    _logger.info("raw data: %s", request)

    # Your prediction logic here
    model_result = ModelPredictor.generate(request.data)
    print("model_result: ", model_result)
    print("type(model_result): ", type(model_result))
    model_result = "your_prediction_result"

    _logger.info("request processed")

    response = PredictResponse(result=model_result)
    return response


def main():
    host = ""
    port = ""

    ## Check if the script is run with command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    ## Run the uvicorn server for fastapi app
    uvicorn.run(
        "__main__:app", 
        host=host, 
        port=port
    )

if __name__ == '__main__':
    main()
    
