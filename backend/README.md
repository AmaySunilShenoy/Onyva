# Onyva 🚆 
Discover Paris and Île-de-France with ease using Onyva, your ultimate local navigation app


----------


# Collaborators 🫂 

This project was a group effort by:

- Upasana Sharma
- Aarjoo Khand
- Amay Sunil Shenoy


----------
# Usage 
## Prerequisites 

You need the following programs to run the application:

- Docker Desktop (or any docker daemon)


## Running the Backend with Docker
1. First, ensure you the docker daemon that is up and running.
2. Then run the following command to create your docker images and containers:


    $ docker compose up


3. The above command starts the `web server`, `mongodb`,  `redis`  and `neo4j` containers.


## Accessing the API
1. The web API will be started on `[http://localhost:8000](http://localhost:8000)` and the API can be accessed there. For easy usage to test the API, you can view all the routes at `[https://localhost:8000/docs](https://localhost:8000/docs)`.
2. To view the neo4j database, you can view at [](http://localhost:7474/browser/)`[http://localhost:7474/browser](http://localhost:7474/browser/)`


## Database Setup

The only database that needs to be setup with data is the `neo4j` database. This can be done by running the `Neo4j Init` API at `[https://localhost:8000/docs](https://localhost:8000/docs)`. This process will load the transport stops and routes between them and will take a few minutes.


# File Structure
----------
 ```
 +---app 🗂️
    |   | main.py 📄
    |   
    +---data 💾
    +---mongo_data 💾
    +---neo4j_db 💾
    | 
    --Database_Connection 🗂️
    |   |   MongoDB.py 🛢️
    |   |   Neo4j.py 🛢️
    |   |   Redis.py 🛢️
    |   |
    |   +---DataFiles
    |   |       stops.csv 📚 
    |   |       stops_new.csv 📚 
    |   |
    |
    +---Routes 🗂️
    |   |   auth_route.py 🔑
    |   |   database_route.py 🪣 
    |   |   path_route.py 🛣️ 
    |   |   subscription_route.py ⏰ 
    |   |   user_route.py 👤 
    |   
    +---Services 🗂️
    |   |   auth_service.py 🔑
    |   |   database_service.py 🪣 
    |   |   path_service.py 🛣️ 
    |   |   subscription_service.py ⏰ 
    |   |   user_service.py 👤 
    |   
    \---utils 🗂️
    |    |   JWTHandler.py 🔑
    |    
    |   .env 🔑
    |   .gitignore
    |   compose.yaml 🐳 
    |   Dockerfile 🐳 
    |   README.md 📄
    |   requirements.txt 📄
    
                
```
**File structure of the backend (API) portion of our application.**


    +---app 🗂️

This is the directory that contains the main fast API file to be ran to start the webserver. All routes and services are registered here.

----------

 

    +---data 💾
    +---mongo_data 💾
    +---neo4j_db 💾

These are the directories that store our database data. This is so that when the containers are stopped and re-ran, data integrity is maintained. (the `data` dir is redis)

----------


    --Database_Connection 🗂️
    |   |   MongoDB.py 🛢️
    |   |   Neo4j.py 🛢️
    |   |   Redis.py 🛢️
    |   |
    |   +---DataFiles
    |   |       stops.csv 📚 
    |   |       stops_new.csv 📚 
    |   |
    |

The database connection folder contains classes that helps us connect , access collections, and disconnect our database instances. These connections can also be accessed globally anywhere in the app, allowing for a single connection to the database for different uses, and therefore more centralised.

The nested `DataFiles` directory contains the csv files that are used to load the data into neo4j. These are the stations of various transport (stops.csv) and the sequence of these routes in their respective lines (stops_new.csv)


----------


    +---Routes 🗂️
    |   |   auth_route.py 🔑
    |   |   database_route.py 🪣 
    |   |   path_route.py 🛣️ 
    |   |   subscription_route.py ⏰ 
    |   |   user_route.py 👤 
    |   |
    +---Services 🗂️
    |   |   auth_service.py 🔑
    |   |   database_service.py 🪣 
    |   |   path_service.py 🛣️ 
    |   |   subscription_service.py ⏰ 
    |   |   user_service.py 👤 

These are the API routes and the services that are run when called with their paths. Each file contains the paths for a specific use case.

- Auth → Creating and Login of Users
- Database → Initializing the neo4j database with data
- Path → Journey and Closest Stop services
- Subscription → Subscription to different lines to receive reports about delays or any other issues.
- User → CRUD operations on user profile and adding of favorite stops


----------


    \---utils 🗂️
    |    |   JWTHandler.py 🔑
    |    

The utils folder contains any utility functions or classes we are using. In our case, we used it for a JWT token generator and verifier. This is a class that creates access and refresh tokens and to decode the token.


----------
    |   .env 🔑
    |   .gitignore
    |   compose.yaml 🐳 
    |   Dockerfile 🐳 
    |   README.md 📄
    |   requirements.txt 📄


- .env
    Stores all the keys and sensitive data of the application (used for JWT secret key)
- Dockerfile
    This is the docker file that has the start config for the python web server
- compose.yaml
    This is the compose file that creates the images and containers for the web server, mongodb, redis and neo4j
- requirements.txt
    This is where all the python dependencies are listed and will be installed inside the web server docker (needs to be installed locally if you want to run the server locally)


----------


# How we chose the Databases and why?

Our application is a route finder and has various different types of services. There are user services for authentication and managing profile information, route/path services to find the shortest path between two locations, subscription and so on.


## MongoDB

**Structure**

To store our users, we decided to use mongo db. 
The user model looks like :


    user = {
      id: ObjectId;
      name: str;
      email: str;
      password: str;
      favourites: [];
      }
    

**Why use MongoDB?**

**Scalability**: MongoDB is designed to scale out easily, allowing us to handle a growing number of users without a significant increase in complexity. We thought about using replica sets but since user login isn’t a major functionality, we thought it might be excessive but could be implemented in the future if our use case requires it.

**Flexibility**: One benefit for using mongo for storing the user is that we can quickly iterate and change the schema as needed without downtime. This is important when we are continuously improving our user-related features and need to adapt the database schema frequently.


## Neo4j

To store our stations and the relationships between them, we are using neo4j.

In the graph, the nodes are the stations and we have 3 different types of relationships.

**Nodes (Stops)**


    <elementId>: 4:fec9a4fe-6393-4918-b428-4fcd4aa2b978:14230
    <id>: 14230
    stop_id: IDFM:29361
    stop_lat: 48.75245747942941
    stop_lon: 2.37250760057213
    stop_name: Pont d'Espagne


- stop_id → Unique ID of a stop
- stop_lat → Latitude location of the stop
- stop_lon → Longitude location of the stop
- stop_name → Name of the stop

**NEXT_STOP Relationship**

This relationship is between two nodes and shows that one node is the next stop in the sequence of the transport line of the other node. This relationship also has its set of attributes:


    <elementId>: 5:fec9a4fe-6393-4918-b428-4fcd4aa2b978:112887
    <id>: 112887
    route_id: IDFM:C01204
    route_name: 183
    route_type: Bus


- route_id → Unique ID of a route (common for stops in that sequence)
- route_name → Common name of the route like (172 (Bus), 7 (Metro), B (RER))
- route_type → This can be Bus, Metro, RER, Tram or Night Bus

**PARENT_STATION Relationship**
This relationship is between two nodes one of which is the parent node of the other. For example, `Châtelet` is the parent node of `Les Halles` stop on M4, `Place du Châtelet` stop on Bus 47 and so on. The relationship between the Child towards the Parent is PARENT_STATION relation.


    <elementId>: 5:fec9a4fe-6393-4918-b428-4fcd4aa2b978:10
    <id>: 10
    child: IDFM:monomodalStopPlace:46736
    parent: IDFM:69254

Here the `child` attribute is the stop_id of the child and the `parent` attribute is the stop_id of the parent. 

**CHILD_STATION**
Similar to the previous PARENT_STATION relationship, it is a relationship from the Parent node towards the Child node and has the same attributes as the PARENT_STATIOn relation.


**Why use Neo4j?**

Neo4j is a graph database, which is perfect for representing the public transport network where stations are nodes and connections (lines) are edges. This structure allows us to find paths efficiently and perform query operations easily.

Using Cypher Queries in Neo4j, we are very easily able to find the shortest path between two nodes and with the help of indexes, find these routes in a matter of milliseconds. In our case, a SHORTESTPATH cypher is used to find the shortest path but requires some tweaking which is explained later on.

With Neo4j, managing and querying complex relationships between stations and lines is straightforward. We can easily query for shortest paths, find connections, and understand the network structure.


## Redis

**Structure**

To cache recent user history and searches, we are using redis. We are also using redis’ pubsub feature as a message queue to send delay/crime reports about certain lines to users who have subscribed to them

**Cache**

When a user searches for a certain start and end point (with the time), we store this search in redis, identified by the users id. Later on, for our frontend application, we can quickly get access to this data to display to the user their recent search history (limited at last 5). The same logic applies for when a user searches for nearby stops near their location.

We also store the result of the above searches. This data is shared amongst all users and so if two users make the search request, we can give the second user with the result of the first users search query. This reduces the burden on our server to calculate the shortest path. (this data has a set TTL and expires after 30 minutes)

**Publish/Subscribe (Message Queues)**

We are also using redis for a subscription service where users can subscribe to various different transport lines and receive reports about any delays, accidents or crimes. We are also storing these reports in redis for each access.


**Why use Redis?**

As Redis uses an in-memory key-value store, it is extremely fast which is perfect for caching recent searches and user history to speed up the response times of our app. Especially since our finding shortest path service is an expensive service, caching search results can speed up our app and increase user satisfaction.

Since we can set expiration times for cached data, it ensures that our app provides fresh and relevant information without manual intervention. (deleting of data manually)

Redis has a built-in pub/sub messaging system, which allows our users to subscribe to updates on specific lines and receive real-time notifications. This is ideal for receiving and disseminating real-time reports about line statuses, delays, and other important updates to users.

Redis supports various data structures like strings, lists, sets, and sorted sets, which can be useful for implementing features like storing recent searches, frequently used routes, and more.
In our case, we use ltrim and lrange to limit our list sizes, making it very easy for data storage and management.




# Use of Queries

Now we will highlight the main queries we have used in our project and a bit of explanation about the logic of the queries.

## Neo4j: Find the shortest path query

Our query for finding the shortest path is as follows:


    MATCH (startNode:Stop {{stop_id: $start}}), (endNode:Stop {{stop_id: $end}})
        CALL {{
            WITH startNode
            OPTIONAL MATCH (startNode)-[startRoute : NEXT_STOP]-()
            RETURN startRoute.route_id as routes
            UNION
            WITH endNode
            OPTIONAL MATCH (endNode)-[endRoute : NEXT_STOP]-()
            RETURN endRoute.route_id as routes
        }}
        WITH startNode, endNode, COLLECT(routes) AS allRoutes
        OPTIONAL MATCH path = SHORTESTPATH ((startNode)-[*]-(endNode))
        WHERE ALL(r IN RELATIONSHIPS(path) WHERE {time} (r.route_id IN allRoutes OR r.parent IS NOT NULL))
        WITH startNode, endNode, path, LENGTH(path) AS nbstations, allRoutes
        OPTIONAL MATCH temppath2 = SHORTESTPATH ((startNode)-[*]-(endNode))
        WHERE ALL(r in relationships(temppath2) WHERE {time} (r.route_id IS NOT NULL OR r.parent IS NOT NULL))
        UNWIND relationships(temppath2) AS allRoutesAlt
        WITH DISTINCT allRoutesAlt.route_id AS correspondance, startNode, endNode, allRoutes, path, nbstations, allRoutesAlt
        OPTIONAL MATCH path2 = SHORTESTPATH ((startNode)-[*]-(endNode))
        WHERE ALL(r IN RELATIONSHIPS(path2) WHERE {time} (r.route_id IN allRoutes OR r.route_id = correspondance OR r.parent IS NOT NULL))
        WITH path2, LENGTH(path2) AS nbstations2, path, nbstations, allRoutes, allRoutesAlt
        ORDER BY nbstations2
        LIMIT 1
        WITH path, nbstations, path2, nbstations2, allRoutes, allRoutesAlt,
        CASE
            WHEN nbstations <= nbstations2 + 5 THEN path
            ELSE path2
        END AS finalPath
        
        RETURN finalPath
    

Now as we previously mentioned, there already exists a shortest path cypher in neo4j. So why not simply use that?

The reason is that only using the shortestPath function results in many different traversals. Since neo4j doesnt care what the route_id is of the relation, it will swap different modes of transport constantly to find the shortest path, and while this maybe indeed the shortest path, it is not how transport is used in real life. The cost of changing modes of transport (which includes the connection time and waiting time) highly outweighs the benefit. But at the same time, we don’t want to produce a route that sticks only to 1 or 2 routes but is very slow.

Now this query isn’t perfect and requires some refactoring in the decision making but it works most of the time.

Below is the line by line explanation of the query,

**Line 1**

- Gets two nodes startNode and endNode with a provided stop_id for each

**Line 2  - 11**

- We use a CALL, which is a subquery to get all the NEXT_STOP relationships that are connected to the startNode as `routes` and combine them with the NEXT_STOP relationships that are connected to the endNode.
- Now we have a list of all routes that startNode and endNode are a part of called `allRoutes` (Line 11)

**Line 12 - 13**

- Now we use OPTIONAL MATCH to find our first path using shortest path with a condition that all the relationships in the path belong to `allRoutes` or the `parent` attribute is not null which allows the path to use the parent node to switch to different modes if needed. (We will ignore the `{time}` variable for now)
- This path would be the path with the least number of transfers possible since it only uses routes that are connected to the start and end nodes.
- We then store the length of this path in a variable `nbstations`

**Line 14 - 17**

- Now we find a `temp` path that is simply using the shortestPath cypher.
- We do this so that we can get one extra transfer that we might use to reach the destination, since most routes in the paris region require only 1 or 2 transfer on average.
- We use UNWIND to get all the relationships and we then take the first distinct element and store it in `correspondance`.

**Line 18 - 20**

- We now find our second possible path, but this time we extend the shortestPath to also use the `correspondence` route. (Again ignore the `{time}` variable for now), This is now `path2`
- We also store the length of this path in `nbstations2`

**Line 21 - 23**

- We now limit the `path` and the `path2` to the shortest one by ordering by the number of stations. (This is because shortestPath cypher returns a list of possible shortest paths)

**Line 24 - 28**

- Now we do a CASE where we compare the difference between the two paths we created and if the first path (only using start and end relations) is shorter than the correspondance path (using an additional transfer) + 5, where 5 is a buffer and can be more fine tuned to a better average, we choose first path
- Or else we choose the second path
- Finally closed as `finalPath`

**Line 30**

- We then finally return the `finalPath`.

**NOTE :**
Lastly the `{time}` parameter is initially passed by the user as a certain hour of the day, if its during the day time, we don’t want to use the `Night Bus` and if its past midnight till 5am, we only want to use `Night Bus` so we use the following logic to handle that toggle:


    
      # Check if the time is between 00:00:00 and 05:00:00 to determine if it should only use night buses
        if time >= "00:00:00" and time <= "05:00:00":
            time = "(r.route_type = 'Night Bus' OR r.parent IS NOT NULL) AND "
        # If the time is not between 00:00:00 and 05:00:00, use all routes except night buses
        else:
            time = "(r.route_type <> 'Night Bus' OR r.parent IS NOT NULL) AND "
    



## Neo4j: Find Closest Station 

Our query for finding the shortest station is below:


    MATCH (s:Stop)
    WITH s, point.distance(point({latitude: $lat, longitude: $lon}), point({latitude: s.stop_lat, longitude: s.stop_lon})) AS distance
    ORDER BY distance
    RETURN s, distance
    LIMIT 5

**Line 1**

- We match a node Stop

**Line 2**

- We then take s, the Stop and then find the distance between the given latitude and longitude and the lat and lon of the stop.

**Line 3-5**

- We then order by `distance` which defaults to ascending. (so shortest distance first)
- Then we return the stop and the distance.
- And we limit it to only the 5 shortest stations.


## MongoDB: Creating User and Updating User Profile

For creating user and finding user for login, we used the following query:


    
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="email already in use")
    # Hash the password
    hashed_password = pwd_context.hash(password)
    # Create user document
    user_document = {
     "email": email,
      "hashed_password": hashed_password
    }
    # Insert user document into the database
    result = users_collection.insert_one(user_document)
    

