import requests
import time
import json

def call_document_intelligence(apim_key, post_url, document):
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