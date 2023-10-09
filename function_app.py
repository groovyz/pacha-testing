import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import doc_operations
import call_db


app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="test/input-{name}",
                               connection="AzureWebJobsStorage")
 
def prototype_blob_trigger(myblob: func.InputStream):

    logging.info(f"Python blob trigger input documents function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    source = myblob.read()
    results = doc_operations.get_text_from(source)
    qas = doc_operations.get_questions_answers_from(results["analyzeResult"]["content"])
    embedded_qas = doc_operations.get_embeddings_from(qas)
    call_db.insert_into_database(embedded_qas, myblob.uri)



@app.blob_trigger(arg_name="askblob", path="test/ask-{name}",
                               connection="AzureWebJobsStorage") 
def prototype_input_trigger(askblob: func.InputStream):
    logging.info(f"Python blob trigger ask function processed blob"
                f"Name: {askblob.name}"
                f"Blob Size: {askblob.length} bytes")
    asksource = askblob.read()
    askresults = doc_operations.get_text_from(asksource)
    askqs = doc_operations.get_questions_from(askresults["analyzeResult"]["content"])
    embedded_askqs = doc_operations.get_embeddings_from(askqs)
    all_similar_questions = call_db.get_closest_neighbors_of(embedded_askqs)

