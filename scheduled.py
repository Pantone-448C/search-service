import os
import time

import multiprocessing as mp

import cachedb

TIMEOUT_SECS = 200


def update_wanderlist_thumbs_one(list_id):
    c = cachedb.get_db()['wanderlist']
    lists = c.get_collection("wanderlists").find({"_id": list_id, '$where': "this.icon.length==0"})
    make_first_activity_thumb(lists)


def update_wanderlist_thumbs():
    c = cachedb.get_db()['wanderlist']
    lists = c.get_collection("wanderlists").find({"icon": "", '$where': "this.activities.length>0"})
    make_first_activity_thumb(lists)


def make_first_activity_thumb(wanderlists: list):
    for l in wanderlists:
        if "activities" in l.keys():
            if len(l['activities']) > 0:
                activityid = l['activities'][0]['ref'].split("/")[1]
                activity = c.get_collection('activities').find_one({"_id": activityid})
                if "image_url" in activity.keys():
                    if len(activity['image_url']) > 2:
                        c.get_collection('wanderlists').update(
                            {"_id": l['_id']}, {"$set": {'icon': activity['image_url']}})

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