Here we used `find_one` to find a user and make sure they don’t already exist and `insert_one` to create a new user.

For updating user, we used :


    def update_user_email(user_id: str, new_email: str):
        try:
            users_collection = mongo.get_collection("users")
            # Check if the new email is already in use
            existing_email = users_collection.find_one({"email": new_email})
            if existing_email:
                raise HTTPException(status_code=400, detail="The new email is already in use")
            
            # Update the email
            result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"email": new_email}})
            if result.modified_count > 0:
                return {"success": "Email updated successfully"}
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            

Again here we use `find_one` to find the user to make sure it exists (for error handling) and then use `update_one` and the `$set` operator to update the user’s email.



## MongoDB: Toggle favourites

We also store the favourite stops of a user in mongodb, as following :


     user = users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Check if the user has a fav_routes field and if not, create it
            if "fav_routes" not in user:
             
                users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"fav_routes": [route_id]}})
                return {"message": "Route added to favorites"}
            else:
                if route_id in user["fav_routes"]:
                   
                #    If route_id is present, remove it from the list
                    users_collection.update_one({"_id": ObjectId(user_id)}, {"$pull": {"fav_routes": route_id}})
                    return {"message": "Route removed from favorites"}
                else:
                    # If route_id is not present, add it to the list
                    users_collection.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"fav_routes": route_id}})
                    return {"message": "Route added to favorites"} 

