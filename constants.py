MAX_MESSAGE_LEN = 32
# Whether we're in debug mode (True) or not (False)
DEBUG_ENABLED = False
ENCODING = 'utf-8'

LISTEN = '127.0.0.1'
PORT_INVITES = 9998
PORT_POLLING = 9999
PORT_HTTP = 8000    # TODO hypercorn/quart does not use this value when it should!

# where is this poll happening
TIMEZONE = 'Europe/Zurich'

INVITE_ERROR_INT = 1

DATETIME_FMT = '%Y-%m-%dT%H:%M:%S.%f%z'
