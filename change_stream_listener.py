#!/usr/bin/env python3

import asyncio
import time
import settings
import sys
import os
from pymongo import MongoClient
from threading import Thread


####
# Start script
####
print("==========================================")
print("    Change Stream Listener                ")
print("Change Stream Events currently monitored: ")
print("Insert, Update, Delete, Replace           ")
print("                                          ")
print("Resume functionality is a separate thread ")
print("==========================================")


####
# Main start function
# Start each individual thread for each event
# Sleep momentarily after starting each thread
####
def main():
    print('Starting Change Stream Listener.\n')

    # Create the insert thread
    insert_loop = asyncio.new_event_loop()
    insert_loop.call_soon_threadsafe(insert_change_stream)
    t = Thread(target=start_loop, args=(insert_loop,))
    t.start()
    time.sleep(0.25)

    # Create the update thread
    update_loop = asyncio.new_event_loop()
    update_loop.call_soon_threadsafe(update_change_stream)
    t = Thread(target=start_loop, args=(update_loop,))
    t.start()
    time.sleep(0.25)

    # Create the delete thread
    delete_loop = asyncio.new_event_loop()
    delete_loop.call_soon_threadsafe(delete_change_stream)
    t = Thread(target=start_loop, args=(delete_loop,))
    t.start()
    time.sleep(0.25)

    # Create the replace thread
    replace_loop = asyncio.new_event_loop()
    replace_loop.call_soon_threadsafe(replace_change_stream)
    t = Thread(target=start_loop, args=(replace_loop,))
    t.start()
    time.sleep(0.25)

    # Create the resume example thread
    resume_loop = asyncio.new_event_loop()
    resume_loop.call_soon_threadsafe(resume_change_stream)
    t = Thread(target=start_loop, args=(resume_loop,))
    t.start()
    time.sleep(0.25)


####
# Make sure the loop continues
####
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


####
# Insert Change Stream
####
def insert_change_stream():
    print("Insert listener thread started.")
    print("==Checking Accounts with negative balance.\n")
    mongo_client = MongoClient(MONGODB_ATLAS_URL)
    db = mongo_client[DATABASE]
    accounts_collection = db[COLLECTION]

    # Change stream pipeline
    pipeline = [
        {'$match': {'operationType': 'insert'}},
        {'$match': {'fullDocument.accounts.type': 'checking'}},
        {'$match': {'fullDocument.accounts.balance': {"$lt": 0}}}
    ]

    try:
        for document in accounts_collection.watch(pipeline=pipeline, full_document='updateLookup'):
            result = "=== INSERT EVENT ===\n"
            result = result + "Checking Account with negative balance!\n"
            result = result + "Emailing user: " + document['fullDocument']['email'] + '\n'

            # Be sure to only display the balance for the checking account
            if document['fullDocument']['accounts'][0]['type'] == 'checking' :
                result = result + 'Checking Acct Balance: ' + str(document['fullDocument']['accounts'][0]['balance']) \
                                + '\n'
            else:
                result = result + 'Checking Acct Balance: ' + str(document['fullDocument']['accounts'][1]['balance']) \
                                + '\n'

            print(result)
    except KeyboardInterrupt:
        keyboard_shutdown()


####
# Update Change Stream
####
def update_change_stream():
    print("Update listener thread started.")
    print("==Savings Acct w/ balance less than 1000.\n")
    mongo_client = MongoClient(MONGODB_ATLAS_URL)
    db = mongo_client[DATABASE]
    accounts_collection = db[COLLECTION]

    # Make sure resume counter does NOT exist as it is being used
    # to trigger the resume operation in another thread
    pipeline = [
        {'$match': {'operationType': 'update'}},
        {'$match': {'fullDocument.accounts.type': 'savings'}},
        {'$match': {'fullDocument.accounts.balance': {'$lt': 1000}}},
        {'$match': {'fullDocument.resumeCounter': {'$exists': False}}}
    ]

    try:
        for document in accounts_collection.watch(pipeline=pipeline, full_document='updateLookup'):
            result = "\n=== UPDATE EVENT ===\n"
            result = result + "Savings Account Deposit\n"
            result = result + "Customer: " + document['fullDocument']['firstName'] + " " + \
                     document['fullDocument']['lastName'] + '\n'
            result = result + "Updated Savings Balance to: "
            result = result + str(document['updateDescription']['updatedFields']['accounts.0.balance']) + '\n'

            print(result)

    except KeyboardInterrupt:
        keyboard_shutdown()


