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
    path_components = f"{myblob.name}".split(os.sep)
    email = path_components[2]
    file_name = path_components[-1]
    try:
        source = myblob.read()
        results = doc_operations.get_text_from(source)
        qas = doc_operations.get_questions_answers_from(results["analyzeResult"]["content"])
        embedded_qas = doc_operations.get_embeddings_from(qas)
        db_operations.insert_into_database(embedded_qas, myblob.uri)
        
        final_response = doc_operations.send_email_notification(email, "success", f"{file_name} was successfully loaded into the Elvish Database")
        logging.info("FUNCTION SUCCEEDED")
    except Exception as e:
        final_response = doc_operations.send_email_notification(email, "failure", f"{file_name} failed to load into the Elvish Database, error was {str(e)} <br><br> Please contact Elvish support at sb@offgroove.com or zhao@offgroove.com")
        logging.info(f"FUNCTION FAILED, ERROR: {str(e)}")
        


@app.blob_trigger(arg_name="askblob", path="pilot/new@elvish.ai/{folder}/{name}",
                               connection="AzureWebJobsStorage") 
def prototype_input_trigger(askblob: func.InputStream):
    logging.info(f"Python blob trigger new documents function processed blob"
                f"Name: {askblob.name}"
                f"Blob Size: {askblob.length} bytes")
    path_components = f"{askblob.name}".split(os.sep)
    email = path_components[2]
    file_name = path_components[-1]
    try:
        asksource = askblob.read()
        askresults = doc_operations.get_text_from(asksource)
        askqs = doc_operations.get_questions_from(askresults["analyzeResult"]["content"])
        embedded_askqs = doc_operations.get_embeddings_from(askqs)
        all_similar = db_operations.get_closest_neighbors_of(embedded_askqs)
        openai_responses = doc_operations.create_all_responses(all_similar)
        responses_csv = doc_operations.create_csv(openai_responses)

        # This is the connection to the blob storage, with the Azure Python SDK
        blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])
        container_client=blob_service_client.get_container_client("pilotout")

        out_path = doc_operations.format_output_path(path_components)
        container_client.upload_blob(name=out_path,data=responses_csv)
    except Exception as e:
        logging.info(f"FAILURE, ERROR WAS {str(e)}")
        doc_operations.send_email_notification(email, "failure", f"{file_name} failed to retrieve answers, error was {str(e)} <br><br> Please contact Elvish support at sb@offgroove.com or zhao@offgroove.com")
