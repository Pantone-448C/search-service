import json

import bson
from google.cloud.firestore_v1 import GeoPoint
from google.cloud.firestore_v1.document import DocumentReference
from pymongo import GEOSPHERE, WriteConcern, MongoClient, ReadPreference, TEXT
from pymongo.errors import CollectionInvalid
from pymongo.read_concern import ReadConcern
import firebase
import time

from bson.codec_options import TypeCodec, TypeRegistry, CodecOptions

import os

from util import clean_document

DB_NAME = "wanderlist"
CONNECTION_STRING = os.environ.get("MONGO_URI")
print(CONNECTION_STRING)
USE_TRANSACTION = False


def get_db():
    return MongoClient(CONNECTION_STRING)


class FBRefCodec(TypeCodec):
    """
    Convert a firebase document reference to

    https://pymongo.readthedocs.io/en/stable/examples/custom_type.html
    """
    python_type = DocumentReference
    bson_type = dict

    def transform_python(self, value: DocumentReference):
        return {"ref": str(value.path)}

    def transform_bson(self, value):
        return firebase.get_db().reference(value)


def user_is_admin(uid):
    return get_db().admins.find_one({"_id": uid}) is not None


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

    res = mdbref.delete_many(
        {"_updated": {"$lt": update_stamp}}, session=session)


def sync_callback(session):
    for collection in ["users", "wanderlists", "activities", "rewards"]:
        sync_table(session, collection)


def init():
    """
    Create the collections and search indexes that are mirrored from firebase
    """
    client = MongoClient(CONNECTION_STRING)
    for c in ["users", "rewards"]:
        try:
            client.wanderlist.create_collection(c)
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


def sync_transacted():
    wc_majority = WriteConcern("majority", wtimeout=1000)
    client = MongoClient(CONNECTION_STRING)

    with client.start_session() as session:
        session.with_transaction(sync_callback,
                                 read_concern=ReadConcern('local'),
                                 write_concern=wc_majority,
                                 read_preference=ReadPreference.PRIMARY)


def sync_notransaction():
    client = MongoClient(CONNECTION_STRING)
    with client.start_session() as session:
        sync_callback(session)


def sync_all():
    init()

    if USE_TRANSACTION:
        sync_transacted()
    else:
        sync_notransaction()


def fill_ref(mongo, ref_str):
    r = ref_str["ref"].split("/")
    coll = r[0]
    docid = r[1]
    record = mongo.db[coll].find_one({"_id": docid})
    if (record is not None):
        return clean_document(record)

    print(f"WARN: Ref miss: {ref_str}")
    return None


def fill_all_refs(mongo, doc: json):

    if doc is None:
        return doc

    if isinstance(doc, dict):
        if ('ref' in doc.keys()):
            # thing is reference
            doc = fill_all_refs(mongo, fill_ref(mongo, doc))
            return doc

    if isinstance(doc, dict):
        topop = []
        for key, val in doc.items():
            val = fill_all_refs(mongo, val)
            if val is None:
                topop.append(key)
            else:
                doc[key] = val
        for key in topop:
            doc.pop(key)

        if "_id" in doc:
            doc["id"] = doc.pop("_id")
        if "_updated" in doc:
            doc.pop("_updated")
    elif isinstance(doc, list) and not (isinstance(doc, str) or isinstance(doc, int) or isinstance(doc, float)):
        for i in reversed(range(len(doc))):
            ndoc = fill_all_refs(mongo, doc[i])
            if ndoc is None:
                doc.pop(i)
            else:
                doc[i] = ndoc

    return doc


if __name__ == "__main__":
    sync_all()
