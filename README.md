
## Search API

Provides a simple REST api for searching the firebase instance.

## Installation
Installation of this API requires a working docker and docker-compose install. See steps below for details.

1. Setup a working install of Docker (https://docs.docker.com/get-docker/)
2. Setup a working install of docker-compose (https://docs.docker.com/compose/install/)
3. Run `docker-compose up -d` from the root of the cloned/extracted folder

### Ports
The above docker-based installation automatically exposes port 8080 for the API and port 27017 for the MongoDB database to the localhost (i.e. these services can be accessed at localhost:8080 and localhost:27017). If either of these needed to be accessed externally to the host machine, the ports should be exposed in the firewall (i.e. port-forwarded). Please see the documentation for your computer/VM to see how to do this.

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

Errors return an error message in the "error" field of the returned JSON map.


#### GET Document

```shell
/activities/$id
/wanderlists/$id
/rewards/$id
```

### Search

methods: `GET`

Text query

```shell
/activities/?query=text query
```

By location

```shell
/activities/?lat=10&lon=10?range=50
```

The range is optional, and specified as a radius in kilometers of the specified location.

### Recommendation

methods: `GET`

By Wanderlist

```shell
/activities/?wanderlist=<wanderlistid>
```

For the authenticated user profile

```shell
/activities/?rec
```

### User

methods: `GET`, `POST`

The user is identified by the firebase user token.

```
/user
```

#### Rewards

methods: `GET`

The points required for each new reward to be attained by users.

```shell
/user/rewards/totalpoints
```

The next recommended award

```shell
/user/rewards/next
```

#### Wanderlist

methods: `GET`, `POST`

```shell
/wanderlists/wanderlistid
```

