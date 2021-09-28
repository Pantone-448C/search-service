from google.cloud.firestore_v1 import GeoPoint
from google.cloud.firestore_v1.document import DocumentReference
from pymongo import GEOSPHERE, WriteConcern, MongoClient, ReadPreference, TEXT
from pymongo.errors import CollectionInvalid
from pymongo.read_concern import ReadConcern
import firebase
import time

from bson.codec_options import TypeCodec, TypeRegistry, CodecOptions

DB_NAME = "wanderlist"
CONNECTION_STRING = "mongodb://127.0.0.1:27017/wanderlist"
USE_TRANSACTION = False


def get_db():
    return MongoClient(CONNECTION_STRING)[DB_NAME]


"""

Convert a firebase document reference to 

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
    """
    Create the collections and search indexes that are mirrored from firebase
    """
    client = MongoClient(CONNECTION_STRING)
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


if __name__ == "__main__":
    sync_all()
