import requests
import time
import json
import openai
import os

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
        print("POST analyze failed:\n%s" % resp.text)
        quit()
    print("POST analyze succeeded:\n%s" % resp.headers)
    get_url = resp.headers["operation-location"]

    wait_sec = 25

    time.sleep(wait_sec)
    # The layout API is async therefore the wait statement

    resp = requests.get(url=get_url, headers={"Ocp-Apim-Subscription-Key": apim_key})

    resp_json = json.loads(resp.text)

    status = resp_json["status"]

    if status == "succeeded":
        print("POST Layout Analysis succeeded:\n%s")
        results = resp_json
    else:
        print("GET Layout results failed:\n%s")
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

    response = openai.ChatCompletion.create(
    engine="pacha-gpt4",
    messages=messages,
    functions=functions,
    temperature=0,
    function_call={"name": "get_questions_and_answers"},  
    )
    if isinstance(response, dict):
        resp_text = response["choices"][0]["message"]
        qaobject = json.loads(resp_text["function_call"]["arguments"])
        allqas = qaobject["questions_and_answers"]
        if len(allqas) != 0:
            print("GET questions and answers from document succeeded:\n%s")
        return allqas
    else:
        print("GET questions and answers from document failed:\n%s")
        quit()

def get_embedding(text, model="pacha-embed"):
   text = text.replace("\n", " ")
   response = openai.Embedding.create(input = [text], engine=model)
   if isinstance(response, dict):
       return response['data'][0]['embedding']
   else:
       print(f"GET embedding instance \n {text} \n failed:\n%s")
       quit()

def get_qa_with_embeddings_from(qas):
    embedded_qas= []
    for qa in qas:
        q_embed = get_embedding(qa.get("question"))
        new_dict = {**qa, **{'embedding': q_embed}}
        embedded_qas.append(new_dict)
    return embedded_qas

