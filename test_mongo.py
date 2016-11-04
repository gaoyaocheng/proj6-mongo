
import pymongo
from pymongo import MongoClient
import sys
import secrets.admin_secrets
import secrets.client_secrets
import arrow

MONGO_ADMIN_URL = "mongodb://{}:{}@{}:{}/admin".format(
    secrets.admin_secrets.admin_user,
    secrets.admin_secrets.admin_pw,
    secrets.admin_secrets.host,
    secrets.admin_secrets.port)
records = [{ "type": "dated_memo",
       "date":  arrow.utcnow().replace(days=-1).naive,
       "text": "This is a sample yesterday",
      },
      { "type": "dated_memo",
       "date":  arrow.utcnow().naive,
       "text": "This is a sample today",
      },
      { "type": "dated_memo",
       "date":  arrow.utcnow().replace(days=+1).naive,
       "text": "Sample one day later",
      }]
date = ['Yesterday','Today', 'Tomorrow']

dbclient = MongoClient(MONGO_ADMIN_URL)
db = getattr(dbclient, secrets.client_secrets.db)
collection = db.dated

def test_save():
    for index, record in enumerate(records):
        record["id"] = index
        assert collection.insert(record)

def test_list():
    i = 0
    for item in collection.find({"type":"dated_memo"}).sort('date', pymongo.ASCENDING):
        print (item)
        print (records[i])
        assert item['id'] == records[i]['id']
        assert item['text'] == records[i]['text']
        i += 1

def test_remove():
    collection.remove({"id":records[0]['id']});
    count = collection.count({"id":records[0]['id']})
    assert count==0

    collection.remove({"type":"dated_memo"});
    count = collection.count({"type":"dated_memo"})
    assert count==0
