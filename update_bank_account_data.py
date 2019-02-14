#!/usr/bin/env python3

import time
from timeit import default_timer as timer
from pymongo import MongoClient
import settings

####
# Start script
####
start = timer()
print("============================")
print("  Update Bank Account Data  ")
print(" Savings Acct Balance < $1k ")
print("============================")


####
# Main start function
####
def main():
    mongo_client = MongoClient(MONGODB_ATLAS_URL)
    db = mongo_client[DATABASE]
    accounts_collection = db[COLLECTION]

    find_query = {
        "accounts": {"$elemMatch": {"type": "savings", "balance": {"$lt": 1000}}}
    }

    for document in accounts_collection.find(find_query):
        print("\nFound Savings Account with under $1000.")

        filter_query = {"_id": document['_id'],
                        "accounts": {"$elemMatch": {"type": "savings", "balance": {"$lt": 1000}}}}

        update_query = {
            "$inc": {"accounts.$.balance": 100}
        }

        update_results = accounts_collection.update_one(filter_query, update_query)
        print("Successful update with matched: " + str(update_results.matched_count) + " and modified count: " +
              str(update_results.modified_count))
        print("Added $100 to customer acct with _id: " + str(document['_id']))

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
