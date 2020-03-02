from flask import Flask, request, redirect, Response, make_response, jsonify
import requests
import re
import os
from utils import get_path, get_response, create_custom_exception, get_custom_exception, NOT_AUTHORIZED
from decorators import exception_capturer, verify_rule, modify_path
from rate_limiter import get_redis_client, rate_per_second, quota_per_seconds, get_usage_plan
from usage_plans import USAGE_PLANS, get_usage_plan_info

REDIS_CLIENT = get_redis_client()

APP = Flask(__name__)
ALB = os.environ["ALB"]

@APP.route("/")
def index():
    return "healthy"

def ret_a():
    # raise create_custom_exception("A", "ALREADY HAVE AN API KEY FOR THIS USAGE PLAN. LIMITED TO ONE PER EMAIL.")
    return "ret-ret-ret-a"

def ret_b():
    # raise create_custom_exception("B", "ALREADY HAVE AN API KEY FOR THIS USAGE PLAN. LIMITED TO ONE PER EMAIL.")
    return "ret-ret-ret-b"

def new_path(path):
    return "/apple/basd"


def authorization_header_exists(headers):
    api_key = "X-Api-Key"
    if api_key not in dict(headers).keys():
        raise get_custom_exception(NOT_AUTHORIZED)
    return dict(headers)[api_key]

@APP.route("/<path:path>", methods=["GET", "POST", "DELETE"])
@exception_capturer()
def proxy(path):
    # ensure authorization header is present
    api_key = authorization_header_exists(request.headers)

    # retrieve usage plan from api key
    usage_plan = get_usage_plan(REDIS_CLIENT, USAGE_PLANS.keys(), api_key)

    # apply usage plan quota and throttling limits
    max_calls, period_in_seconds, throttling_rate = get_usage_plan_info(USAGE_PLANS, usage_plan)
    quota_per_seconds(REDIS_CLIENT, api_key, max_calls, period_in_seconds)
    rate_per_second(REDIS_CLIENT, api_key, throttling_rate)

    if request.method == "GET":
        redirect_url = get_path(ALB, path)
        resp = requests.get(redirect_url)
        response = get_response(resp)
        return response
    elif request.method == "POST":
        redirect_url = get_path(ALB, path)
        resp = requests.post(redirect_url, json=request.get_json())
        response = get_response(resp)
        return response
    elif request.method == "DELETE":
        redirect_url = get_path(ALB, path)
        resp = requests.delete(redirect_url).content
        response = get_response(resp)
        return response

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




# rate = 5.0; // unit: messages
# per  = 8.0; // unit: seconds
# allowance = rate; // unit: messages
# last_check = now(); // floating-point, e.g. usec accuracy. Unit: seconds

# when (message_received):
#   current = now();
#   time_passed = current - last_check;
#   last_check = current;
#   allowance += time_passed * (rate / per);
#   if (allowance > rate):
#     allowance = rate; // throttle
#   if (allowance < 1.0):
#     discard_message();
#   else:
#     forward_message();
#     allowance -= 1.0;