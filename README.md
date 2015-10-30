# BucketList-API [![Coverage Status](https://coveralls.io/repos/andela-sjames/BucketList-Api/badge.svg?branch=master&service=github)](https://coveralls.io/github/andela-sjames/BucketList-Api?branch=master) [![Build Status](https://travis-ci.org/andela-sjames/BucketList-Api.svg?branch=master)](https://travis-ci.org/andela-sjames/BucketList-Api)
Python Flask API Demonstration


This is an API that allows users to create bucketlists and add items to their bucketlists.As a Token Based Api,  Authentication is used to ensure security, allowing Users interaction only when there are authenticated via a set a protocols.



EndPoint |Functionality|Public Access
---------|-------------|--------------
POST /auth/login|Logs a user in|TRUE
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
User login/registers via ``` POST auth/login``` route and is given a token    
User uses token which expires after a period of 24 hour.  
User obtains token if he/she wants to continue using  API services.       
User uses token to make request to server for resources defined above.    

RESTful API is STATELESS and so no user session is stored.

##OTHER FEATURES  
User can search for bucketlist using limits and page(pagination via limit)  
``` GET /bucketlists/limit=2 ``` and ``` GET /bucketlists/limit=4&page=1```  
Default limit without specification is 20 and default page number is 1.  
```GET /bucketlists/id/limit=5 ``` and ```GET /bucketlists/id/limit=4&page=2```  

User can also search for bucketlist using search parameter q.  
``` GET /bucketlists/q=create ``` and  ``` GET /bucketlists/q='game'&limit=4&page=1```  



#USAGE
Install dependencies using ``` pip install -r requirements.txt ```    
Run ``` python manager.py runserver``` to start server  
Test Api using ```POSTMAN```  or ``` cURL ```  

####Database Used: Postgress.  
Set User: Administrator  
Password: administrator  
Database name: bucketlist  

######HAVE FUN!!!






