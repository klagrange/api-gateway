import os
import redis
import time
from utils import get_custom_exception, TOO_MANY_REQUESTS, PAYMENT_REQUIRED, NOT_AUTHORIZED
import uuid

RATE_PER_SECOND_KEY = "rate-limit:{0}:{1}"
API_KEY_QUOTA = "quota:{0}"
USAGE_PLAN_API_KEY = "usage-plan:{0}:{1}"

def get_redis_client():
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        db=int(os.getenv("REDIS_DB")),
        password=os.getenv('REDIS_PASSWORD')
    )
    assert redis_client.ping()  # check if connection is successful
    return redis_client

def rate_per_second(redis_client, api_key, throttling_rate):
    key = RATE_PER_SECOND_KEY.format(api_key, int(time.time()))
    current_rate = int(redis_client.incr(key))

    print("current_rate = {0}".format(throttling_rate))
    if current_rate > throttling_rate:
        raise get_custom_exception(TOO_MANY_REQUESTS)

    # set TTL to 1 sec
    if redis_client.ttl(key) == -1:  # timeout is not set
        redis_client.expire(key, 1)  # expire in 1 second

def quota_per_seconds(redis_client, api_key, max_calls, period_in_seconds):
    key = API_KEY_QUOTA.format(api_key)
    quota_count = int(redis_client.incr(key))

    print("{0} > {1}".format(quota_count, max_calls))
    if quota_count > max_calls:
        raise get_custom_exception(PAYMENT_REQUIRED)

    # set TTL to `period_in_seconds` sec
    if redis_client.ttl(key) == -1:  # timeout is not set
        redis_client.expire(key, period_in_seconds)  # expire in 1 second

def add_api_key(redis_client, usage_plan):
    key = USAGE_PLAN_API_KEY.format(usage_plan, uuid.uuid4())
    redis_client.incr(key)

def get_usage_plan(redis_client, usage_plans, api_key):
    for usage_plan in usage_plans:
        key = USAGE_PLAN_API_KEY.format(usage_plan, api_key)
        res = redis_client.get(key)
        if res is None:
            continue
        else:
            return usage_plan
    raise get_custom_exception(NOT_AUTHORIZED, "Invalid Api Key {0}".format(api_key))

def xxx():
    REDIS_CLIENT = get_redis_client()
    success = 0
    fail = 0
    for i in range(2000):
        try:
            rate_per_second(REDIS_CLIENT, "mysuperkeykey", 100)  # example: 100 requests per second
            success += 1
        except Exception:
            fail += 1
        time.sleep(5/1000)  # sleep every 5 milliseconds
    print(f"Success count = {success}")
    print(f"Fail count = {fail}")


if __name__ == "__main__":
    REDIS_CLIENT = get_redis_client()
    add_api_key(REDIS_CLIENT, "free")
    # usages = ["freex", "basic"]
    # plan = get_usage_plan(REDIS_CLIENT, usages, "f9644abe-b44a-4b47-8a9e-91efcbc1ce25")
    # print(plan)
# def get_epoch():
#     return calendar.timegm(time.gmtime())