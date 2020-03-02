USAGE_PLANS = {
    "free": {
        "throttling_rate": 1,
        "quota": {
            "max_calls": 5,
            "period_in_seconds": 20
        }
    }
}

def get_usage_plan_info(usage_plans, usage_plan):
    usage_plan_details = usage_plans[usage_plan]
    quota_info = usage_plan_details["quota"]
    max_calls = quota_info["max_calls"]
    period_in_seconds = quota_info["period_in_seconds"]
    throttling_rate = usage_plan_details["throttling_rate"]

    return max_calls, period_in_seconds, throttling_rate