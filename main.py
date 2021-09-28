
from google.cloud.firestore_v1 import GeoPoint
from google.cloud.firestore_v1.document import DocumentReference
from pymongo import GEOSPHERE, WriteConcern, MongoClient, ReadPreference, TEXT
from pymongo.errors import CollectionInvalid
from pymongo.read_concern import ReadConcern

import firebase
import time
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

def sync_table(session, name: str):
    fb = firebase.get_db()
    docs = fb.collection(name).stream()

    mdb = session.client["wanderlist"]
    mdbref = mdb.get_collection(name, codec_options=codec_options)

    update_stamp = time.time()

    for doc in docs:
        rec = doc.to_dict()
        rec["_id"] = doc.id
        rec["_updated"] = update_stamp
        mdbref.replace_one({"_id": doc.id}, rec, upsert=True, session=session)

    res = mdbref.delete_many({"_updated": {"$lt": update_stamp}}, session=session)


def sync_callback(session):
    sync_table(session, "users")
    sync_table(session, "wanderlists")
    sync_table(session, "activities")

def init():
    client = MongoClient(cachedb.CONNECTION_STRING)
    try:
        client.wanderlist.create_collection("users")
    except CollectionInvalid as e:
        print(e)
        pass
    try:
        client.wanderlist.create_collection("activities")
        client.wanderlist.activities.create_index([("location", GEOSPHERE)])
        client.wanderlist.activities.create_index([("name", TEXT)])
        # https://docs.mongodb.com/manual/tutorial/geospatial-tutorial/
        # db.activities.find({ location:    { $geoWithin:       { $centerSphere: [ [ 153.2993414657, -28.25302903 ], 50 / 3963.2 ] } } })
    except CollectionInvalid as e:
        print(e)
        pass
    try:
        client.wanderlist.create_collection("wanderlists")
        client.wanderlist.wanderlists.create_index([("name", TEXT)])
    except CollectionInvalid as e:
        print(e)
        pass

def sync_all():
    wc_majority = WriteConcern("majority", wtimeout=1000)
    client = MongoClient(cachedb.CONNECTION_STRING)
    init()

    with client.start_session() as session:
        session.with_transaction(sync_callback,
                                 read_concern=ReadConcern('local'),
                                 write_concern=wc_majority,
                                 read_preference=ReadPreference.PRIMARY)
#    sync_activities()

if __name__ == "__main__":
    sync_all()
