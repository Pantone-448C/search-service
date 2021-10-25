import json
import time
import cachedb
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import firebase
from util import *
from constant_responses import *
from systems import *

app = Flask(__name__)
app.config["MONGO_URI"] = cachedb.CONNECTION_STRING
mongo = PyMongo(app)

ENFORCE_AUTH = True


def get_request_user():
    if (ENFORCE_AUTH):
        user = mongo.db.users.find_one({"_id": request.user['uid']})
    else:
        user = mongo.db.users.find_one({"_id": "XnlSRZqHepPM3HCDY2NV4BETTJC3"})

    return user


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(500)
def resource_not_found(e):
    return jsonify(error=str(e)), 500


@app.before_request
def enforce_auth():
    if not ENFORCE_AUTH:
        return
    if not request.headers.get('authorization'):
        return NO_AUTH
    else:
        try:
            user = firebase.verify_token(request.headers["authorization"])
            request.user = user
        except Exception as e:
            print(e)
            return {"error": "Invalid token"}, 400


@app.route('/activity/search', methods=["GET"])
def activitysearch():
    query: str = request.args.get("query")

    resp: Cursor = mongo.db.activities.find({"$text": {"$search": query}})
    if resp:
        return cursor_to_json(resp)
    return BAD_REQUEST


@app.route('/activities', methods=["GET"])
def activity():
    if "lat" in request.args.keys() or "lon" in request.args.keys():
        return activitynear()
    if "query" in request.args.keys():
        return activitysearch()
    if "activities" in request.args.keys():
        return activitylist()
    if "wanderlist" in request.args.keys():
        return activitywanderlist()
    if "rec" in request.args.keys():
        return activitiesrecforuser()

    return {"error": "Provide search argument lat,lon or query, list of activties, wanderlistid or 'rec'"}, 400


def activitywanderlist():
    """
    recommend a list of activities based on an existing wanderlist.
    """
    id = request.args["wanderlist"]
    res = mongo.db.wanderlists.find_one({"_id": id})
    if res is None:
        return NOT_FOUND
    wanderlist = Wanderlist(clean_document(cachedb.fill_all_refs(mongo, res)))

    acts = {"results": recommend_activities(wanderlist, mongo)}

    if (len(acts['results']) == 0):
        return activitiesrecforuser()
    return jsonify(acts)


def activitiesrecforuser():
    """
    recommend a list of activities based on an existing wanderlist.
    """

    userlists = clean_document(mongo.db.users.find_one(
        {"_id": request.user['uid']}))["wanderlists"]


    if (userlists is None or len(userlists) == 0):
        return cursor_to_json(mongo.db.activities.find().limit(50))

    wanderlist = Wanderlist(cachedb.fill_all_refs(
        mongo, userlists[0]["wanderlist"]))

    wanderlist._json["id"] = "invalid"

    for l in userlists:
        activities = cachedb.fill_all_refs(mongo, l['wanderlist'])['activities']
        wl = Wanderlist(cachedb.fill_all_refs(mongo, l["wanderlist"])) 
        wanderlist._json["activities"] += wl._json["activities"]


    acts = {"results": recommend_activities(wanderlist, mongo)}
    return jsonify(acts)


def activitylist():
    activities = []
    for id in json.loads(request.args["activities"]):
        res = mongo.db.activities.find_one({"_id": id})
        if res is None:
            return BAD_COLLECTION
        activities.append(clean_document(res))

    return jsonify(activities)


@app.route('/activity/near', methods=["GET"])
def activitynear():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    range = request.args.get("range")

    if lat is None or lon is None:
        return NEAR_ARGS

    if range is None:
        range = km_to_radian(50.0)
    else:
        range = km_to_radian(float(range))

    lat = float(lat)
    lon = float(lon)

    resp: Cursor = mongo.db.activities.find(
        {"location": {"$geoWithin":
                      {"$centerSphere": [[lon, lat], range]}}})

    return cursor_to_json(resp)


@app.route('/', methods=["GET"])
def index():
    return {"routes": {
        "/activity/search": {"params": {"query": "search query string"}},
        "/activity/near": {"params": {
            "lat": "Latitude (float, degrees)",
            "lon": "Longitude (float, degrees)",
            "range": "(optional) the search radius in km"
        }},
    }}, 400


@app.route('/<string:collection>/<string:id>', methods=["GET", "POST"])
def genericcrud(collection, id):
    routes = ["activities", "wanderlists", "rewards"]
    if not ENFORCE_AUTH:
        routes.append("users")

    if collection not in routes:
        return BAD_COLLECTION
    if request.method == "GET":
        res = mongo.db[collection].find_one({"_id": id})
        if res is not None:
            return cachedb.fill_all_refs(mongo, res)

    if request.method == "POST":
        content = request.get_json()
        return NOT_PERMITTED

        if content is None:
            return {"error": "No document"}, 400

        content["_id"] = id
        content["_updated"] = time.time()
        res = mongo.db[collection].update_one({"_id": id}, {'$set': content})
        if (res is None):
            return {"error:", "Document doesnt exist, use create method instead"}, 400

    return {}


@app.route('/<string:collection>', methods=["POST"])
def genericcreate(collection):
    routes = ["activities", "wanderlists", "rewards"]
    if not ENFORCE_AUTH:
        routes.append("users")
    if collection not in routes:
        return BAD_COLLECTION

    content = request.get_json()

    if content is None:
        return {"error": "No document"}, 400

    content["id"] = new_docid()
    content["_id"] = content["id"]
    content["_updated"] = time.time()
    res = mongo.db[collection].insert_one(content)

    return jsonify(content)


@app.route('/user', methods=["GET", "POST"])
def getuser():
    if request.method == "GET":
        res = get_request_user()

        if res is None:
            doc = firebase.get_db().collection(
                u'users').document(request.user['uid'])
            if doc.get().to_dict() is None:
                return NOT_FOUND

            print("Account not  found, falling back to firebase")
            res = doc.get().to_dict()
            res["_id"] = doc.id
            res["_updated"] = time.time()
            mdbref = mongo.db.get_collection(
                "users", codec_options=cachedb.codec_options)
            mdbref.replace_one({"_id": doc.id}, res, upsert=True)

        val = cachedb.fill_all_refs(mongo, res)
        return val
    if request.method == "POST":
        content = request.get_json()

        if content is None:
            return {"error": "No document"}, 400

        content["_id"] = request.user["uid"]
        content["_updated"] = time.time()
        res = mongo.db.users.update(
            {'_id': request.user["uid"]}, content, True)
        return {}


@app.route('/user/rewards/totalpoints', methods=["GET"])
def rewardsteps():
    return jsonify(1000)


@app.route('/user/rewards/next', methods=["GET"])
def recommend_reward():
    user = get_request_user()
    if "rewards" not in user:
        return clean_document(mongo.db.rewards.find_one())

    users_rewards = [r["reward"]["ref"].split("/")[1] for r in user["rewards"]]
    cursor = mongo.db.rewards.find({"_id": {"$not": {"$in": users_rewards}}})
    available_rewards = [r for r in cursor]
    if len(available_rewards) == 0:
        return NO_REWARDS
    # choose the best one
    return jsonify(clean_document(available_rewards[0]))


if __name__ == "__main__":
    app.run()
