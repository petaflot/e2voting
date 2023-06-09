# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap

conf = {
	'name': 'Trust Authority One (md5)',
	'desc': "This trust authority is an md5 dummy ; a good example to implement proprietary hash methods",
	'serve': ('127.0.0.1', 10001),
}

from hashlib import md5
from shared_funcs import enc
def hash( data ):
	#return md5(data).digest()
	return enc(md5(data).hexdigest())
