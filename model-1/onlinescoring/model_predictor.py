from __future__ import annotations
from typing import List
import numpy as np
from logging_config import configure_logger

## Setup the logger
_logger = configure_logger(__name__)

class ModelPredictor:
    """Singleton-style wrapper over the sklearn model."""
    _model = None

    @classmethod
    def set_model(cls, model) -> None:
        _logger.info("set_model(): model set")
        cls._model = model
        _logger.info("set_model(): model set completed")

    @classmethod
    def generate(cls, data: List[List[float]]):
        if cls._model is None:
            raise RuntimeError("ModelPredictor not initialised (call set_model first)")
        
        _logger.info("generate(): request received")

        np_data = np.array(data)
        model_result = cls._model.predict(np_data)
        
        _logger.info("generate(): request processed")

        return model_result.tolist()