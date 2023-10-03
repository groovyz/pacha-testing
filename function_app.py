import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import analyze_doc


app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="test/{name}",
                               connection="AzureWebJobsStorage")
 
def prototype_blob_trigger(myblob: func.InputStream):

    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    source = myblob.read()
    results = analyze_doc.get_text_from(source)
    qas = analyze_doc.get_questions_answers_from(results["analyzeResult"]["content"])
    embedded_qas = analyze_doc.get_qa_with_embeddings_from(qas)