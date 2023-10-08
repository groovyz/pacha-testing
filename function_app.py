import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import analyze_doc
import insert_to_db


app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="test/input-{name}",
                               connection="AzureWebJobsStorage")
 
def prototype_blob_trigger(myblob: func.InputStream):

    logging.info(f"Python blob trigger input documents function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    source = myblob.read()
    results = analyze_doc.get_text_from(source)
    qas = analyze_doc.get_questions_answers_from(results["analyzeResult"]["content"])
    embedded_qas = analyze_doc.get_qa_with_embeddings_from(qas)
    insert_to_db.insert_into_database(embedded_qas, myblob.uri)



@app.blob_trigger(arg_name="askblob", path="test/ask-{name}",
                               connection="AzureWebJobsStorage") 
def prototype_input_trigger(askblob: func.InputStream):
    logging.info(f"Python blob trigger ask function processed blob"
                f"Name: {askblob.name}"
                f"Blob Size: {askblob.length} bytes")
