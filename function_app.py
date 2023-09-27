import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
from requests import get, post
import os
from collections import OrderedDict
import numpy as np
import pandas as pd
from analyze_doc import call_document_intelligence

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="test/{name}",
                               connection="AzureWebJobsStorage")
 
def prototype_blob_trigger(myblob: func.InputStream):
    # This is the call to the Document Intelligence endpoint
    endpoint = os.environ["AzureDocumentIntelEndpoint"]
    apim_key = os.environ["AzureDocumentIntelKey"]
    post_url = endpoint + "/formrecognizer/v2.1/layout/analyze"
    source = myblob.read()
    results = call_document_intelligence(apim_key, post_url, source)
    print(results)

    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
