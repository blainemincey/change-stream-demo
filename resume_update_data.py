#!/usr/bin/env python3

import time
from timeit import default_timer as timer
from pymongo import MongoClient
import settings

####
# Start script
####
start = timer()
print("=============================")
print("     Resume Example          ")
print(" Update a field on Checking  ")
print(" Accts w/ balance > $1k      ")
print("=============================")


####
# Main start function
####
def main():
    mongo_client = MongoClient(MONGODB_ATLAS_URL)
    db = mongo_client[DATABASE]
    accounts_collection = db[COLLECTION]

    find_query = {
        "accounts": {"$elemMatch": {"type": "checking", "balance": {"$gt": 1000}}},
        "resumeCounter": {"$exists": False}
    }

    counter = 0
    for document in accounts_collection.find(find_query):
        print("\nFound Checking Account w/ balance > $1000.")

        # increment counter
        counter = counter + 1

        filter_query = {
                        "_id": document['_id'],
                        "accounts": {"$elemMatch": {"type": "checking", "balance": {"$gt": 1000}}}
                        }

        update_query = {
            "$set": {"resumeCounter": counter}
        }

        update_results = accounts_collection.update_one(filter_query, update_query)
        print("Successful update with matched: " + str(update_results.matched_count) + " and modified count: " +
              str(update_results.modified_count))
        print("Incremented resumeCounter to customer acct with _id: " + str(document['_id']))
        print("Counter value: " + str(counter))

        time.sleep(1)


####
# Constants loaded from .env file
####
MONGODB_ATLAS_URL = settings.MONGODB_ATLAS_URL
DATABASE = settings.DATABASE
COLLECTION = settings.COLLECTION

####
# Main
####
if __name__ == '__main__':
    main()

####
# Indicate end of script
####
end = timer()
print('====================================================')
print('Total Time Elapsed (in seconds): ' + str(end - start))
print('====================================================')
