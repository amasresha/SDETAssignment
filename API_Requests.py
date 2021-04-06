import requests
import json
import datetime
from SDETAssignment.SDETAssignment import Helpers as hp

base_uri = "http://192.168.1.228:8088"


# POST requests

def get_post_response(file_name):
    # read input
    url = base_uri + "/hash"
    input_data = open(hp.get_root_path() + '\\TestData\\' + file_name, 'r')
    request_body = json.dumps(json.load(input_data))
    headers = {'Accept': 'application/json'}
    # make a post request
    print("sending post request{}")
    print(datetime.datetime.now())
    response = requests.post(url, headers=headers, data=request_body)
    stat.post_status = response.status_code
    return response


def get_encoded_password(job_id):
    url = base_uri + "/hash/" + job_id
    print("sending get request{}")
    print(datetime.datetime.now())
    return requests.get(url)


def get_stats(sub_url=""):
    # default: sub_url = "/stats"
    if sub_url == "":
        sub_url = "/stats"
    url = base_uri + sub_url
    return requests.get(url)


def shutdown():
    url = base_uri + "/hash"
    data = 'shutdown'
    print('shutting down')
    print(datetime.datetime.now())
    shut_down= requests.post(url, data=data)
    stat.shutdown_status=shut_down.status_code
    return shut_down


class stat:
    post_status =""
    shutdown_status=""


