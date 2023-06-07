# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap

conf = {
	'name': 'Trust Authority One (md5)',
	'desc': "This trust authority is an md5 dummy ; a good example to implement proprietary hash methods",
	'serve': ('127.0.0.1', 10001),
}

from hashlib import md5
hash = md5
