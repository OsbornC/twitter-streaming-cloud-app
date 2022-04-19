import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://twitty.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'OiuUSlng1GmnmdnZZZn5g7wF2hX93MxLoaKq5lfVBMrOOU1fx4dq2RhDxn6n3ny7MrEH6LebN9ypCHpTxG1dog=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'IMDB'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'Items'),
}