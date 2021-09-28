import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# https://firebase.google.com/docs/firestore/quickstart
cred = credentials.Certificate("wanderlistkey.json")
firebase_admin.initialize_app(cred)

def get_db():
    db = firestore.client()
    return db


if __name__ == "__main__":
    users_ref = get_db().collection(u'users')
    docs = users_ref.stream()

    for doc in docs:
        print(f'{doc.id} => {doc.to_dict()}')


