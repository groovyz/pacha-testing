import requests
import time
import json
import openai
import os
import pandas as pd
import logging
import traceback

def get_text_from(document):
    # This is a call to the document intelligence endpoint

    endpoint = os.environ["AzureDocumentIntelEndpoint"]
    apim_key = os.environ["AzureDocumentIntelKey"]
    post_url = endpoint + "/formrecognizer/documentModels/prebuilt-read:analyze?api-version=2023-07-31"
    headers = {
    # Request headers
    'Content-Type': 'application/pdf',
    'Ocp-Apim-Subscription-Key': apim_key,
        }
    resp = requests.post(url=post_url, data=document, headers=headers)

    if resp.status_code != 202:
        logging.info(f"POST analyze failed:\n{resp.text}")
        quit()
    logging.info(f"POST analyze succeeded:\n{resp.headers}")
    get_url = resp.headers["operation-location"]

    wait_sec = 25

    time.sleep(wait_sec)
    # The layout API is async therefore the wait statement

    resp = requests.get(url=get_url, headers={"Ocp-Apim-Subscription-Key": apim_key})

    resp_json = json.loads(resp.text)

    status = resp_json["status"]

    if status == "succeeded":
        logging.info("POST Layout Analysis succeeded:\n")
        results = resp_json
    else:
        logging.info(f"GET Layout results failed:\n {status}")
        quit()
        
    results = resp_json

    return results

def get_questions_answers_from(text):
    # This is a call to an OpenAI Function Call
    openai.api_type = "azure"
    openai.api_base = os.environ["AzureOpenAIEndpoint"]
    openai.api_version = "2023-07-01-preview"
    openai.api_key = os.environ["AzureOpenAIKey"]

    messages= [{"role": "system", "content": "You're an assistant that extracts questions and answers. Only use the functions you have been provided with."},
        {"role": "user", "content": f"Get questions and answers from {text}"}]
    functions = [
        {
            "name": "get_questions_and_answers",
            "description": "Identify and retrieve question and answer pairs from the string blob provided.",
            "parameters": {
                "type" : "object",
                "properties": {
                    "questions_and_answers":{
                        "type" : "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question":{
                                    "type": "string",
                                    "description": "A question identified from a string blob"
                                },
                                "answer": {
                                    "type": "string",
                                    "description": "The answer corresponding to the question identified from the string blob"
                                }
                            }
                        }
                    }           
                },
                "required": ["questions_and_answers"]
            }
        }
    ]
    try:
        response = openai.ChatCompletion.create(
        engine="pacha-gpt4",
        messages=messages,
        functions=functions,
        temperature=0,
        function_call={"name": "get_questions_and_answers"},  
        )
    except Exception as e:
        logging.info(f"OPENAI CALL FOR EXTRACTING Q & A FAILED: \n {e} \n")
        logging.error(traceback.format_exc())
        quit()

    if isinstance(response, dict):
        resp_text = response["choices"][0]["message"]
        qaobject = json.loads(resp_text["function_call"]["arguments"])
        allqas = qaobject["questions_and_answers"]
        if len(allqas) != 0:
            logging.info("GET questions and answers from document succeeded\n")
        return allqas
    else:
        logging.info(f"GET questions and answers from document failed:\n OPENAI DID NOT RETURN A DICTIONARY - RESPONSE IS {response}")
        quit()

