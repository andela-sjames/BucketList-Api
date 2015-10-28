# BucketList-Api [![Coverage Status](https://coveralls.io/repos/andela-sjames/BucketList-Api/badge.svg?branch=master&service=github)](https://coveralls.io/github/andela-sjames/BucketList-Api?branch=master)
Python Flask Api Demonstration


This is an API that allows users to create bucketlists and add items to their bucketlists.As a Token Based Api,  Authentication is used to ensure security, allowing Users interaction only when there are authenticated via a set a protocols.



EndPoint |Functionality|Public Access
---------|-------------|--------------
POST /auth/login|Logs a user in|TRUE
GET /auth/logout<username>|Logs a user out| FALSE
POST /bucketlists/|Create a new bucket list|FALSE
GET /bucketlists/|List all the created bucket lists|FASLE
GET /bucketlists/<id>|Get single bucket list|FALSE
PUT /bucketlists/<id>|Update this bucket list|FALSE
DELETE /bucketlists/<id>|Delete this single bucket list|FALSE
POST /bucketlists/<id>items/|Create a new item in bucket list|FALSE
PUT /bucketlists/<id>items/<item_id>|Update a bucket list item|FALSE
DELETE /bucketlists/<id>items/<item_id>|Delete an item in a bucket list|FALSE



