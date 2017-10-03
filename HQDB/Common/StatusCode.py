def __getDetail(code):
    status_code = code
    description = ''
    if status_code == 400:
        description = 'Bad Request'
    elif status_code == 401:
        description = 'Unauthorized'
    elif status_code == 402:
        description = 'Payment Required'
    elif status_code == 403:
        description = 'Forbidden'
    elif status_code == 404:
        description = 'Not Found'
    elif status_code == 405:
        description = 'Method Not Allowed'
    elif status_code == 406:
        description = 'Not Acceptable'
    elif status_code == 407:
        description = 'Proxy Authentication Required'
    elif status_code == 408:
        description = 'Request Timeout'
    elif status_code == 409:
        description = 'Conflict'
    elif status_code == 410:
        description = 'Gone'
    elif status_code == 411:
        description = 'Length Required'
    elif status_code == 412:
        description = 'Precondition Failed'
    elif status_code == 413:
        description = 'Request Entity Too Large'
    elif status_code == 414:
        description = 'Request-URI Too Long'
    elif status_code == 415:
        description = 'Unsupported Media Type'
    elif status_code == 416:
        description = 'Requested Range Not Satisfiable'
    elif status_code == 417:
        description = 'Expectation Failed'
    elif status_code == 500:
        description = 'Internal Server Error'
    elif status_code == 501:
        description = 'Not Implemented'
    elif status_code == 502:
        description = 'Bad Gateway'
    elif status_code == 503:
        description = 'Service Unavailable'
    elif status_code == 504:
        description = 'Gateway Timeout'
    elif status_code == 505:
        description = 'HTTP Version Not Supported'
    else:
        description = 'Status Code not define'
    if status_code >= 400 and status_code <= 417:
        description = 'Client Error - ' + description
    if status_code >= 500 and status_code <= 505:
        description = 'Server Error - ' + description
    return description

