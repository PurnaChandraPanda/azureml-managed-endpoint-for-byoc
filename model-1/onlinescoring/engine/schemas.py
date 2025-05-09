from typing import List
from pydantic import BaseModel

class ScoreRequest(BaseModel):
    data: str
    out1: str
    out2: str

class ScoreResponse(BaseModel):
    prediction: str

class PredictRequest(BaseModel):
    data: List[List[int]]

class PredictResponse(BaseModel):
    result: str

