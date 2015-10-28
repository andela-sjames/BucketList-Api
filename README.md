# BucketList-Api [![Coverage Status](https://coveralls.io/repos/andela-sjames/BucketList-Api/badge.svg?branch=master&service=github)](https://coveralls.io/github/andela-sjames/BucketList-Api?branch=master)
Python Flask Api Demonstration


This is an API that allows users to create bucketlists and add items to their bucketlists.As a Token Based Api,  Authentication is used to ensure security, allowing Users interaction only when there are authenticated via a set a protocols.



EndPoint |Functionality|Public Access
---------|-------------|--------------
POST /auth/login|Logs a user in|TRUE
GET /auth/logout/username|Logs a user out| FALSE
POST /bucketlists/|Create a new bucket list|FALSE
GET /bucketlists/|List all the created bucket lists|FASLE
GET /bucketlists/id|Get single bucket list|FALSE
PUT /bucketlists/id|Update this bucket list|FALSE
DELETE /bucketlists/id|Delete this single bucket list|FALSE
POST /bucketlists/id/items/|Create a new item in bucket list|FALSE
PUT /bucketlists/id/items/item_id|Update a bucket list item|FALSE
DELETE /bucketlists/id/items/item_id|Delete an item in a bucket list|FALSE

##**__RESOURCES__**

**__AUTH__** __url_data__:username = "username"  

POST /auth/login | Logs a user in  
```Parameters/Input data: {"username":"testuser"}```  

GET /auth/logout/username | Logs a user out  __url_data__:username = "username"  
``` Parameters/Input data: nil ```  

**__User__**  __url data__: __username__ = __username__  

Only visible/exposed on login  

GET user/username  
``` Parameters/Input data: nil ```  

**BUCKETLIST** __url data__: __id__ = __bucketlist id__   

POST /bucketlists/  | create a new bucketlist  
``` Parameters/Input data: {"name":"name of bucketlist"} ```  

GET /bucketlists/ | List all the created bucket lists  
```Parameters/Input data: nil ```  

GET /bucketlists/id | Get single bucket list  
```Parameters/Input data: nil ```  

PUT /bucketlists/id | Update this bucket list  
```Parameters/Input data: {"name":"updata bucketlist name"}```   

DELETE /bucketlists/id | Delete this single bucket list  
``` Parameters/Input data: nil ```  


**__ITEMS__**  __url data__:__id__ = __bucketlist__ __id__, __item_id__ = __item id__   

POST /bucketlists/id/items/ | Create a new item in bucket list  
``` Parameters/Input data: {"name":"my bucketlistitem", "Done":false } ```  

PUT /bucketlists/id/items/item_id | Update a bucket list item  
``` Parameters/Input data: {"name":"update my bucketlistitem", "Done":true } ```  

DELETE /bucketlists/id/items/item_id | Delete an item in a bucket list  
``` Parameters/Input data: nil ```  


##WORKFLOW
User login/registers via ``` POST auth/login``` route and a request token route is exposed.  
User sends a ```GET``` request to exposed route using username and password.  
User uses token which expires after a period of 1 hour.  
User obtains token if he/she wants to continue using  Api services.  
User can choose to log out using ``` GET auth/logout/username``` which invalidates his/her token.     
Once User is logged out, user will have to login to have access to valid token.  
If User token is still valid before logout, logging out will invalidate the user token.  

RESTful API is RESTLESS and so no user session is stored.


#USAGE
Install dependencies using ``` pip install -r requirements.txt ```    
Run ``` python manager.py runserver``` to start server  
Test Api using ```POSTMAN```  or ``` cURL ```  






