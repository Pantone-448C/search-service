from pymongo.cursor import Cursor

from models import *
import geopy.distance

from util import km_to_radian, cursor_to_json

MAX_REC_DIST = 100.0


def activityweighting(a: Activity):
    weighting = {
        "tags": {},
        "locations": [a.locationLatLng()]
    }
    for tag in a.tags():
        weighting["tags"][tag] = 1

    return weighting


def wanderlist_location(wanderlist: Wanderlist):
    return [a.locationLatLng() for a in wanderlist.activities()]


def wanderlistweighting(l: Wanderlist):
    weighting = {
        "tags": {},
        "locations": [],
    }

    for a in l.activities():
        weighting["locations"].append(a.locationLatLng())
        for tag in a.tags():
            if tag in weighting["tags"]:
                weighting["tags"][tag] += 1
            else:
                weighting["tags"][tag] = 1
    return weighting


def compare_activity(wanderlist: Wanderlist, activity: Activity):
    score = 0.0
    wlweighting = wanderlistweighting(wanderlist)

    for a in wanderlist.activities():
        dist = geopy.distance.distance(
            a.locationLatLng(), activity.locationLatLng()).km
        dist = (MAX_REC_DIST - dist) / MAX_REC_DIST

        totaltags = len(activity.tags()) + len(wlweighting["tags"])
        tagscore = 0.0

        for t in activity.tags():
            if t in wlweighting["tags"].keys():
                tagscore += wlweighting["tags"][t]
        tagscore /= totaltags

        score += tagscore * dist

    if len(activity.tags()) > 0:
        score /= len(activity.tags())
    if len(wanderlist.activities()) > 0:
        score /= len(wanderlist.activities())

    return score


def activities_near(mongo, lat, lon, rng):
    resp: Cursor = mongo.db.activities.find(
        {"location": {"$geoWithin":
                      {"$centerSphere": [[lon, lat], rng]}}})
    return [Activity(a) for a in cursor_to_json(resp)["results"]]


def recommend_activities(wanderlist: Wanderlist, mongo):
    locs = wanderlist_location(wanderlist)

    activities = {}
    existing_activities = [a.id() for a in wanderlist.activities()]
    for loc in locs:
        lat, lon = loc
        rng = km_to_radian(MAX_REC_DIST)
        for a in activities_near(mongo, lat, lon, rng):
            if a.id() in activities.keys() or a.id() in existing_activities:
                continue

            doc = a.json()
            doc["similarity_score"] = compare_activity(wanderlist, a)
            activities[a.id()] = doc

    # sort on the activity weighting for this list

    return [a[1] for a in sorted(activities.items(), key=lambda x: x[1]["similarity_score"], reverse=True)]