Here we use the `$pull` operator to remove the favourite route if it is already in the list and if it isn’t in the list, we use the `$addToSet` to add to the favourite into the array (and also creates the array if it doesn’t exist).



## Redis: PubSub with Websockets

We created a publish and subscribe service with redis for route reports. We handle messages and send it to the user using the following function:

    
     # Subscribe to the user's channel (this will be used to forward message to the user depending on which routes they are subscribed to)
        pubsub = redis.pubsub()
        pubsub.subscribe(user_id)
        # Listen for messages on the user's channel
        try:
            for message in pubsub.listen():
                if message['type'] == 'message' and message['channel'].decode() == user_id:
                    data = message['data'].decode()
                    print(f"Sending message to {user_id}: {data}")
                    await websocket.send_text(data)
        except Exception as e:
            print(f"Error handling messages for {user_id}: {e}")
          

This will work well with the WebSocket on the frontend.

## Redis: Toggle Subscription

We use redis for subscription and use the following query to subscribe and unsubscribe to the route:


    
    # If the user is already subscribed, unsubscribe
        if redis.sismember(f"route:{route_id}", user_id):
            redis.srem(f"route:{route_id}", user_id)
            return {"success": "unsubscribed"}
        # If the user is not subscribed, subscribe
        redis.sadd(f"route:{route_id}", user_id)
        return {"success": "subscribed"}
    

