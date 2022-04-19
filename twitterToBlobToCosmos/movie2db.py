import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

import os, uuid
import datetime
import json
import config
import requests


HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


BLOB_AZURE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=twittertoblob;AccountKey=NznNDxkhrcwSVo3h2Z768SXq2eYgAROk+t2aIafIJZa10TFxMI2mSpXTJ0o4mtJ7t0L2hfc2sSuT+AStDo/NgQ==;EndpointSuffix=core.windows.net"
BLOB_CONTAINER_NAME = str("tweets")

BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAP2kawEAAAAAhs6QRNCBbbcSoJcHvvm1prTzMJU%3Dv6VUrcnCTQP0ufh0Lqf5nUFU4Kv2NWwwYobAl20BJUzfVKj2pg'

SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

def upsert_item(container, doc_id, account_number):
    print('\nUpserting an item\n')
    print('\nParameters Here:\n', doc_id, '\t', account_number)
    read_item = container.read_item(item=doc_id, partition_key=account_number)
    print("object_got:", read_item)
    response = container.upsert_item(body=read_item)

    print('Upserted Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))

def upload_cosmosdb_tweets(file_name, movie_id):
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        # setup database for this sample
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
        
        movie_kv = {'id': movie_id, 'partitionKey': movie_id, 'movie_name': 'Fantastic Beasts: The Secrets of Dumbledore', 'tweet_ids':[]}
        tweets_json = {}
        with open(file_name) as json_file:
            tweets_json = json.load(json_file)
        tweets_list = tweets_json['data']
        tweets_dist = {}
        for tweet in tweets_list:
            tweet_id = tweet['id']
            movie_kv['tweet_ids'].append(tweet_id)
            item_id = movie_id + 'tweet'+ tweet['id']
            tweet['id'] = item_id
            tweet['partitionKey']= movie_id
            tweets_dist[item_id] = tweet

            response = container.upsert_item(body=tweet)
            print('\nUpserted tweet\'s Id is {0}, \n new text={1}'.format(response['id'], response['text']))

        response = container.upsert_item(body=movie_kv)
        print('\nUpserted tweet\'s Id is {0}, \n new text={1}'.format(response['id'], response['movie_name']))

        with open('movie.json', 'w') as f:
            json.dump(movie_kv, f, sort_keys= True)
        with open('tweets.json', 'w') as f:
            json.dump(tweets_dist, f, sort_keys=True)
            
    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
            print("\nrun_sample done")


def upload_blob(file_name):
    data = []
    with open(file_name) as json_file:
            data = json.load(json_file)
    # connecting to Azure Storage
    
    blob_name = file_name #"tweets-fantasticbeasts.json"
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_AZURE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=blob_name)

    # upload json to Azure Storage
    blob_client.upload_blob(json.dumps(data))

def download_blob(file_name):
    # connecting to Azure Storage
    
    blob_name = file_name #"tweets-fantasticbeasts.json"
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_AZURE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=blob_name)

    # upload json to Azure Storage
    data = json.loads(blob_client.download_blob().readall())
    #print(data)
    with open('tmp.json', 'w') as f:
        json.dump(data, f, sort_keys=True)


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def tweets_request(file_name, query_params):
    json_response = connect_to_endpoint(SEARCH_URL, query_params)
    # tweets = json.dumps(json_response, sort_keys=True)
    with open(file_name, 'w') as f:
        json.dump(json_response, f, sort_keys=True)
    

if __name__ == '__main__':
    tweets_file_name = "tweets-fantasticbeasts.json"
    
    # query_params = {'query': "(#FantasticBeasts OR #SecretsOfDumbledore) lang:en has:media -is:retweet -is:reply -is:quote", 'max_results':10, 'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld', 'expansions':'author_id','user.fields':'description'}

    # # request tweets from TwitterAPI
    # tweets_request(tweets_file_name, query_params)
    
    # # upload to blob storage 
    # upload_blob(tweets_file_name)

    # # ------- Analysis and sentiment analysis
    # download_blob(tweets_file_name)
    # # ....

    # ------- Dump results to cosmosDB
    upload_cosmosdb_tweets(tweets_file_name, 'tt4123432')

    
    
