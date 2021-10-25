import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

import os

# https://firebase.google.com/docs/firestore/quickstart
cred = credentials.Certificate(os.environ.get("ADMIN_KEY_FILE"))
firebase_admin.initialize_app(cred)


def get_db():
    db = firestore.client()
    return db


if __name__ == "__main__":
    users_ref = get_db().collection(u'users')
    docs = users_ref.stream()

    for doc in docs:
        print(f'{doc.id} => {doc.to_dict()}')


def verify_token(id_token):
    decoded_token = auth.verify_id_token(id_token)
    return decoded_token
