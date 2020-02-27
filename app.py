from flask import Flask, request, redirect, Response
import requests
import re
import os

APP = Flask(__name__)

ALB = os.environ["ALB"]

def get_path(base, path):
    redirect_url = "{0}{1}".format(base, path)
    return redirect_url

def get_response(resp):
    excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
    headers = [(name, value) for (name, value) in  resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response

@APP.route("/")
def index():
    return "Flask is running!"

@APP.route("/<path:path>", methods=["GET", "POST", "DELETE"])
def proxy(path):
    if request.method == "GET":
        redirect_url = get_path(ALB, path)
        resp = requests.get(redirect_url)
        response = get_response(resp)
        return response
        # return "GET"
    # elif request.method == "POST":
    #     resp = requests.post(f"{SITE_NAME}{path}",json=request.get_json())
    #     excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
    #     headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    #     response = Response(resp.content, resp.status_code, headers)
    #     return response
    # elif request.method == "DELETE":
    #     resp = requests.delete(f"{SITE_NAME}{path}").content
    #     response = Response(resp.content, resp.status_code, headers)
    #     return response

if __name__ == '__main__':
    APP.run()
    # PATH_REGEX = re.compile("^(?P<version>\d+.\d+.\d+)/(?P<service>.+)/?(?P<rest>.*)$")
    # text = "1.0.0/portfolio"

    # x = re.match(PATH_REGEX, text)
    # if x:
    #     search_results = re.search(PATH_REGEX, text)
    #     version = search_results.group("version")
    #     service = search_results.group("service")
    #     rest = search_results.group("rest")
    #     print(version)
    #     print(service)
    #     print(rest)