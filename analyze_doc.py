import requests
import time
import json
import openai
import os

def get_text_from(document):
    # This is a call to the document intelligence endpoint

    endpoint = os.environ["AzureDocumentIntelEndpoint"]
    apim_key = os.environ["AzureDocumentIntelKey"]
    post_url = endpoint + "/formrecognizer/v2.1/layout/analyze"
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
    openai.api_base = "https://pacha.openai.azure.com/"
    openai.api_version = "2023-07-01-preview"
    openai.api_key = "6999ef57bf0d473690c756f5cdacdbcd"

    messages= [{"role": "user", "content": f"Get questions and answers from {text}"}]
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
    function_call={"name": "get_questions_and_answers"},  
)
    print(response['choices'][0]['message'])


