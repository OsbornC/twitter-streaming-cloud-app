import datetime
import logging
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos import exceptions, CosmosClient
import azure.functions as func
import http.client
import json

HOST = 'https://twitty.documents.azure.com:443/'
MASTER_KEY = 'OiuUSlng1GmnmdnZZZn5g7wF2hX93MxLoaKq5lfVBMrOOU1fx4dq2RhDxn6n3ny7MrEH6LebN9ypCHpTxG1dog=='
DATABASE_ID = 'IMDB'
CONTAINER_ID = 'Items'
BOX_OFFICE_ID = 'BOX_OFFICE_TOP_MOVIES'
WHOLE_MOVIE_SET = 'WHOLE_MOVIE_SET'

client = CosmosClient(HOST, MASTER_KEY)

database_name = DATABASE_ID
database = client.create_database_if_not_exists(id=database_name)
container_name = CONTAINER_ID
container = database.create_container_if_not_exists(
    id=container_name, 
    partition_key=PartitionKey(path="/id")
)

db = client.get_database_client(DATABASE_ID)
container = db.get_container_client(CONTAINER_ID)

def upsert_item(container, item, partition_key):
	response = container.upsert_item(body=item)
	# print('Upserted Item\'s Id is {0}'.format(response['id']))

def fetch_box_office_movie_list():
	conn = http.client.HTTPSConnection("imdb-api.com", 443)
	payload = ''
	headers = {}
	conn.request("GET", "/en/API/BoxOffice/k_h00xj2rl", payload, headers)
	res = conn.getresponse()
	data = res.read()
	# print(json.loads(data.decode("utf-8")))
	return json.loads(data.decode("utf-8"))["items"]

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    # if mytimer.past_due:
    #     logging.info('The timer is past due!')

    # logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    items = fetch_box_office_movie_list()
    ls = []
    read_item = container.read_item(item=WHOLE_MOVIE_SET, partition_key=WHOLE_MOVIE_SET)
    movie_set = set(read_item['whole_movie_set'])
    
    for item in items:
        ls.append(item['id'])
        movie_set.add(item['id'])
        upsert_item(container, item, item['id'])
    upsert_item(container, {'id': BOX_OFFICE_ID, 'movie_list': ls}, BOX_OFFICE_ID)
    read_item['whole_movie_set'] = list(movie_set)
    upsert_item(container, read_item, WHOLE_MOVIE_SET)