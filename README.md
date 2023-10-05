# Pairing_Bot
> A Line robot provides dating services.


## Introduction
Service owners organize several events on different topics. Customers who apply these events may pair with others.

This service is on Line application, based on [__Messaging API__](https://developers.line.biz/en/services/messaging-api/) and __Flask__.

This sample codes provides a book exchange event. Customers can upload a book they want to share/exchange and pair with another book they are interest in.

## Structure
![image](https://github.com/jack2012aa/Dating_Bot/blob/reconstruct/result/structures.png)

`app.py` uses Flask to accept messages from Messaging API and routes them to `services.line_message_handler`

`services` provides procedures to handle requests.  `user_actions_manager` manages requests of sign up and event application. 
`find_book_actions_manager` and `upload_book_actions_manager` manages requests of present book exchange event.

`models` connects to a database and provides `services` essential information.

## Result
![image](https://github.com/jack2012aa/Dating_Bot/blob/reconstruct/result/IMG_3111.PNG)
![image](https://github.com/jack2012aa/Dating_Bot/blob/reconstruct/result/IMG_3112.JPG)
![image](https://github.com/jack2012aa/Dating_Bot/blob/reconstruct/result/IMG_3113.PNG)
![image](https://github.com/jack2012aa/Dating_Bot/blob/reconstruct/result/IMG_3114.PNG)


## User replys
The book exchange event was hold in 2023/2 but only a few people attended. Most comments mentioned that the UI was unclear, too complicated, and difficult to use. After discussion we think that

1. the apply form should be done by forms like google forms to reduce applying difficulty, and
2. a backstage may help our group to maintain events.

Furthermore, in my own opinion,

3. the procedure of events should be more modelized to reduce the difficulty on establishing new events.

## Authers
Idea from Ya-Chi Wu\
Coded by Chang-Yu Huang\
Picture by Wan-Chian Zhang