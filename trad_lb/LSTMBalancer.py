import aiohttp
import requests
from fastapi import FastAPI, HTTPException
import uvicorn
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import time
import threading

from collections import deque

last_sequence = [deque([0,0,0,0,0,0], maxlen=7) for _ in range(3)]
model = load_model("/home/fuxuras/school/gp/trad_lb/lstm_model.keras")
servers = ["localhost:8001", "localhost:8002", "localhost:8003"]
app = FastAPI()
scale = 1.39610
scaler = MinMaxScaler(feature_range=(0, 1))

predicts = [0, 0, 0]

def update_predicts():
    while True:
        input_array = np.zeros((1, 7, 1))
        for i in range(3):
            input_array[0, :, 0] = last_sequence[i]
            predicts[i] = model.predict(input_array, verbose=0)[0][0]
        time.sleep(0.2)

def get_best_server(n):
    best_server_index = np.argmin(predicts)
    last_sequence[best_server_index].append(custom_minmax_scale(n))
    return servers[best_server_index]


def custom_minmax_scale(x, data_min=0.0, data_max=716276.0, min_=0.0, scale_=1.3961098794319508e-06):
    return (x - data_min) * scale_ + min_

@app.get("/nth_prime")
async def nth_prime(n: int):
    if n <= 0:
        raise HTTPException(status_code=400, detail="Invalid input")

    server = get_best_server(n)
    url = f"http://{server}/nth_prime?n={n}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=response.text)
            result = await response.json()

    return result


if __name__ == "__main__":
    thread = threading.Thread(target=update_predicts)
    thread.daemon = True
    thread.start()
    uvicorn.run(app, port=8081)