from flask import Response

def get_path(base, path):
    redirect_url = "{0}{1}".format(base, path)
    return redirect_url

def get_response(resp):
    excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
    headers = [(name, value) for (name, value) in  resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response

def create_custom_exception(ttype, message, statusCode=None):
    exception_body = {
        "type": ttype,
        "message": message
    }
    if statusCode:
        exception_body["statusCode"] = statusCode
    return Exception(exception_body)

NOT_AUTHORIZED = "NOT_AUTHORIZED"
TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
def get_custom_exception(ttype, custom_message=None):
    if ttype == NOT_AUTHORIZED:
        return Exception({
            "type": ttype,
            "message": "Not Authorized" if not custom_message else custom_message,
            "statusCode": 403
        })
    if ttype == TOO_MANY_REQUESTS:
        return Exception({
            "type": ttype,
            "message": "Too Many Requests",
            "statusCode": 429
        })
    if ttype == PAYMENT_REQUIRED:
        return Exception({
            "type": ttype,
            "message": "Payment Required",
            "statusCode": 402
        })
    return Exception()
