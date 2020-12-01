from flask import Flask, request, Response
import markdown.extensions.fenced_code
import random
from config.configuration import db, messages_coll
import json
from bson.json_util import dumps

app = Flask(__name__)

#------------------ POST ENDPOINTS -----------------------

@app.route("/")
def index():
    readme_file = open("README.md","r")
    md_template_string = markdown.markdown(readme_file.read(), extensions = ["fenced_code"])
    return md_template_string

@app.route('/new/character',methods=['POST'])
def addingChars():
    """
    Checks if a character already exists in our database before creating it.
    """
    name = request.form.get('name')
    if db.characters.find_one({'name': name}):
        data = dumps({"Error": "The character already exists"})
        return Response(data, status=409, mimetype='application/json')
    data = dumps(db.characters.insert_one({'name': name}).inserted_id)
    return Response(data, status=204, mimetype='application/json')

@app.route('/new/chat',methods=['POST'])
def addingChats():
    """
    Checks if a chat already exists in our database before creating it.
    """
    name = request.form.get('chat_name')
    participants = request.form.getlist('participants')
    if db.chats.find_one({'chat_name': name}):
        data = dumps({"Error": "The chat already exists"})
        return Response(data, status=409, mimetype='application/json')
    all_participants_exist = True
    for p in participants:
        if not db.characters.find_one({'name': p}):
            all_participants_exist = False
    
    if all_participants_exist:
            data = dumps(db.chats.insert_one({'chat_name': name, 'participants': participants}).inserted_id)
    else:
        error = 'At least one participant is not in our characters collection, please make sure you have introduced all.'
        raise ValueError (error)
    return Response(data, status=204, mimetype='application/json')


@app.route('/new/message',methods=['POST'])
def addingMessages():
    """
    Creates a message with the participant_name of whom writes it and the chat_name where
    it is written in our database.
    """
    name = request.form.get('name')
    messages = request.form.getlist('messages')
    if not db.characters.find_one({'name': name}):
        error = "Please, make sure this character exists in our database"
        raise ValueError (error)
    messages_json = []
    chats_list = list(db.chats.find({'participants': name }))
    print(chats_list)
    for c in chats_list:
        chat_name = c['chat_name']
        for m in messages:
            db.messages.insert_one({'chat_name': chat_name, 'participant_name': name, 'message': m})
    return Response(None, status=204, mimetype='application/json')

@app.route('/new/message/nlp',methods=['POST'])
def addingNLP():
    """
    This function adds the nlp polarity and sentiments parameters to each message
    so we can ask the Simpsons API for the mean of a user's messages or a chat's messages
    optimizing the time of the answer.
    """
    message = request.json['message']
    polarity = request.json['polarity']
    sentiment = request.json['sentiment']
    mess_lst = list(db.messages.find({'message': message }))
    for mess in mess_lst:
        db.messages.update({"_id": mess["_id"]}, {"$set": {"sentiment": sentiment, "polarity": polarity}})
    return Response(None, status=204, mimetype='application/json')
        


#------------------ GET ENDPOINTS -----------------------

@app.route("/characters/all")
def allChars():
    """
    This function let you obtain the name of all the characters of the characters collection.
    """
    cursor=db.characters.find({}, {'_id': 0, 'name': 1})
    data = dumps(cursor)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route("/messages/all")
def allMessages():
    """
    This function let you obtain all the messages of the messages collection.
    """
    cursor=db.messages.find({}, {'_id': 0,'chat_name':0, 'participant_name':0,  'message': 1, 'polarity':1, 'sentimen':1})
    data = dumps(cursor)
    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route("/chats/all")
def chats():
    """
    This function let you obtain all the chats of the chats collection with the participants of each one.
    """
    chats = dumps(db.chats.find({}, {'_id': 0,'chat_name':1, 'participants':1}))
    return chats

@app.route('/characters/chat/<name>')
def chatUser(name):
    """
    This function returns the chats where the character introduced participates and the participants.
    """
    res = dumps(db.chats.find({'participants': name}, {'_id': 0,'chat_name':1, 'participants':1}))
    if len(res) == 0:
        error = "Please, make sure this character exists in this chat."
        raise ValueError (error)
    else:
       return res

