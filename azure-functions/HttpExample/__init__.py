import logging
import azure.functions as func
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions
from azure.storage.blob import ContainerClient
import gzip 

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    container_name = req.params.get('container_name')
    storage_account_key = req.params.get('storage_account_key')
    account_name = req.params.get('account_name')
    
    blob_service_client_instance = BlobServiceClient(account_url="https://" + account_name + ".blob.core.windows.net", credential=storage_account_key)
    connection_string = "DefaultEndpointsProtocol=https;AccountName=" + account_name + ";AccountKey=" + storage_account_key + ";EndpointSuffix=core.windows.net"
    container = ContainerClient.from_connection_string(conn_str=connection_string, container_name=container_name)

    blob_list = container.list_blobs()
    decompressed_data = None
    for blob in blob_list:
        blob_client_instance = blob_service_client_instance.get_blob_client(
            container_name, blob.name, snapshot=None)
        blob_data = blob_client_instance.download_blob()
        data = blob_data.readall()
        decompressed_data = gzip.decompress(data)

    if container_name and storage_account_key and account_name:
        return func.HttpResponse(f"Hello, {decompressed_data}. This HTTP triggered function executed successfully.")