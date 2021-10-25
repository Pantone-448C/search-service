#    sync_activities()
import cachedb
import waitress
import apiserver
import scheduled
from multiprocessing import Queue
import multiprocessing as mp
import signal
import os

job_server = None


def stop_scheduled():
    job_server.join()
    job_server.close()


if __name__ == "__main__":
    ctx = mp.get_context('spawn')

    job_server = ctx.Process(target=scheduled.run)
    job_server.start()

    print("Serving on 0.0.0.0:8080")
    waitress.serve(apiserver.app, host='0.0.0.0', port=8080)
    os.kill(job_server.pid, signal.SIGINT)
