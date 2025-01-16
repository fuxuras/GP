import aiohttp
import requests
from fastapi import FastAPI, HTTPException
import uvicorn

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.index = 0

    def round_robin(self):
        server = self.servers[self.index]
        self.index = (self.index + 1) % len(self.servers)
        return server


app = FastAPI()
lb = LoadBalancer(["localhost:8001", "localhost:8002", "localhost:8003"])


@app.get("/nth_prime")
async def nth_prime(n: int):
    if n <= 0:
        raise HTTPException(status_code=400, detail="Invalid input")

    server = lb.round_robin()
    url = f"http://{server}/nth_prime?n={n}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=response.text)
            result = await response.json()

    return result


if __name__ == "__main__":
    uvicorn.run(app, port=8080)