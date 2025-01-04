from numba import jit
import threading
from fastapi import FastAPI, HTTPException

load_value = 0

class prime_finder(threading.Thread):
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

@app.get("/nth_prime")
async def get_nth_prime(n: int):
    global load_value
    if n <= 0:
        raise HTTPException(status_code=400, detail="Invalid input")
    try:
        load_value += n
        prime_finder_thread = prime_finder(n)
        prime_finder_thread.start()
        prime_finder_thread.join()
        prime_number = prime_finder_thread.result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        load_value -= n
    return {"nth_prime": prime_number}

@app.get("/load_value")
async def get_load_value():
    global load_value
    return {"load_value": load_value}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

