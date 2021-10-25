
BAD_REQUEST = ({"error": "Bad request"}, 400)

ACTIVITY_SEARCH_ARGS = ({"error": "Bad request",
                         "reason": "Provide either a location or search query",
                         "required one of": [["lat", "lon"], "query"]}, 400)

NEAR_ARGS = ({"error": "Bad request",
              "required args": ["lat", "lon"],
              "optional args": ["range"]
              }, 400)


NOT_FOUND = ({"error": "Not found"}, 404)

BAD_COLLECTION = ({"error": "Not found"}, 400)

NO_AUTH = ({"error": "No authorization"}, 401)

NOT_PERMITTED = ({"error": "Not permitted "}, 401)

NO_REWARDS = ({"error": "No appropriate reward found"}, 404)

ERROR_500 = ({"error": "Internal Server Error"}, 500)
