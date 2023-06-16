#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap
from quart import Quart, render_template, websocket
import json
import base64
from datetime import datetime
#from threading import Thread
import devel
from shared_funcs import enc, dec, int_as_bytes
import asyncio
from constants import LISTEN, ENCODING, DATETIME_FMT

app = Quart(__name__)

@app.route("/")
async def index():
	return await render_template("index.html", 
			BMM = app.BMM, 
			dec = dec,
			enc = enc,
			len = len,
			round = round,
		)

@app.route("/config.json")
async def json_api():
	# TODO write a function that does this a bit more automatically and re-usable for other projects
	#print(app.BMM.trustees)
	return json.dumps( {dec(base64.b64encode(key)): dec(base64.b64encode(val)) for key, val in (
		( b"authority", app.BMM.authority ),
		( b"question", app.BMM.question ),
		#( b"poll_opens", enc(datetime.strptime(app.BMM.poll_opens, DATETIME_FMT)) ),    # is there a better way? this seems barely acceptable, TODO i'ts broken
		#( b"poll_closes", enc(datetime.strptime(app.BMM.poll_closes, DATETIME_FMT)) ),    # is there a better way? this seems barely acceptable, TODO it's broken
		( b"poll_port", int_as_bytes(app.BMM.ballot_server_port) ),
		( b"anticipated_results", enc(str(app.BMM.anticipated_results)) ),
	)})

@app.route("/trustees.json")
async def trustees_api():
	#print(app.BMM.trustees)
	return json.dumps( {dec(base64.b64encode(key)): dec(base64.b64encode(val)) for key, val in (
		# using a string like that is not exactly great practice... fortunately we only expect ASCII chars here (host:port)
		( b"trustees", enc('\n'.join([':'.join([dec(t[0]),dec(t[1])]) for t in app.BMM.trustees])) ),
	)})

@app.websocket("/ws")
async def ws():
	while True:
		await websocket.send("hello")
		await websocket.send_json({"hello": "world"})

@app.before_serving
async def startup():
	loop = asyncio.get_event_loop()
	from ballotter_core import BallotMiddleMan
	app.BMM = await BallotMiddleMan.init( loop, authority, question, trustees, voters, host, ENCODING )

@app.after_serving
async def shutdown():
	#app.smtp_server.close()
	# TODO close other listening threads
	pass

async def http_run( loop, authority, host, port ):
	#t = Thread(target=app.run, args={ 'host':host, 'port':port })
	#t.run()
	t = loop.create_task( await app.run( host=host, port=port ))
	t.run()
	print(f"HTTP Listening on {host}:{port} for {authority}")

#async def main( loop, authority, question, trustees, voters, host ):
#	from ballot_server import BallotMiddleMan
#	BMM = await BallotMiddleMan.init( loop, authority, question, trustees, voters, host, ENCODING )
#	await BMM.open_poll()

if __name__ == '__main__':
	from sys import argv
	try:
		# whut? why doesn't this work? TypeError: a bytes-like object is required, not 'str'
		#voters = [v.rstrip('b\n') for v in open(argv[1],'rb').readlines()]
		# this double-nested generator works but is not as pretty and probably not optimal
		voters = [ v.rstrip(b'\n') for v in [v for v in open(argv[1],'rb').readlines()] ]
		trustees = [ l.rstrip(b'\n') for l in open(argv[2],'rb').readlines() ]
	except FileNotFoundError:
		print(f"usage: {argv[0]} <voters.list> <trustees.list>")
		raise SystemExit
	except IndexError:
		print(f"usage: {argv[0]} <voters.list> <trustees.list>")
		raise SystemExit
	
	# TODO acept command-line arguments for PORT_* and LISTEN

	authority = enc(input(f"Authority ID/Name [{dec(devel.AUTHORITY_NAME)}]: "))
	authority = devel.AUTHORITY_NAME if authority == b'' else authority
	question = enc(input(f"Question [{dec(devel.QUESTION)}]: "))
	question = devel.QUESTION if question == b'' else question
	host = input(f"Listen on [{LISTEN}]: ")
	host = LISTEN if host == '' else host

	from hypercorn.asyncio import serve
	from hypercorn.config import Config
	loop = asyncio.get_event_loop()
	loop.run_until_complete(serve(app, Config()))
	# or even
	#await serve(app, config)
