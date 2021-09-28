#    sync_activities()
import cachedb
import waitress
import apiserver

if __name__ == "__main__":
    cachedb.sync_all()
    print("Serving on 0.0.0.0:8080")
    waitress.serve(apiserver.app, host='0.0.0.0', port=8080)
