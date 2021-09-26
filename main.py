#!/usr/bin/python
import requests
import sys
from requests.auth import HTTPBasicAuth
import json
import config

def get_reference_id(repo_id):
    """This function takes the repository id and 
    returns the reference id of the master branch.
    """
    ref_url = "https://dev-api.metabob.com/repository/" + repo_id + "?include=refs"
    response = requests.get(ref_url)
    response_json_obj = response.json()

    for i in response_json_obj["refs"]:
        if i["name"] == "master":
            return i["id"]

repo_id = sys.argv[1]

ref_id = get_reference_id(repo_id)
url = "https://dev-api.metabob.com/analysis/" + str(ref_id) + "/problems/"

response = requests.get(url)
json_obj = response.json()

#Add your atlassian workspace url here
jira_url = "https://kushalgopal.atlassian.net//rest/api/2/issue"

#Basic Authorization for your Jira Software - email, token
#Token can be found here - https://id.atlassian.com/manage/api-tokens.
#Replace config.email and config.token with your email and token respectively
auth = HTTPBasicAuth(config.email, config.jira_token)

headers = {
   "Accept": "application/json",
   "Content-Type": "application/json"
}

for i in json_obj["problems"]:
    description = i["category"]["description"]
    explanation = i["explanation"]
    line_no = i["lineno"]
    end_line_no = i["end_lineno"]
    path = i["path"]
    name = i["category"]["name"]

    payload = json.dumps(
        {
            "fields": {
                "project":
                {
                    "key": "TP"
                },
                "summary": description,
                "description": f"Name = {name}\n \
                    Path = {path}\n \
                    Line Number = {line_no}\n \
                    End Line Number = {end_line_no}\n \
                    Explanation = {explanation}",
                "issuetype": {
                    "name": "Bug"
                }
            }
        }
    )

    response = requests.request(
        "POST",
        jira_url,
        data=payload,
        headers=headers,
        auth=auth
    )

    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
