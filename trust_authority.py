#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 noet number nowrap
"""
    trust authority instance
"""
import asyncio
import logging
from constants import *
#from shared_funcs import dec, enc

class TrustAuthority:
	"""
		really, that is just a fancy way to say "there is a function that will make a pseudo-secret 'hash' of some sort when given publicly known data"

		it is suggested to use regular cryptography with keys and certificates or another trust and validation mechanism to authenticate the parties ; 
		however there are a large variety of methods available and we will not discuss them here.

		TrustAuthority objects have a hash() method, called three times, in order:
		- once by the ballot process when it is instantiated and it build the voters list
		- a second time when generating the balot "papers" (by the process generating these, either by print or through a web service or equivalent)
		- a third time by each voter upon ballot/vote submission

		this ensures a high level of anonymity and high security
	"""
	def __init__( self, name, hash, desc = None ):
		self.name = name
		if desc: self.desc = desc

		if callable(hash):
			self.hashfunc = hash
		elif type(hash) is dict:
			self.hashfunc = hash.get
		else:
			raise Exception("`hash` value invalid")

	async def run( self, host, port ):
		server = await asyncio.start_server(self.trustee_callback, host, port)
		address = ', '.join(str(sock.getsockname()) for sock in server.sockets)
		print(f"{self.name}: listening on {address}")
		logging.info(f"{self.name}: listening on {address}")
		async with server:
			await server.serve_forever()


	async def trustee_callback(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
		""" Callback function for handling incoming server functions.
	
		:param reader: Reader stream
		:param writer: Writer stream
		"""
		request = await reader.read(MAX_MESSAGE_LEN)
	
		# TODO, show client information in debug log :
		# 15:41 < petaflot> hello! I was wondering.. if I have sth like
		# `server = await asyncio.start_server(callback, host, port)` ; how can
		# I - from within callback() - have the details of the client (ie. IP
		# address, port..)
		# 15:46 < SnoopJ> petaflot, I don't think
		# start_server() passes information like that to the client, but maybe
		# you want to write a `Server` class that contains the host/port and
		# which implements the callback as a method instance, which would give
		# you access to the host information at least.

		print(f"received: {request}")
		logging.debug(f"received: {request}")

		return_message = self.hashfunc( request )
	
		# Send response
		if return_message is not None:
			#print(f"Send: {return_message}")
			logging.debug(f"Send: {return_message}")
			writer.write(return_message)
		else:
			#print(f"Nothing to send")
			logging.debug(f"Nothing to send")

	
		await writer.drain()

		# Shut down Stream
		writer.close()
		await writer.wait_closed()


if __name__ == '__main__':
	from sys import argv
	import importlib
	try:
		trustee_id = int(argv[1])
	except IndexError:
		print(f"usage: {argv[0]} <trustee_id>")
		raise SystemExit

	conf = importlib.import_module(f"sample_configs.trustee_{trustee_id}")

	TA = TrustAuthority( conf.conf.pop('name'), conf.hash, conf.conf.pop('desc',None) )
	asyncio.run( TA.run( *conf.conf.pop('serve') ) )
