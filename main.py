from google.cloud.firestore_v1 import GeoPoint
from google.cloud.firestore_v1.document import DocumentReference
from pymongo import GEOSPHERE

import firebase
import cachedb

from bson import string_type
from bson.codec_options import TypeCodec, TypeRegistry, CodecOptions

"""
https://pymongo.readthedocs.io/en/stable/examples/custom_type.html

"""
class FBRefCodec(TypeCodec):
    python_type = DocumentReference
    bson_type = dict

    def transform_python(self, value: DocumentReference):
        return {"ref": str(value.path)}

    def transform_bson(self, value):
        return firebase.get_db().reference(value)


class FBGeoPointCodec(TypeCodec):
    python_type = GeoPoint
    bson_type = dict

    def transform_python(self, value: GeoPoint):
        return {"type": "Point",
                "coordinates": [value.longitude, value.latitude]}

    def transform_bson(self, value):
        return firebase.get_db().reference(value)


type_registry = TypeRegistry([FBRefCodec(), FBGeoPointCodec()])
codec_options = CodecOptions(type_registry=type_registry)

def sync_activities():

    fb = firebase.get_db()
    mdb = cachedb.get_db().get_collection("activities", codec_options=codec_options)

    docs = fb.collection(u'activities').stream()

    mdb.drop()

    mdb.create_index([("location", GEOSPHERE)])
    # https://docs.mongodb.com/manual/tutorial/geospatial-tutorial/
    # db.activities.find({ location:    { $geoWithin:       { $centerSphere: [ [ 153.2993414657, -28.25302903 ], 50 / 3963.2 ] } } })

    inserts = []
    for doc in docs:
        rec = doc.to_dict()
        rec["_id"] = doc.id

        inserts.append(rec)
    mdb.insert_many(inserts)

def sync_table(name: str):

    fb = firebase.get_db()
    docs = fb.collection(name).stream()

    mdb = cachedb.get_db()
    mdbref = mdb.get_collection(name, codec_options=codec_options)
    mdbref.drop()

    inserts = []
    for doc in docs:
        rec = doc.to_dict()
        rec["_id"] = doc.id
        inserts.append(rec)

    mdbref.insert_many(inserts)

def sync_all():
    sync_activities()
    sync_table("users")
    sync_table("wanderlists")

sync_all()
