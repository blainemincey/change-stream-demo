#!/usr/bin/env python3

import time
from timeit import default_timer as timer
from pymongo import MongoClient
import settings

####
# Start script
####
start = timer()
print("=====================================")
print("      Delete Bank Account Data       ")
print(" Checking Acct with negative balance ")
print("=====================================")


####
# Main start function
####
def main():
    mongo_client = MongoClient(MONGODB_ATLAS_URL)
    db = mongo_client[DATABASE]
    accounts_collection = db[COLLECTION]

    find_query = {
        "accounts": {"$elemMatch": {"type": "checking", "balance": {"$lt": 0}}}
    }

    for document in accounts_collection.find(find_query):
        print("\nFound Checking Account with negative balance.")

        customer_first_name = document['firstName']
        customer_last_name = document['lastName']

        filter_query = {"_id": document['_id']}

        deleted_results = accounts_collection.delete_one(filter_query)
        print("Successfully deleted customer with negative checking balance.")
        print("Customer name: " + customer_first_name + " " + customer_last_name)
        print("Number of documents deleted: " + str(deleted_results.deleted_count))

        time.sleep(0.5)


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
