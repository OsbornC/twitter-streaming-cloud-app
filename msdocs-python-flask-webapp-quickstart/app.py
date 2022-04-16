from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import requests
import os 
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime
import config
# from flask_cors import CORS, cross_origin

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

app = Flask(__name__)
# CORS(app)

client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
try:
    db = client.create_database(id=DATABASE_ID)
    print('Database with id \'{0}\' created'.format(DATABASE_ID))

except exceptions.CosmosResourceExistsError:
    db = client.get_database_client(DATABASE_ID)
    print('Database with id \'{0}\' was found'.format(DATABASE_ID))

# setup container for this sample
try:
    container = db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
    print('Container with id \'{0}\' created'.format(CONTAINER_ID))

except exceptions.CosmosResourceExistsError:
    container = db.get_container_client(CONTAINER_ID)
    print('Container with id \'{0}\' was found'.format(CONTAINER_ID))


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

@app.route('/test', methods=['GET'])
def test():
    response = jsonify({'some': 'data'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/read', methods=['GET'])
def read_item():
    print('\nReading Item by Id\n')
    doc_id = request.args.get('doc_id')
    account_number = request.args.get('account_number')
    print('1111', doc_id, account_number)
    # We can do an efficient point read lookup on partition key and id
    r = container.read_item(item=doc_id, partition_key=account_number)
    
    print('Item read by Id {0}'.format(doc_id))
    print('Partition Key: {0}'.format(r.get('partitionKey')))
    print('Subtotal: {0}'.format(r.get('subtotal')))
    response = jsonify({'Subtotal': r.get('subtotal')})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
# r = container.read_item(item='SalesOrder1', partition_key='Account1')

# print('1111',r.get('subtotal'))
if __name__ == '__main__':
   app.run()