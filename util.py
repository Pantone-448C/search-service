from pymongo.cursor import Cursor


def km_to_radian(x: float):
    return x / 6378.152


def m_to_radian(x: float):
    return x / 6378100.0


def cursor_to_json(c: Cursor):
    js = []
    for result in c:
        result.pop("_updated")
        result["id"] = result["_id"]
        result.pop("_id")
        js.append(result)
    return {"results": js}


def clean_document(d):
    d["id"] = d["_id"]
    d.pop("_id")
    d.pop("_updated")
    return d
