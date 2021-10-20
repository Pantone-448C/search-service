import os
import time

import multiprocessing as mp

TIMEOUT_SECS = 200



def update_wanderlist_thumbs():
    return

def run():
    print("Started scheduled jobs")
    while True:
        try:
            while True:
                # do periodic jobs
                update_wanderlist_thumbs()
                time.sleep(10)
        except KeyboardInterrupt:
            return


