import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import json
import time
from requests import get, post
import os
import requests
from collections import OrderedDict
import numpy as np
import pandas as pd

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="test/{name}",
                               connection="AzureWebJobsStorage") 
def prototype_blob_trigger(myblob: func.InputStream):
    test_text = myblob.read()
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes"
                f"Blob Content: {test_text}")
