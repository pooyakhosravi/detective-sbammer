from flask import Flask, request
import requests
import json
app = Flask(__name__)

URL = "https://www.googleapis.com/youtube/v3/commentThreads"

PARAMS = {'key': 'AIzaSyC-jE0nNlKI6lxDLUfZbbewJ2LVBljtRwQ',
            'part':'snippet,replies'}


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


    for item in data['items']:
        result['items'].append(
            {
                'id': item['id'],
                'text' : item['snippet']['topLevelComment']['snippet']['textOriginal'],
                'author': {
                    'name': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    'url': item['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
                    'picture': item['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'],
                }
            })
    

    return json.dumps(result)
