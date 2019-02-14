#!/usr/bin/env python3

import time
from timeit import default_timer as timer
from pymongo import MongoClient
import settings
import datetime
import random
from faker import Faker

fake = Faker()

####
# Start script
####
start = timer()
print("============================")
print("  Insert Bank Account Data  ")
print("============================")


####
# Main start function
####
def main():
    mongo_client = MongoClient(MONGODB_ATLAS_URL)
    db = mongo_client[DATABASE]
    accounts_collection = db[COLLECTION]

    for idx in range(NUM_RECORDS_TO_GENERATE):
        account = {"firstName": fake.first_name(),
                   "lastName": fake.last_name(),
                   "phoneNumbers": [{
                       "type": "mobile",
                       "number": fake.phone_number()
                   }, {
                       "type": "home",
                       "number": fake.phone_number()
                   }
                   ],
                   "mobileNumber": fake.phone_number(),
                   "email": fake.email(),
                   "birthDate": datetime.datetime.strftime(fake.date_of_birth(tzinfo=None, minimum_age=16,
                                                                              maximum_age=90), '%m-%d-%Y'),
                   "address": {
                       "street": fake.street_address(),
                       "city": fake.city(),
                       "state": fake.state(),
                       "zip": fake.postalcode()
                   },
                   "accounts": [
                       {
                           "type": "savings",
                           "accountNumber": fake.credit_card_number(card_type=None),
                           "interestRate": random.uniform(1.1, 4.9),
                           "balance": random.randint(1, 5000)
                       },
                       {
                           "type": "checking",
                           "accountNumber": fake.credit_card_number(card_type=None),
                           "overdraftLimit": random.randint(0, 9999),
                           "balance": random.randint(-4999, 5000)
                       }
                   ]

                   }

        accounts_collection.insert_one(account)
        record_num = ++idx
        print("Inserted record: " + str(record_num))
        time.sleep(0.5)


####
# Constants loaded from .env file
####
MONGODB_ATLAS_URL = settings.MONGODB_ATLAS_URL
NUM_RECORDS_TO_GENERATE = int(settings.NUM_RECORDS_TO_GENERATE)
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
