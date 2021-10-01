
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
