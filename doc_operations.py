import requests
import time
import json
#import openai
from openai import OpenAI
import os
import pandas as pd
import logging
import traceback
import time

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
    time.sleep(30)
    client = OpenAI()
    # This is a call to an OpenAI Function Call
    #openai.api_type = "azure"
    #openai.api_base = os.environ["AzureOpenAIEndpoint"]
    #openai.api_version = "2023-07-01-preview"
    #openai.api_key = os.environ["AzureOpenAIKey"]

    messages= [{"role": "system", "content": "You're an assistant that extracts questions and answers. Only use the functions you have been provided. Extract the entirety of questions and answers, do not truncate."},
        {"role": "user", "content": f"Get all questions and answers from {text}"}]
    tools = [
        {
            "type": "function",
            "function": {"name": "get_questions_and_answers",
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
        }
    ]
    try:
        #print(text)
        response = client.chat.completions.create(
        model="gpt-4",
        messages=messages, # type: ignore
        tools=tools, # type: ignore
        tool_choice= {"type": "function", "function": {"name": "get_questions_and_answers"}},  
        )
    except Exception as e:
        logging.info(f"OPENAI CALL FOR EXTRACTING Q & A FAILED: \n {e} \n")
        logging.error(traceback.format_exc())
        quit()
    
    resp_text = response.choices[0].message
    if resp_text.tool_calls is not None:
        qaobject = json.loads(resp_text.tool_calls[0].function.arguments)
        allqas = qaobject.get("questions_and_answers")
        if len(allqas) != 0:
            logging.info("GET questions and answers from document succeeded\n")
        #print(allqas)
        return allqas
    else:
        logging.info(f"GET questions and answers from document failed:\n OPENAI DID NOT RETURN A DICTIONARY - RESPONSE IS {response}")
        quit()

def get_questions_from(text):
    # This is a call to an OpenAI Function Call
    client = OpenAI()
    #openai.api_type = "azure"
    #openai.api_base = os.environ["AzureOpenAIEndpoint"]
    #openai.api_version = "2023-07-01-preview"
    #openai.api_key = os.environ["AzureOpenAIKey"]

    messages= [{"role": "system", "content": "You're an assistant that extracts questions. Only use the functions you have been provided with."},
        {"role": "user", "content": f"Identify and retrieve questions from {text}"}]
    
    tools = [
        {
            "type": "function",
            "function": {
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
        }
    ]
    try:
        response = client.chat.completions.create(
        model="gpt-4",
        messages=messages, # type: ignore
        tools=tools, # type: ignore
        tool_choice= {"type": "function", "function": {"name": "get_questions"}},  
        )
    except Exception as e:
        logging.info(f"OPENAI CALL FOR EXTRACTING QUESTIONS FAILED: \n {e} \n")
        logging.error(traceback.format_exc())
        quit()
    
    resp_text = response.choices[0].message
    if resp_text.tool_calls is not None:
        qaobject = json.loads(resp_text.tool_calls[0].function.arguments)
        #print(qaobject)
        #print(type(qaobject))
        allqs = qaobject.get("questions")
        if len(allqs) != 0:
            logging.info("GET questions from document succeeded:\n")
        return allqs
    else:
        logging.info(f"GET questions from document failed:\n OPENAI DID NOT RETURN A DICTIONARY - RESPONSE IS {response}")
        quit()

def get_embedding(text, client, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    try:
        time.sleep(0.2)
        response = client.embeddings.create(input = [text], model=model)
    except Exception as e:
        logging.info(f"OPENAI CALL TO GET EMBEDDING INSTANCE FAILED: \n {e} \n")
        logging.error(traceback.format_exc())
        response = None

    if response is not None:
        return response.data[0].embedding
    else:
        return []

def get_embeddings_from(objects):
    client = OpenAI()
    embedded= []
    for o in objects:
        q_embed = get_embedding(o.get("question"), client)
        if len(q_embed) != 0:
            new_dict = {**o, **{'embedding': q_embed}}
            embedded.append(new_dict)
    logging.info(f"ALL EMBEDDINGS PROCESSED")
    return embedded

def get_openai_response_to(context, question):
    time.sleep(1)
    client = OpenAI()
    #openai.api_type = "azure"
    #openai.api_base = os.environ["AzureOpenAIEndpoint"]
    #openai.api_version = "2023-07-01-preview"
    #openai.api_key = os.environ["AzureOpenAIKey"]

    messages= [{"role": "system", "content": "You're a consultant who specializes in crafting responses to RFP (Request for Proposal) questions when given a context. If the context is not enough, return an empty string. Only use the functions you have been provided with."},
        {"role": "user", "content": f"Here is the context: \n\n {context} \n Using the context, help me craft an answer to {question}"}]
    
    
    tools = [
        {
            "type": "function",
            "function": {
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
        }
    ]
    try:
        response = client.chat.completions.create(
        model="gpt-4",
        messages=messages, # type: ignore
        tools=tools, # type: ignore
        tool_choice= {"type": "function", "function": {"name": "craft_response"}},  
        )
    except Exception as e:
        logging.info(f"OPENAI CALL FOR CREATING RESPONSES FAILED ERROR: \n {e} \n")
        logging.error(traceback.format_exc())
        response = None
 
    resp_text = response.choices[0].message # type: ignore
    q_response = json.loads(resp_text.tool_calls[0].function.arguments, strict=False) # type: ignore
    return q_response

def create_all_responses(similar_objs):
    raw_responses = []
    for obj in similar_objs:
        context = "\n".join(obj["similar-answers"])
        question = obj["question"]
        response = get_openai_response_to(context, question)
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

def send_email_notification(blob_name, status, msg):
    s = requests.session()
    s.headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    url = os.environ["NotificationEndpoint"]
    https = s.post(url, json={"email": blob_name, "status": status, "message": msg})
    return https

def format_output_path(blob_path_components):
    out_path_split = blob_path_components[1:-1]
    out_path_split.append(os.path.splitext(blob_path_components[-1])[0]+"-result.csv")
    #out_path_split.insert(0,"pilotout")
    #out_path = os.path.join(*out_path_split)
    out_path = "-".join(out_path_split)
    return out_path