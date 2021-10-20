import os
import time

import multiprocessing as mp

import cachedb

TIMEOUT_SECS = 200


def update_wanderlist_thumbs():
    c = cachedb.get_db()['wanderlist']
    lists = c.get_collection("wanderlists").find({"icon": "", '$where': "this.activities.length>0"})

    for list in lists:
        if "activities" in list.keys():
            if len(list['activities']) > 0:
                activityid = list['activities'][0]['ref'].split("/")[1]
                activity = c.get_collection('activities').find_one({"_id": activityid})
                if "image_url" in activity.keys():
                    if len(activity['image_url']) > 2:
                        #list['icon'] = activity['image_url']
                        c.get_collection('wanderlists').update(
                            {"_id": list['_id']}, {'icon': activity['image_url']})

def run():
    print("Started scheduled jobs")
    while True:
        try:
            while True:
                # do periodic jobs
                update_wanderlist_thumbs()
                time.sleep(1000)
        except KeyboardInterrupt:
            return


