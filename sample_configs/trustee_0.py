# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap

conf = {
	'name': 'Trust Authority Zero (echo)',
	'desc': "This trust authority is an echo dummy",
	'serve': ('127.0.0.1', 10000),	# (host, port) ; host must be ASCII or Base64-encoded
}

def hash( data ):
    return data
