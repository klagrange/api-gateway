from functools import wraps
import traceback
from flask import make_response, jsonify

def exception_capturer():
    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(path):
            try:
                print("=====> exception_capturer {0}".format(path))
                response = handler(path)
            except Exception as exception:
                # custom exceptions that bubbled up
                custom_args = exception.args
                if len(custom_args) == 1 and isinstance(custom_args[0], dict):
                    args = custom_args[0]
                    status_code = args["statusCode"] if "statusCode" in args.keys() else 400
                    return make_response(jsonify({
                        "type": args["type"],
                        "error_snippet": args["message"],
                    }), status_code)

                # unhandled exceptions
                trace = traceback.format_exc()
                return make_response(jsonify({
                    "type": "SERVER_ERROR",
                    "error_snippet": str(exception),
                    "traceback": trace,
                }), 500)
            return response
        return wrapper
    return wrapper_wrapper

def verify_rule(fn):
    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(path):
            # print("=====> verify_rule {0}".format(path))
            # print(fn())
            response = handler(path)
            return response
        return wrapper
    return wrapper_wrapper

def modify_path(fn):
    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(path):
            # print("=====> modify_path {0}".format(path))
            new_path = fn(path)
            response = handler(new_path)
            return response
        return wrapper
    return wrapper_wrapper
