#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap
from quart import Quart, render_template, websocket
#from threading import Thread

ballot_http = Quart(__name__)

@ballot_http.route("/")
async def hello():
	return await render_template("index.html")

@ballot_http.route("/api")
async def json():
	return {
		'authority': devel.AUTHORITY_NAME,
		'poll_open': devel.POLL_OPEN,
		'poll_port': devel.PORT_POLLING,
		'poll_early_results': devel.POLL_EARLY_RESULTS,
		'ballot_competitors': devel.BALLOT_COMPETITORS,
	}

@ballot_http.websocket("/ws")
async def ws():
	while True:
		await websocket.send("hello")
		await websocket.send_json({"hello": "world"})

async def http_run( loop, authority, host, port ):
	#t = Thread(target=ballot_http.run, args={ 'host':host, 'port':port })
	#t.run()
	t = loop.create_task( await ballot_http.run( host=host, port=port ))
	t.run()
	print(f"HTTP Listening on {host}:{port} for {authority}")
