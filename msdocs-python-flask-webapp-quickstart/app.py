from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import requests
import os 

app = Flask(__name__)


@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')
   response = requests.get('https://cloud-computing-twitter-function-app.azurewebsites.net//api/HttpExample?name=%s' % name)
   greeting = response.text
   
   if name:
       print('Request for hello page received with greeting=%s' % greeting)
       return render_template('hello.html', greeting = greeting)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()