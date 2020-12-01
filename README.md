#  📺 The Simpsons API 💻
![](https://lh3.googleusercontent.com/1Y9DV2zJMsR9DOclgisI-NtGJbVBMq9dui7ecnpJsZwyllOoJh-PhTPweWb0yXq5m6szzhrdRg=w640-h400-e365-rj-sc0x00ffffff)


I have created the Simpsons API [from this Kaggle dataset named 'Dialogue lines of the Simpsons'](https://www.kaggle.com/pierremegret/dialogue-lines-of-the-simpsons). 

I created an API which let us fill our [Mongo DB](https://www.mongodb.com/es) database with POST queries.

In this Mongo database we have three collections:
- *Characters*: with the characters of the TV series.
- *Messages*: this collection has every message written by every character with the message, the chat where it has been written and the participant of the chat who wrote it.
- *Chats*: this collection contains all the chat-groups of the Springfield Characters with the participants of each one.


## How does it work?

### POST queries

*/new/user*\
With this POST query we can insert characters in the database through a request (after checking that the character doesn't exist already in the database).

```
url_char = "http://localhost:5000/new/character"
requests.post(url_char, data=newcharacter)
```

*/new/chat*\
We can insert new chats following the steps we followed with the preovious new/user endpoint.
```
simpsons_family = {"chat_name": "family",
           "participants": ["Marge Simpson","Homer Simpson","Lisa Simpson","Bart Simpson", "Maggie Simpson"]
}
```

*/new/message*
To insert a message in the database as follows:
````
url_message = "http://localhost:5000/new/message"
requests.post(url_message, data='thenewmessage')
````

### GET queries

*/characters/all*\
With this endpoint we can get all the characters from the character collection.

````
http://127.0.0.1:5000/characters/all
````
With the previous url and changing its end after 
````http://127.0.0.1:5000/````
We can obtain different kinds of information from the API:
- /messages/all : all the messages from the messages collection.
- /chats/all : all the chats from the chats collection.
- /characters/chat/<name>' : returns the chats where the character introduced participates and the participants.
- /messages/<name> : returns the messages of the character introduced.

Con requests a la API podemos analizar los sentimientos de los mensajes que se han escrito en un chat, los sentimientos de una frase random de un usuario o de todos los mensajes de un usuario para saber si se expresa feliz o triste.


- /messages/nlp/participant/<name> : returns the nlp metrics specified in the functions documentation of the messages of the character introduced.
- /messages/nlp/chat/<chat_name> : returns the nlp metrics specified in the functions documentation of the messages of the chat_name introduced.

NLP metrics (using [TextBlob](https://textblob.readthedocs.io/en/dev/) library):
- Polarity: Polarity is float which lies in the range of [-1,1] where 1 means positive statement and -1 means a negative statement. 
- Sentiments: Subjective sentences generally refer to personal opinion, emotion or judgment whereas objective refers to factual information. Subjectivity is also a float which lies in the range of [0,1].
