from os import path, makedirs
from subprocess import Popen
import json
from time import sleep

makedirs(path.join("data", "batch"), exist_ok=True)


BATCH_SIZE = 20
MAX_PROCESSES = 10

Popen(["python3", "scraper.py", f"{BATCH_SIZE}", "1", "0"]).wait()
f = open(path.join("data", "bac_2024_page_metadata.json"))
metadata = json.load(f)
last_page = int(metadata["selection"][-1])


processes = []
queue = []
failures = 0

for i in range(BATCH_SIZE, last_page + 1, BATCH_SIZE):
    if path.exists(path.join("data", "batch", f"bac_2024_batch_{i}.json")):
        print(f"{i} already exists")
    else:
        queue.append(f"{i}")

try:
    while len(queue) > 0:
        sleep(3)

        alive_processes = []
        for process in processes:
            code = p.poll()
            if code is None:
                alive_processes.append(p)
            else:
                print(f"Process finished with code {code}")
                if code != 0:
                    failures += 1
        processes = alive_processes
        if len(processes) >= MAX_PROCESSES:
            continue

        idx = queue.pop(0)
        print(
            f"Starting process for {idx} | {len(queue)} batches left in queue | {failures} failures"
        )
        p = Popen(["python3", "scraper.py", f"{BATCH_SIZE}", idx, f"{last_page - 1}"])
        processes.append(p)

except KeyboardInterrupt:
    for process in processes:
        process.wait()

for process in processes:
    process.wait()

print("Combining results...")

full_list = []


def add_file(i):
    print(f"Reading {i}")
    global full_list
    with open(path.join("data", "batch", f"bac_2024_batch_{i}.json"), "r") as f:
        for value in json.load(f).values():
            full_list += value


add_file(1)
for i in range(0, last_page + 1, BATCH_SIZE):
    if i == 0:
        continue
    add_file(i)

with open(path.join("data", "bac_2024_full.json"), "w") as f:
    json.dump(full_list, f)