Here the `sismember` method checks for the subscription of that user on a route, if so it uses `srem` to remove the subscription and if not, it uses `sadd` to add the user to the route subscription.



## Redis: Publish Report

We can publish reports for certain reports using the below function


    
      # Check if the same report has already been published for the given route
        report_key = f"route_id:{route_id}:{crime_report}"
        if redis.get(report_key):
            return {"error": "Crime report already published"}
        # Store the report in redis and publish it to all subscribers
        redis.set(report_key, user_id) 
        redis.publish(route_id, json.dumps({"route_id": route_id, "crime_report": crime_report}))
        

We use the `get` method to check whether the report has already been published, if not we use the `set` method to store the report in the redis database. We also use `publish` the report to the route_id topic so that all subscribers can receive it.


## Redis: Cache search results

We are also using redis to cache the results of a search query, we do that as follows


    # Check if the search key exists in the cache (redis)
        search_key = f"{start_latitude},{start_longitude},{end_latitude},{end_longitude},{time}"
        # If the search key exists, return the result from the cache
        if redis.exists(search_key):
            paths = redis.get(search_key)
            return json.loads(paths)

Here the function checks whether it already exists in the database and if so it just returns the database stored value, avoiding running the expensive shortest path query. And if this doesnt exist, after the query is ran, it is stored in redis


     # Store the search result in the cache with a timeout of 30 minutes (this is a shared pool of cache for all users, so any similar search with be fetched from the cache)
     redis.setex(search_key,1800, json.dumps(all_paths))

Here we use setex to search the search result with an expiry of 30 mins


## Redis: Cache search queries

We implemented caching of user search results with their user id so that we can quickly provide the recent history of the user


    
     # Store the search key in the recent searches list (by user id to fetch later)
        redis.lpush(f"{user_id}-recent_searches", search_key)
        # Trim the list to keep only the 5 most recent searches
        redis.ltrim(f"{user_id}-recent_searches", 0, 4)
        

We push the search query into the user’s recent searches using `lpush` and we trim it to only store the last 5 search results using `ltrim`.

Then we can retrieve this later using a function as follows,


    recent_searches = redis.get(f"{user_id}-recent_searches")
    recent_stations = redis.get(f"{user_id}-recent_stations")

We use the `get` method to retrieve and output it.


# Conclusion

The goal of this project was to incorporate different NoSQL databases cohesively in one application, namely MongoDB (document database), Neo4j(Graph database) and Redis (In-Memory database).

By leveraging MongoDB, Neo4j, and Redis , we ensure that our app is robust, scalable, efficient, and capable of giving optimal routes, delivering real-time updates and providing an optimal user experience for public transport navigation in Paris.

