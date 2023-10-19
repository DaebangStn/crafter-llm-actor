import json
import requests
API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer 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"}
def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

if __name__=="__main__":
    resp = query("Can you please let us know more details about your ")
    print(resp)