####
# Delete Change Stream
####
def delete_change_stream():
    print("Delete listener thread started.")
    print("==All delete operations.\n")
    mongo_client = MongoClient(MONGODB_ATLAS_URL)
    db = mongo_client[DATABASE]
    accounts_collection = db[COLLECTION]

    pipeline = [
        {'$match': {'operationType': 'delete'}}
    ]

    try:
        for document in accounts_collection.watch(pipeline=pipeline, full_document='updateLookup'):
            result = "\n=== DELETE EVENT ===\n"
            result = result + "Customer deleted from collection: " + str(document['ns']['coll']) + "\n"
            result = result + "Customer _id: " + str(document['documentKey']['_id']) + "\n"

            print(result)

    except KeyboardInterrupt:
        keyboard_shutdown()


####
# Replace Change Stream
####
def replace_change_stream():
    print("Replace listener thread started.")
    print("==Replace operation typically from MongoDB Compass.\n")
    mongo_client = MongoClient(MONGODB_ATLAS_URL)
    db = mongo_client[DATABASE]
    accounts_collection = db[COLLECTION]

    pipeline = [
        {'$match': {'operationType': 'replace'}}
    ]

    try:

        for document in accounts_collection.watch(pipeline=pipeline, full_document='updateLookup'):
            result = "\n=== REPLACE EVENT ===\n"
            result = result + "Did this change occur in MongoDB Compass?\n"
            result = result + str(document) + "\n"

            print(result)

    except KeyboardInterrupt:
        keyboard_shutdown()


####
# Resume capability implemented
####
def resume_change_stream():
    print("Resume listener thread started.")
    print("==Updates to checking accts w/ balance greater than 100.\n")
    mongo_client = MongoClient(MONGODB_ATLAS_URL)
    db = mongo_client[DATABASE]
    accounts_collection = db[COLLECTION]

    pipeline = [
        {'$match': {'operationType': 'update'}},
        {'$match': {'fullDocument.accounts.type': 'checking'}},
        {'$match': {'fullDocument.accounts.balance': {'$gt': 100}}},
        {'$match': {'fullDocument.resumeCounter': {'$exists': True}}}
    ]

    # cursor to watch for specific updates
    cursor = accounts_collection.watch(pipeline=pipeline, full_document='updateLookup')
    # variable to indicate when to close change stream
    resume_counter = 0

    # loop thru docs in cursor
    try:
        for document in cursor:

            resume_token = document['_id']
            resume_counter = resume_counter + 1
            # check that the resumecounter field has been updated in document
            fulldoc_resume_counter_value = document['fullDocument']['resumeCounter']

            result = "\n=== RESUME EXAMPLE ===\n"
            result = result + "Resume token: " + str(resume_token) + "\n"
            result = result + "Counter value: " + str(fulldoc_resume_counter_value) + "\n"
            print(result)

            # once the resume_counter is greater than specified integer, sleep, close change stream, restart
            if resume_counter > 4:
                print("Resume Counter: " + str(resume_counter))
                print("Simulate failure for 10 seconds...")
                time.sleep(10)
                cursor.close
                print("Resume Change Stream closed.")
                print("Restart Change Stream with resume token: " + str(resume_token))
                # reset the cursor with resume token
                cursor = accounts_collection.watch(pipeline=pipeline,
                                                   full_document='updateLookup', resume_after=resume_token)
                # reset variables
                resume_counter = 0
                continue

    except KeyboardInterrupt:
        keyboard_shutdown()


###
# "Gracefully" consume output via ctrl-c
###
def keyboard_shutdown():
    print('Interrupted\n')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


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

