import aiohttp
import requests
from fastapi import FastAPI, HTTPException
import uvicorn
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import time

from collections import deque

last_sequence = [deque([0,0,0,0,0,0], maxlen=7) for _ in range(3)]
model = load_model("/home/fuxuras/school/gp/trad_lb/lstm_model.keras")
servers = ["localhost:8001", "localhost:8002", "localhost:8003"]
app = FastAPI()
scale = 1.39610



def get_best_server(n):
    best_value = 10000
    best_server = -1
    input_array = np.zeros((1, 7, 1))

    for i in range(3):
        last_sequence[i].append(n * scale)
        input_array[0, :, 0] = last_sequence[i]
        value = model.predict(input_array, verbose=0)[0][0]
        if value < best_value:
            best_value = value
            best_server = i

    for i in range(3):
        if i != best_server:
            last_sequence[i].pop()

    return servers[best_server]


@app.get("/test")
async def test(n:int):
    return get_best_server(n)

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
    uvicorn.run(app, port=8081)