from flask import Flask, request
import requests
import json
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import pickle


model = load_model('my_model.h5')


#Tokenizing
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)




app = Flask(__name__)

URL = "https://www.googleapis.com/youtube/v3/commentThreads"

PARAMS = {'key': 'AIzaSyC-jE0nNlKI6lxDLUfZbbewJ2LVBljtRwQ',
            'part':'snippet,replies',
            'maxResults': 100
        }


@app.route("/")
def index():
    return 'index'



@app.route("/comments/<videoId>")
def hello(videoId):
    myParams = PARAMS.copy()
    myParams['videoId'] = videoId

    if request.form.get("next"):
        print(request.form.get("next"))
        myParams['pageToken'] = request.form.get("next")

    r = requests.get(url = URL, params=myParams)
    
    data = r.json()
    result = {}
    result['items'] = []
    result['nextPage'] = data['nextPageToken']
    spamWords = {}


    for item in data['items']:

        # word1 = ["I respect you ...I am a respectable person who loves you. The world is changing a lot and your wallet is empty.So I make money by watching advertisements.The revenue you earn from advertising is about $ 5,000 a month.Start from now on and stayLive happily.Subscription address https:/"]
        word1 = [item['snippet']['topLevelComment']['snippet']['textOriginal']]
        word1_input = pad_sequences(tokenizer.texts_to_sequences(word1),maxlen = 500)
        reveresed_word_map = dict(map(reversed, tokenizer.word_index.items()))
        word_pred = model.predict_classes(word1_input)
        word_proba = model.predict_proba(word1_input)

        for word in word1_input[0]:
            if word == 0:
                continue
            if reveresed_word_map[word] in spamWords:
                spamWords[reveresed_word_map[word]] = spamWords[reveresed_word_map[word]] + 1
            else:
                spamWords[reveresed_word_map[word]] = 1

        result['wordcloud'] = spamWords

        result['items'].append(
            {
                'id': item['id'],
                'spam': int(word_pred[0][0]),
                'spamprob' : float(word_proba[0][0]),
                'text' : item['snippet']['topLevelComment']['snippet']['textOriginal'],
                'author': {
                    'name': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    'url': item['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
                    'picture': item['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'],
                }
            })
    

    return json.dumps(result)
