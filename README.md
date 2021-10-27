
## Search API

Provides a simple REST api for searching the firebase instance.

## Installation
Installation of this API requires a working docker and docker-compose install. See steps below for details.

1. Setup a working install of Docker (https://docs.docker.com/get-docker/)
2. Setup a working install of docker-compose (https://docs.docker.com/compose/install/)
3. Run `git clone https://github.com/Pantone-448C/search-service` to clone the repository to `./search-service`
4. Place the Firebase Admin API JSON private key `wanderlistkey.json` within the cloned folder
5. Run `docker-compose up -d` from the cloned folder

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

