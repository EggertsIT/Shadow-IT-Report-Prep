import requests
import json
import os
import time
import csv
from dotenv import load_dotenv
import pandas as pd

load_dotenv() 

api_key = os.getenv("API_KEY_PROD")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

base_url = "https://zsapi.zscloud.net/api/v1/"
#base_url = "https://zsapi.zscaler.net/api/v1/"
#base_url = "https://zsapi.zscalerbeta.net/api/v1/"

auth_url = base_url+"authenticatedSession"
report_url = base_url+"shadowIT/applications/export"
id_url = base_url+"cloudApplications/lite"

def obfuscate_api_key(seed: list):
    now = int(time.time() * 1000)
    n = str(now)[-6:]
    r = str(int(n) >> 1).zfill(6)
    key = "".join(seed[int(str(n)[i])] for i in range(len(str(n))))
    for j in range(len(r)):
        key += seed[int(r[j]) + 2]

    return {"timestamp": now, "key": key}

api_obf = obfuscate_api_key(api_key)

payload = json.dumps({
            "apiKey": api_obf["key"],
            "username": username,
            "password": password,
            "timestamp": api_obf["timestamp"],
        })

auth_headers = {
  'Content-Type': 'application/json',
}

response = requests.request("POST", auth_url, headers=auth_headers, data=payload, verify=False)
cookies = response.cookies.get_dict()
JSESSIONID=cookies['JSESSIONID']

headers = {
  'Content-Type': 'application/json',
  'Cookie': f'JSESSIONID={JSESSIONID}'
}


all_app_ids = []

page = 0
while True:
    app_ids_url = f"{id_url}?limit=1000&pageNumber={page}"
    app_ids_response = requests.get(app_ids_url, headers=headers)
    app_ids = json.loads(app_ids_response.text)
    print(app_ids)
    time.sleep(0.5)
    if not app_ids:
        break
    all_app_ids.append(app_ids)
    page += 1

all_ids = pd.concat([pd.DataFrame(app_ids) for app_ids in all_app_ids], ignore_index=True)
all_ids.to_csv('app_id.csv', index=False)



payload = json.dumps({
  "duration": "LAST_7_DAYS"
})

cloud_apps_response = requests.request("POST", report_url, headers=headers, data=payload, verify=False)
api_response_text = cloud_apps_response.text


api_response_text = api_response_text.replace("Potential Integrations,Tags,,Certifications", "Potential Integrations,Tags,Certifications")

print(api_response_text)
csv_reader = csv.reader(api_response_text.splitlines(), delimiter=',', quotechar='"')

for _ in range(5):
    next(csv_reader)

column_names = next(csv_reader)


df = pd.DataFrame(csv_reader, columns=column_names)

df.to_csv('shadow_it_report.csv', index=False)
