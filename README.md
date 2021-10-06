
## Search API

Provides a simple REST api for searching the firebase instance.

## Installation

1. Ensure you have a working local mongodb server. 
2. Place the admin api json private key at `wanderlistkey.json`
3. Ensure the constant `CONNECTION_STRING` in `cachedb.py` to points to the mongodb
   instance.

```shell
python3 -m venv env 
source env/bin/activate
pip install -r requirements.txt
python main.py
```

- `python cachedb.py` will sync the Firestore into mongodb
- `python main.py` will sync the Firestore and start the flask server

## API
Must Set header

```shell
authorization: $firebase_user_token
```

This can be obtained in flutter using:

```dart
  _getToken() async {
    print(await FirebaseAuth.instance.currentUser!.getIdToken());
    return {"authorization": await FirebaseAuth.instance.currentUser!.getIdToken()};
  }
```

### GET

#### Whole Document

```shell
/activities/$id
/wanderlists/$id
/rewards/$id
```

### Search

Text query

```shell
/activities/?query=text query
```

By location

```shell
/activities/?lat=10&lon=10?range=50
```

The range is optional, and specified as a radius in kilometers of the specified location.

### User

The user is identified by the firebase user token.

```
/user
```

#### Rewards

The points required for each new reward to be attained by users.

```shell
/user/rewards/totalpoints
```

The next recommended award

```shell
/user/rewards/next
```

