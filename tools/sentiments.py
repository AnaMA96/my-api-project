def sentimentAnalysis(sentence):
    sia = SentimentIntensityAnalyzer()
    polarity = sia.polarity_scores(sentence)
    pol = polarity['compound']
    return pol


def sentimentsAndPolarity(message):
    polarity_and_sentiment_mess = []
    for mess in mess_lst:
        blob = TextBlob(mess)
        polarity_and_sentiment_mess.append({'message': mess,
                                           'sentiment': {'polarity': blob.sentiment.polarity, 
                                                        'subjectivity': blob.sentiment.subjectivity}, 
                                           'polarity':sia.polarity_scores(mess)})
    return polarity_and_sentiment_mess