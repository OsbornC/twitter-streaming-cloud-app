import requests
import os
import json

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAP2kawEAAAAAhs6QRNCBbbcSoJcHvvm1prTzMJU%3Dv6VUrcnCTQP0ufh0Lqf5nUFU4Kv2NWwwYobAl20BJUzfVKj2pg'

import asyncio
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "(#morbius OR #MORBIUS) lang:en has:media -is:retweet -is:reply -is:quote", "tag": "morbius"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,
    )
    res = []
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    count = 0
    for response_line in response.iter_lines():
        count += 1
        if response_line:
            json_response = json.loads(response_line)
            line = json.dumps(json_response, indent=4, sort_keys=True)
            print(line)
            res.append(line)
        if count == 3:
            return res
    return res

async def run(data):
    # Create a producer client to send messages to the event hub.
    # Specify a connection string to your event hubs namespace and
    # the event hub name.
    producer = EventHubProducerClient.from_connection_string(conn_str="Endpoint=sb://cloudgroupfiveeventhub.servicebus.windows.net/;SharedAccessKeyName=socialtwitter-access;SharedAccessKey=sZ+LjllXmwAiI0XMm/2myfbajcBWQjgPegKKh+RW0do=;EntityPath=socialtwitter-eh", eventhub_name="socialtwitter-eh")
    async with producer:
        # Create a batch.
        event_data_batch = await producer.create_batch()

        # Add events to the batch.
        for d in data:
            event_data_batch.add(EventData(d))
        # Send the batch of events to the event hub.
        await producer.send_batch(event_data_batch)

def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    res = get_stream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(res))

if __name__ == "__main__":
    main()