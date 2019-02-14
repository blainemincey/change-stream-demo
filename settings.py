#!/usr/bin/env python3
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Accessing variables.
NUM_RECORDS_TO_GENERATE = os.getenv('NUM_RECORDS_TO_GENERATE')
MONGODB_ATLAS_URL = os.getenv('MONGODB_ATLAS_URL')
DATABASE = os.getenv('DATABASE')
COLLECTION = os.getenv('COLLECTION')

# Using variables.
# print('Num Records to generate: ' + NUM_RECORDS_TO_GENERATE)
print('MongoDB Atlas DB URL: ' + MONGODB_ATLAS_URL)
print('Database: ' + DATABASE)
print('Collection: ' + COLLECTION)