@app.route('/messages/<name>')
def messagesUser(name):
    """
    This function returns all the messages written by the indicated character.
    """
    res = dumps(db.messages.find({'participant_name': name}, {'_id': 0,'participant_name':1, 'chat_name':1, 'message':1, 'polarity': 1, 'sentiment':1}))
    if len(res) == 0:
        error = "Please, make sure this character exists in this chat."
        raise ValueError (error)
    else:
       return res

@app.route('/messages/nlp/participant/<name>')
def messages_nlp(name):
    """
    This function let us obtain the nlp (sentiment and polarity) metrics (represented by the mean of each one)
    of all the messages written by the indicated character.
    """
    if not db.characters.find_one({'name': name}):
        error = "Please, make sure this character exists in our database"
        raise ValueError (error)
    message_lst_participant = list(db.messages.find({'participant_name': name, 'polarity': {"$exists": True}, 'sentiment': {"$exists": True}}, {'_id': 0,'participant_name':1, 'chat_name':1, 'polarity': 1, 'sentiment': 1}))

    polarity_neg = []
    polarity_neu = []
    polarity_pos = []

    sentiment_polarity = []
    sentiment_subjectivity = []

    for message in message_lst_participant:
        polarity = message['polarity']
        polarity_neg.append(polarity['neg'])
        polarity_neu.append(polarity['neu'])
        polarity_pos.append(polarity['pos'])

        sentiment = message['sentiment']
        sentiment_polarity.append(sentiment['polarity'])
        sentiment_subjectivity.append(sentiment['subjectivity'])

    mean_dict = {}
    if len(polarity_neg)>0 and len(polarity_neu)>0 and len(polarity_pos)>0 and len(sentiment_polarity)>0 and len(sentiment_subjectivity)>0:
        mean_dict = {
            'polarity': {
                'neg_mean': sum(polarity_neg) / len(polarity_neg),
                'neu_mean': sum(polarity_neu) / len(polarity_neu),
                'pos_mean': sum(polarity_pos) / len(polarity_pos)
            },
            'sentiment': {
                'polarity_mean': sum(sentiment_polarity) / len(sentiment_polarity),
                'subjectivity_mean': sum(sentiment_subjectivity) / len(sentiment_subjectivity)
            }
        }
    
    return dumps(mean_dict)



@app.route('/messages/nlp/chat/<chat_name>')
def messages_nlp_chat(chat_name):
    """
    This function let us obtain the nlp (sentiment and polarity) metrics (represented by the mean of each one)
    of all the messages written inside the indicated chat.
    """
    if not db.messages.find_one({'chat_name': chat_name}):
        error = "Please, make sure this chat exists in our database"
        raise ValueError (error)
    message_lst_chat = list(db.messages.find({'chat_name': chat_name, 'polarity': {"$exists": True}, 'sentiment': {"$exists": True}}, {'_id': 0,'participant_name':1, 'chat_name':1, 'polarity': 1, 'sentiment': 1}))

    polarity_neg = []
    polarity_neu = []
    polarity_pos = []

    sentiment_polarity = []
    sentiment_subjectivity = []

    for message in message_lst_chat:
        polarity = message['polarity']
        polarity_neg.append(polarity['neg'])
        polarity_neu.append(polarity['neu'])
        polarity_pos.append(polarity['pos'])

        sentiment = message['sentiment']
        sentiment_polarity.append(sentiment['polarity'])
        sentiment_subjectivity.append(sentiment['subjectivity'])

    mean_dict = {}
    if len(polarity_neg)>0 and len(polarity_neu)>0 and len(polarity_pos)>0 and len(sentiment_polarity)>0 and len(sentiment_subjectivity)>0:
        mean_dict = {
            'polarity': {
                'neg_mean': sum(polarity_neg) / len(polarity_neg),
                'neu_mean': sum(polarity_neu) / len(polarity_neu),
                'pos_mean': sum(polarity_pos) / len(polarity_pos)
            },
            'sentiment': {
                'polarity_mean': sum(sentiment_polarity) / len(sentiment_polarity),
                'subjectivity_mean': sum(sentiment_subjectivity) / len(sentiment_subjectivity)
            }
        }
    
    return dumps(mean_dict)





app.run(debug=True)







