from flask import Flask, request, render_template
import json

app = Flask(__name__, template_folder='.')

@app.route('/api/stress', methods=['GET', 'POST'])
def stress():
    payload = request.get_json()
    text = payload['text'] if payload else ''
    return json.dumps({'stressed-text': text}), 200, {'ContentType':'application/json'} 

@app.route('/')
def index():
    return render_template('index.html')
