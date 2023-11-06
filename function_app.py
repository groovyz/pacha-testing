import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import doc_operations
import db_operations
import os

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="pilot/past@elvish.ai/{folder}/{name}",
                               connection="AzureWebJobsStorage")
 
def prototype_blob_trigger(myblob: func.InputStream):

    logging.info(f"Python blob trigger past documents function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    #source = myblob.read()
    #results = doc_operations.get_text_from(source)
    #qas = doc_operations.get_questions_answers_from(results["analyzeResult"]["content"])
    #embedded_qas = doc_operations.get_embeddings_from(qas)
    #db_operations.insert_into_database(embedded_qas, myblob.uri)
    
    #send_response_code = doc_operations.send_email_notification(myblob.name, "success", "The Document successfully sent")


@app.blob_trigger(arg_name="askblob", path="pilot/new@elvish.ai/{folder}/{name}",
                               connection="AzureWebJobsStorage") 
def prototype_input_trigger(askblob: func.InputStream):
    logging.info(f"Python blob trigger new documents function processed blob"
                f"Name: {askblob.name}"
                f"Blob Size: {askblob.length} bytes")
    #asksource = askblob.read()
    #askresults = doc_operations.get_text_from(asksource)
    #askqs = doc_operations.get_questions_from(askresults["analyzeResult"]["content"])
    #embedded_askqs = doc_operations.get_embeddings_from(askqs)
    #all_similar = db_operations.get_closest_neighbors_of(embedded_askqs)
    #openai_responses = doc_operations.create_all_responses(all_similar)
    #responses_csv = doc_operations.create_csv(openai_responses)

    # This is the connection to the blob storage, with the Azure Python SDK
    #blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])
    #container_client=blob_service_client.get_container_client("test")

    blob_path_components = f"{askblob.name}".split(os.sep)
    out_path_split = blob_path_components[1:-1]
    out_path_split.append(os.path.splitext(blob_path_components[-1])[0]+"-result.csv")
    out_path_split.insert(0,"pilotout")
    out_path = os.path.join(*out_path_split)
    logging.info(f"{out_path}")
    #container_client.upload_blob(name=out_path,data=responses_csv)


