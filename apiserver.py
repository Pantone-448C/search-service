import json

from pymongo.cursor import Cursor

import cachedb
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = cachedb.CONNECTION_STRING
mongo = PyMongo(app)


def km_to_radian(x: float):
    return x / 6378.152


def m_to_radian(x: float):
    return x / 6378100.0


def cursor_to_json(c: Cursor):
    js = []
    for result in c:
        result.pop("_updated")
        result["id"] = result["_id"]
        result.pop("_id")
        js.append(result)
    return {"results": js}


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.route('/activity/search', methods=["GET"])
def activitysearch():
    query: str = request.args.get("query")
    if query is None:
        return jsonify({"error": "No query param specified"}), 400

    resp: Cursor = mongo.db.activities.find({"$text": {"$search": query}})

    return cursor_to_json(resp)


@app.route('/activity/near', methods=["GET"])
def activitynear():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    range = request.args.get("range")

    if lat is None or lon is None:
        return jsonify({"error": "lat or lon not specified"}), 400

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

if __name__ == "__main__":
    app.run()
