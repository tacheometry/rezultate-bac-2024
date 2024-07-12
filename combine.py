from os import path, makedirs
from subprocess import Popen
import json
from time import sleep, time

makedirs(path.join("data", "batch"), exist_ok=True)


BATCH_SIZE = 20
MAX_PROCESSES = 10

log_file = open(path.join("data", "log.txt"), "w+")
Popen(["python3", "scraper.py", f"{BATCH_SIZE}", "1", "0"], stdout=log_file).wait()
f = open(path.join("data", "bac_2024_page_metadata.json"))
metadata = json.load(f)
last_page = int(metadata["selection"][-1])


processes = []
queue = []
failures = 0

for i in range(BATCH_SIZE, last_page + 1, BATCH_SIZE):
    if path.exists(path.join("data", "batch", f"bac_2024_batch_{i}.json")):
        print(f"[{i}] already exists")
    else:
        queue.append(f"{i}")

last_loop = time()
last_idx = "1"
try:
    while len(queue) > 0:
        sleep(0.1)

        status_bar = "\r\t\tProcesses: [ "
        for process in processes:
            status_bar += process["idx"] + " "
        status_bar += (
            f"] | {len(queue)} in queue | {failures} failures | Last batch: {last_idx}"
        )

        print("", end="\r")
        print(status_bar, end="")

        now = time()
        if now - last_loop >= 3:
            last_loop = now

            alive_processes = []
            for process in processes:
                code = process["handle"].poll()
                idx = process["idx"]
                if code is None:
                    alive_processes.append(process)
                else:
                    print(f"[{idx}] Finished with code {code}", file=log_file)
                    if code == 0:
                        last_idx = idx
                    else:
                        failures += 1
                        print(f"[{idx}] Adding to the end of the queue", file=log_file)
                        queue.append(idx)
            processes = alive_processes
            if len(processes) >= MAX_PROCESSES:
                continue

            idx = queue.pop(0)
            print(f"[{idx}] Starting process", file=log_file)
            p = Popen(
                ["python3", "scraper.py", f"{BATCH_SIZE}", idx, f"{last_page - 1}"],
                stdout=log_file,
            )
            processes.append({"handle": p, "idx": idx})

except KeyboardInterrupt:
    for process in processes:
        process["handle"].wait()
    exit()

for process in processes:
    process["handle"].wait()

print("Combining results...")

full_list = []


def add_file(i):
    print(f"Reading {i}")
    global full_list
    batch_path = path.join("data", "batch", f"bac_2024_batch_{i}.json")
    if path.exists(batch_path):
        with open(batch_path, "r") as f:
            for value in json.load(f).values():
                full_list += value
    else:
        print(f"Could not find {batch_path}")


add_file(1)
for i in range(0, last_page + 1, BATCH_SIZE):
    if i == 0:
        continue
    add_file(i)

with open(path.join("data", "bac_2024_full.json"), "w") as f:
    json.dump(full_list, f)
