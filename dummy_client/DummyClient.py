import numpy as np
import requests
import asyncio
import aiohttp
import random
import time

class DummyClient:
    def __init__(self):
        self.sequence = []
        self.seed = 0

    def generate_numbers(self):
        number_of_elements = int(input("Enter number of elements: "))
        range_of_elements = int(input("Enter range of elements: "))

        np.random.seed(self.seed)

        scale = range_of_elements / 10
        shape = 2

        raw_numbers = np.random.pareto(shape, number_of_elements) * scale

        self.sequence = np.clip(np.round(raw_numbers).astype(int), 1, range_of_elements)

        print("Sequence created.")
        print(self.sequence)

    def set_seed(self):
        self.seed = int(input("Enter seed: "))


    async def send_sequence(self):
        async with aiohttp.ClientSession() as session:
            i = 0
            tasks = []
            while i < len(self.sequence):
                num_requests = random.randint(20, 100)
                for offset in range(num_requests):
                    if i + offset < len(self.sequence):
                        task = asyncio.create_task(self.send_request(session, self.sequence[i + offset]))
                        tasks.append(task)
                wait_time = random.uniform(0, 20)
                print(f"Waiting for {wait_time:.2f} seconds before sending next batch of requests...")
                i += num_requests
                await asyncio.sleep(wait_time)

    async def send_request(self,session, i):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                async with session.get(f'http://localhost:8080/nth_prime?n={i}') as response:
                    print(await response.text())
                    return
            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    backoff_time = random.uniform(1, 3)
                    print(f"Request failed ({e}), retrying in {backoff_time:.2f} seconds...")
                    await asyncio.sleep(backoff_time)
                else:
                    print(f"Request failed after {max_retries} attempts.")

    def print_sequence(self):
        for i in range(10):
            print(self.sequence[i])


if __name__ == '__main__':
    is_running = True
    dummy_client = DummyClient()
    while is_running:
        print("Select Number")
        print("1. Create Sequence")
        print("2. Send Sequence")
        print("3. Set seed")
        print("4. Print Sequence")
        print("5. Exit")

        choice = input("Enter choice: ")
        if choice == '1':
            dummy_client.generate_numbers()
        elif choice == '2':
            asyncio.run(dummy_client.send_sequence())
        elif choice == '3':
            dummy_client.set_seed()
        elif choice == '4':
            dummy_client.print_sequence()
        elif choice == '5':
            is_running = False
        else:
            print("Invalid Choice")