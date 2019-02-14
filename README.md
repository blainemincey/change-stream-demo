# CHANGE-CAPTURE 

Ability for applications to listen for and react to individual database events, in realtime (e.g. for fraud detection for updating a realtime visual dashboard or for CDC capture for downstream systems).

_SA Maintainer_: [Blaine Mincey](mailto:blaine.mincey@mongodb.com)

## Description

This proof demonstrates how MongoDB can be utilized to easily implement CDC 
(Change Data Capture) by using the native Change Streams capability within MongoDB.  
Change Streams allow applications to access real-time data changes without the 
complexity and risk of tailing the oplog.  Applications can use change streams
to subscribe to all data changes on a single collection, a database, or an entire
deployment, and immediately react to them.  Because change streams use the aggregation
framework, applications can also filter for specific changes or transform the notifications
at will.

In order to illustrate this capability, we will run several different Python processes
to capture several distinct CRUD style operations within MongoDB.  Specifically, we will
run a multi-threaded Python process that will essentially listen for changes in a 
specific collection for Insert, Update, Delete, and Replace operations.  Also, we will
illustrate how a change stream can be interrupted and then resumed without missing a single
change.

## Setup
__1. Identify an Atlas cluster__
* Using a cluster you have already created in MongoDB Atlas or one that has
already been created in any tier size will suffice for this proof.

__2. Download/Clone the proof to a root or working directory__
Within your root/working directory, you should have the following:
* [.env.example](.env.example) - Environment variable file that should be renamed to .env 
* [change_stream_listener.py](change_stream_listener.py) - Multi-threaded script to listen for change events
* [delete_bank_account_data.py](delete_bank_account_data.py) - Script to run delete operations
* [insert_bank_account_data.py](insert_bank_account_data.py) - Script to run insert operations
* [reset.py](reset.py) - Script to reset/create the database and collection
* [resume_update_data.py](resume_update_data.py) - Script to update data and trigger a resume operation
* [settings.py](settings.py) - Script to load environment variable from .env
* [update_bank_account_data.py](update_bank_account_data.py) - Script to run update operations
* [README.md](README.md) - This README file

__3. Configure Environment Variables__
* Be sure to rename .env.example to .env
* This file contains a number of variables:
    * NUM_RECORDS_TO_GENERATE - Defaults to 100 for the insert script
    * DATABASE - Name of the database that is defaulted to 'bankdatabase'
    * COLLECTION - Name of the collection that is defaulted to 'accounts'
    * MONGODB_ATLAS_URL - The URL to your MongoDB Atlas cluster
* Copy the Application Short SRV connection string for your Atlas cluster and paste it
into your .env file in the MONGODB_ATLAS_URL variable

!["SRV"](images/Copy_Srv_From_Atlas.png)

Be sure to add your password to the URL.  For example:
````
MONGODB_ATLAS_URL = mongodb+srv://bmincey:thePassword@changestreamcluster-r4qj4.mongodb.net/bankdatabase?retryWrites=true
````

__4. Ensure Python3 is setup properly__
* This proof was developed using Python3
* The following may need to be installed to your environment using Pip3:
    * pip3 install python-dotenv
    * pip3 install pymongo
    * pip3 install dnspython
    * pip3 install Faker
    
Once these modifications have been made, we can begin testing the proof.

__5. Execute [reset.py](reset.py)__

This script should be run initially in order to create the database and collection
as these must exist prior to starting a change stream.  Upon execution, you should have this:

![](images/reset-script.png)


__6. Start the primary script [change_stream_listener.py](change_stream_listener.py)__ 

This script upon successful startup, will indicate the following:

![](images/change_stream_start.png)

This script should indicate that a change stream listener has started for Insert, 
Update, Delete, and Replace events along with the filter being used.  Also, an indication
of a 'resume' thread should be indicated along with its filter.
    
## Execution

### Insert Event
Open a separate terminal and run the [insert_bank_account_data.py](insert_bank_account_data.py) script.
While it is running, you should see output similar to the following indicating that bank
records are being inserted:

![](images/insert.png) 

While the insert script is running, check the terminal for the change stream output 
which should look like the following:

![](images/insert_cs.png)

The Insert event is filtered for any bank customers inserted into the accounts collection
with a negative checking account balance.

### Update Event

Next, we will test the update change stream functionality by running the [update_bank_account_data.py](update_bank_account_data.py). 
As this is run, the output should look like the following:

![](images/update.png)

As indicated, the script is filtering for checking accounts with under $1000 in the balance and
adding $100 to it.

As the script is running, check the terminal where the change stream listener is running
and the output should be similar to the following:

![](images/update_cs.png)

The Update event is being filtered for bank customers where their checking account
has a deposit made and indicating the new balance.

### Delete Event

Next, we will test the delete change stream functionality by running the [delete_bank_account_data.py](delete_bank_account_data.py).
As this script is executing, you should see the following in the terminal:

![](images/delete.png)

The delete script is deleting customers with a negative checking account balance.

As the delete script is running, check the terminal output for the change stream listener and you
should find similar output to the following:

![](images/delete_cs.png)

### Replace Event

Next, we will test the replace change stream functionality by utilizing the use of MongoDB Compass.
It should be noted the when an update to a document is made using MongoDB Compass, a full
document replace occurs.  Connect to your MongoDB Atlas Cluster using MongoDB Compass and find open
the existing documents in the database we are using.  If you kept the default settings,
this will be the 'bankdatabase' and the 'accounts' collection.  Locate a random
document in the collection and make a few updates to it and then click 'Update'.  This
should look similar to what is here:

![](images/compass_replace.png)

After you have clicked the 'Update' button, check the terminal output for our change stream
listener.  If you made updates to a single document, there will only be a single entry in the 
terminal.  You should see output similar to this:

![](images/replace_cs.png)

 
## Measurement

For our final execution of the proof, we will test the resume capability of
change streams.  This is a critical aspect of MongoDB Change Streams as it provides
the capability of not losing any changes and being able to resume immediately following
the last change event.

### Resume Capability

Start the [resume_update_data.py](resume_update_data.py) script.  The output should
be similar to the following:

![](images/resume.png)

This script is filtering for customers with a checking account balance greater
than $1000.  For these records, an additional field named 'resumeCounter' is added
to the specific document and increased by 1 so we can verify if we missed any records
as we are going to terminate the change stream and then restart it.

Inspect the output of the change stream terminal, you should see something similar to the 
following:

![](images/resume_cs.png)

It should be noted that for every 5 updates, the change stream listener will 
simulate a 10 second failure while the [resume_update_data.py](resume_update_data.py) is
running.  After 10 seconds, the resume change stream is closed and then re-established
using the resume token.  Take note of the 'Counter Value' value as this is being 
incremented by 1.  You should see, for example, in the image above, the Counter Value
is 5 when a failure is indicated.  Once the change stream restarts, the Counter Value
starts at 6 as expected.

You can do a quick inspection using MongoDB Compass to ensure that no increments
of the 'resumeCounter' field were lost during the failure simulations by doing something
similar to this:

![](images/compass_spotcheck.png)

Simply filter within MongoDB Compass for documents with the 'resumeCounter' field that
is greater than 0, sort by 'resumeCounter' ascending, and then project only the 'resumeCounter'
field.

