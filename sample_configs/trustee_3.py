# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap

conf = {
	'name': 'Trust Authority Three (dic)',
	'desc': "This trust authority is dictionnary-based ; ideally it should read hashes from yet another file or database",
	'serve': ('127.0.0.1', 10002),
}

hash = {
	b'charles': b'Paranoid, has own auth service',
	b'alice': b"she's charle's friend, too",
}

