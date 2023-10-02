import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
from requests import get, post
import os
from collections import OrderedDict
import numpy as np
import pandas as pd
from analyze_doc import get_text_from, get_questions_answers_from


app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="test/{name}",
                               connection="AzureWebJobsStorage")
 
def prototype_blob_trigger(myblob: func.InputStream):

    source = myblob.read()
    results = get_text_from(source)
    get_questions_answers_from(results["analyzeResult"]["content"])

    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
