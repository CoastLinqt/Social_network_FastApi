# Twitter Clone

The project is a new page of the social network Twitter.
Opportunities:
1. The user can add a new tweet.
2. The user can delete his tweet.
3. The user can fire another user.
4. The user can unsubscribe from another user.
5. The user can mark the tweet as liked.
6. The user can remove the mark"I like it."
7. The user can receive a feed from tweets.
8. A tweet may contain a picture

## Installation and launch

Find out that you have Docker and docker-compose installed.



1. Building and running containers with the application and database:
```
docker layout
```
## Usage
###1. Adding a tweet
```
PUBLICATIONS /api/tweets
HTTP parameter:
api key: str
{
"tweet_data": string
"tweet_media_ids": Array[int] // Optional parameter. The download
computer will connect to the endpoint/api/media. The frontend will
upload images there automatically when sending a tweet and send
the ID is in json.
}
```

#### Let's try to find an endpoint that will help create a new business. The backend will validate it and save it in the database. It takes a long time to reply to the ID of the created tweet.
```
{
"result": true,
“tweet_id”: int
}
```

### 2. The endpoint for downloading files from the application. The download takes place through
the submission of the form.
```
Mail /api/media environment
HTTP parameter:
api key: str
- form: file= "image".jpg”
```
#### It takes a long time to come back and be loaded.
```
{
"result": true,
“media_id”: int
}
```

###3. You are trying to find the end point to achieve the goal.
```
DELETE /api/tweets/<id>
HTTP parameter:
api key: str
```
#### A message about the operation status should be returned in response.
```
{
"result": correct
}
```

###4. The user can put a "Like" mark on the tweet.
```
PUBLISH /api/tweets/<id> / likes
HTTP parameter:
api key: str
```
#### A message about the operation status should be returned in response.
```
{
"result": correct
}
```

### 5. The user can remove the "Like" mark from the tweet.
```
DELETE /api/tweets/<id> / likes
HTTP parameter:
api key: str
```
#### A message about the operation status should be returned in response.
```
{
"result": correct
}
```

### 6. A user can fire another user.
```
POST /api/users/<id>/follow
HTTP parameter:
api key: str
```
#### A message about the operation status should be returned in response.
```
{
"result": true
}
```
### 7. The user can unsubscribe from another user.
```
DELETE /api/users/<id>/follow
HTTP parameters:
api key: str
```
#### A message about the operation status should be returned in response.
```
{
"result": true
}
```
### 8. The user can receive a feed with tweets.
```
RECEIVE /api/tweets
HTTP parameter:
api key: str
``
#### It takes a long time to return to sleep, as a witness to events for a lazy user.
``
{
"result": right,
in "tweet": [
{
"id": int,
"Commonwealth": string,
"attachments" [link_1, link_2,]
"author": {"id": int", "name": line}
“like": [{"user ID”: int,"name”: string}]
}]}
```
#### In case of any error on the backend side, return a message in the following format:
```
{
"result”: false,
“error_type”: str,
“error_message”: str
}
```

### 9. The user can receive information about his profile:
```
GET /api/users/me
HTTP parameter:
api key: str
```
#### In response, we get:
```
{
"result": "true",
"user": {
"id":"int",
"name":"str",
"subscribers": [{"id":"int", "name":"str"}],
"next":[{"id":"int", "name":"str"}]
}}
```


### 10. The user can access product information from any ID
```
GET /api/users/<id>
```
#### In response, we get:
```
{
"solution": "correct",
"user": {
"id":"int",
"name":"str",
"subscribers": [{"id":"int", "name":"str"}],
"next":[{"id":"int", "name":"str"}]
}}
```