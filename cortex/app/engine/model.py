import os
import logging
import numpy as np
# Standard Keras 3.0+ imports
import keras
from keras import layers, models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_model(input_shape):
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.LSTM(50, return_sequences=True),
        layers.Dropout(0.2), 
        layers.LSTM(50, return_sequences=False),
        layers.Dropout(0.2),
        layers.Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    logger.info("Production model architecture built successfully.")
    return model

def train_model(model, X, y, epochs=20, batch_size=32):
    logger.info(f"Starting training on {len(X)} data points...")
    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
    logger.info("Training complete.")
    return model