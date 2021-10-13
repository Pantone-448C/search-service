

class Activity:

    def __init__(self, json):
        self._json = json

    def id(self):
        return self._json["id"]

    def address(self):
        return self._json["address"]

    def locationJson(self):
        return self._json["location"]

    def locationLatLng(self):
        return tuple(self._json["location"]["coordinates"][::-1])

    def name(self):
        return self._json["name"]

    def tags(self):
        return self._json["tags"]

    def json(self):
        return self._json

class Wanderlist:

    def __init__(self, json):
        self._json = json

    def id(self):
        return self._json["id"]

    def name(self):
        return self._json["name"]

    def activities(self):
        return [Activity(a) for a in self._json["activities"]]

    def author_name(self):
        return self._json["author_name"]

    def json(self):
        return self._json