def get_questions_from(text):
    # This is a call to an OpenAI Function Call
    openai.api_type = "azure"
    openai.api_base = os.environ["AzureOpenAIEndpoint"]
    openai.api_version = "2023-07-01-preview"
    openai.api_key = os.environ["AzureOpenAIKey"]

    messages= [{"role": "system", "content": "You're an assistant that extracts questions. Only use the functions you have been provided with."},
        {"role": "user", "content": f"Identify and retrieve questions from {text}"}]
    functions = [
        {
            "name": "get_questions",
            "description": "Identify and retrieve questions from the string blob provided.",
            "parameters": {
                "type" : "object",
                "properties": {
                    "questions":{
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question":{
                                    "type": "string",
                                    "description": "A question identified from a string blob"
                                }
                            }
                        }
                    }           
                },
                "required": ["questions"]
            }
        }
    ]
    try:
        response = openai.ChatCompletion.create(
        engine="pacha-gpt4",
        messages=messages,
        functions=functions,
        temperature=0,
        function_call={"name": "get_questions"},  
        )
    except Exception as e:
        logging.info(f"OPENAI CALL FOR EXTRACTING QUESTIONS FAILED: \n {e} \n")
        logging.error(traceback.format_exc())
        quit()
        
    if isinstance(response, dict):
        resp_text = response["choices"][0]["message"]
        qobject = json.loads(resp_text["function_call"]["arguments"])
        allqs = qobject["questions"]
        if len(allqs) != 0:
            logging.info("GET questions from document succeeded:\n")
        return allqs
    else:
        logging.info("GET questions from document failed:\n")
        quit()

def get_embedding(text, model="pacha-embed"):
    text = text.replace("\n", " ")
    try:
        response = openai.Embedding.create(input = [text], engine=model)
    except Exception as e:
        logging.info(f"OPENAI CALL TO GET EMBEDDING INSTANCE FAILED: \n {e} \n")
        logging.error(traceback.format_exc())
        quit()

    if isinstance(response, dict):
        return response['data'][0]['embedding']
    else:
        logging.info(f"GET embedding instance \n {text} \n failed - NOT A DICTIONARY\n")
        quit()

def get_embeddings_from(objects):
    embedded= []
    for o in objects:
        q_embed = get_embedding(o.get("question"))
        new_dict = {**o, **{'embedding': q_embed}}
        embedded.append(new_dict)
    logging.info(f"ALL EMBEDDINGS PROCESSED")
    return embedded

def get_openai_response_to(similar_obj):
    openai.api_type = "azure"
    openai.api_base = os.environ["AzureOpenAIEndpoint"]
    openai.api_version = "2023-07-01-preview"
    openai.api_key = os.environ["AzureOpenAIKey"]

    context = "\n".join(similar_obj["similar-answers"])
    question = similar_obj["question"]

    messages= [{"role": "system", "content": "You're a consultant who specializes in crafting responses to RFP (Request for Proposal) questions when given a context. If the context is not enough, return an empty string. Only use the functions you have been provided with."},
        {"role": "user", "content": f"Here is the context: \n\n {context} \n Using the context, help me craft an answer to {question}"}]
    
    functions = [
        {
            "name": "craft_response",
            "description": "Craft a response a particular to RFP (Request for Proposal) question when given a context. If the context is not enough, return an empty string.",
            "parameters": {
                "type" : "object",
                "properties": {
                    "question_response" : {
                        "type": "string",
                        "description": "The written response to the question provided with the context"
                    }        
                },
                "required": ["questions_response"]
            }
        }
    ]
    try:
        response = openai.ChatCompletion.create(
        engine="pacha-gpt4",
        messages=messages,
        functions=functions,
        temperature=0,
        function_call={"name": "craft_response"},  
        )
    except Exception as e:
        logging.info(f"OPENAI CALL FOR CREATING RESPONSES FAILED ERROR: \n {e} \n")
        logging.error(traceback.format_exc())
        quit()

    if isinstance(response, dict):
        resp_text = response["choices"][0]["message"]
        q_response = json.loads(resp_text["function_call"]["arguments"])
        return q_response

def create_all_responses(similar_objs):
    raw_responses = []
    for obj in similar_objs:
        response = get_openai_response_to(obj)
        if isinstance(response, dict):
            new_dict = {**obj, **response}
        else:
            new_dict = {**obj, **{'question_response': ''}}
        raw_responses.append(new_dict)
    logging.info("RAW RESPONSES SUCCESSFULLY CREATED")
    return raw_responses

def create_csv(responses):
    responses_df = pd.DataFrame(responses)
    responses_csv = responses_df.to_csv(index=False,mode="w")
    logging.info("CSV SUCCESSFULLY CREATED")
    return responses_csv

def send_email_notification(blob_name, msg):
    s = requests.session()
    s.headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    url = os.environ["EmailEndpoint"]
    https = s.post(url, json={"email": blob_name, "status": msg})
    return https.status_code