from concurrent.futures import ThreadPoolExecutor
from numba import jit
import threading
from fastapi import FastAPI, HTTPException
import uvicorn
import asyncio



class PrimeFinder(threading.Thread):
    def __init__(self, n):
        super().__init__()
        self.result = None
        self.n = n

    def run(self):
        self.result = self.nth_prime(self.n)

    @staticmethod
    @jit(nopython=True, nogil=True)
    def nth_prime(n):
        def is_prime(number):
            if number <= 1:
                return False
            for i in range(2, number - 1):
                if number % i == 0:
                    return False
            return True

        count = 0
        num = 1
        while count < n:
            num += 1
            if is_prime(num):
                count += 1
        return num



app = FastAPI()
active_conn = 0
load_value = 0
thread_pool = ThreadPoolExecutor(max_workers=4)

async def run_prime_finder(n):
    prime_finder = PrimeFinder(n)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(thread_pool, prime_finder.run)
    return prime_finder.result

@app.get("/nth_prime")
async def get_nth_prime(n: int):
    if n <= 0:
        raise HTTPException(status_code=400, detail="Invalid input")
    try:
        global active_conn
        global load_value
        load_value += n
        active_conn += 1
        prime_number = await run_prime_finder(n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        load_value -= n
        active_conn -= 1
    return {"nth_prime": prime_number}

@app.get("/stats")
async def get_active_conn():
    global active_conn
    global load_value
    return {"active_conn": active_conn, "load_value": load_value}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

